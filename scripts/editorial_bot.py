import json
import urllib.request
import xml.etree.ElementTree as ET
import ssl
import os
import re
import random
from datetime import datetime
import google.generativeai as genai

# --- CONFIGURAZIONE ---
API_KEY = os.environ.get("GEMINI_API_KEY")
print("------------------------------------------------")
if API_KEY:
    print("✅ DEBUG: Chiave API trovata.")
    genai.configure(api_key=API_KEY)
    # MODELLO STABILE
    model = genai.GenerativeModel('gemini-2.0-flash') 
else:
    print("❌ DEBUG: NESSUNA CHIAVE TROVATA.")
print("------------------------------------------------")

# --- FONTI RSS (RECENSIONI VERE) ---
SOURCES = {
    "CINEMA": ["https://www.rogerebert.com/feed/reviews", "https://www.theguardian.com/film/rss"],
    "MUSIC": ["https://pitchfork.com/rss/reviews/albums/", "https://www.nme.com/reviews/feed"]
}

# --- UTILITÀ ---
def load_existing_data():
    try:
        with open("data.js", "r", encoding="utf-8") as f:
            content = f.read().replace("const mshData = ", "").replace(";", "")
            return json.loads(content)
    except:
        return {"cinema": [], "music": []}

def extract_json(text):
    try:
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if match: return json.loads(match.group())
        clean = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except: return None

# --- AI ---
def generate_review(category, news_items):
    if not API_KEY: return None
    titles_context = "\n".join([f"- {item['title']}" for item in news_items[:8]]) if news_items else ""
    
    if category == "CINEMA":
        role = "Critico Cinematografico d'Essai (Marte 2050)"
        task = "Scegli un film RECENTE. Scrivi una recensione critica, tagliente e sofisticata."
    else:
        role = "Critico Musicale Underground (Marte 2050)"
        task = "Scegli un album RECENTE. Scrivi una recensione tecnica, emotiva e profonda."

    prompt = f"""
    Sei {role} per "VELVET". Spunti: {titles_context}
    {task}
    REGOLE:
    1. Scrivi 100-120 parole.
    2. Niente immagini. Solo testo puro.
    3. Inserisci un VOTO (es. 8.5/10).
    OUTPUT JSON:
    {{
        "title": "Titolo Recensione ITA",
        "author": "Nome Critico",
        "excerpt": "Testo recensione...",
        "vote": "8/10",
        "streaming_search_query": "Titolo film/album esatto"
    }}
    """
    try:
        response = model.generate_content(prompt)
        return extract_json(response.text)
    except Exception as e:
        print(f"Errore AI: {e}")
        return None

# --- PULIZIA DATABASE ---
def clean_data(data_list):
    # Rimuove placeholder e duplicati
    cleaned = []
    seen = set()
    for item in data_list:
        t = item.get("title", "")
        # SE IL TITOLO È 'SYSTEM ONLINE' LO BUTTA VIA
        if t and t != "SYSTEM ONLINE" and t not in seen:
            cleaned.append(item)
            seen.add(t)
    return cleaned[:10] # Max 10 items

# --- ESECUZIONE ---
print("--- INIZIO SCANSIONE ---")
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}
news_basket = {"CINEMA": [], "MUSIC": []}

for cat, urls in SOURCES.items():
    print(f"📡 Scansione {cat}...")
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as response:
                tree = ET.fromstring(response.read())
                items = tree.findall(".//item")
                if not items: items = tree.findall("{http://purl.org/rss/1.0/}item")
                for item in items[:5]:
                    t = item.find("title").text
                    news_basket[cat].append({"title": t})
        except: pass

current_data = load_existing_data()
today_str = datetime.now().strftime("%d.%m.%Y")

print("🧠 Elaborazione Cinema...")
c_rev = generate_review("CINEMA", news_basket["CINEMA"])
if c_rev and c_rev.get("title"): 
    c_rev["date"] = today_str
    current_data["cinema"].insert(0, c_rev)

# APPLICA PULIZIA
current_data["cinema"] = clean_data(current_data["cinema"])

print("🧠 Elaborazione Musica...")
m_rev = generate_review("MUSIC", news_basket["MUSIC"])
if m_rev and m_rev.get("title"): 
    m_rev["date"] = today_str
    current_data["music"].insert(0, m_rev)

# APPLICA PULIZIA
current_data["music"] = clean_data(current_data["music"])

json_output = json.dumps(current_data, indent=4)
with open("data.js", "w", encoding="utf-8") as f:
    f.write(f"const mshData = {json_output};")

print("--- UPDATE COMPLETATO ---")
