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
    print("✅ DEBUG: Chiave API trovata. Inizializzazione Velvet Terminal...")
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash') 
else:
    print("❌ DEBUG: NESSUNA CHIAVE TROVATA. Sistema offline.")
print("------------------------------------------------")

# --- NUOVE FONTI (SOLO RECENSIONI DI COSE USCITE) ---
SOURCES = {
    # Roger Ebert & Guardian Film Reviews (Solo film usciti)
    "CINEMA": [
        "https://www.rogerebert.com/feed/reviews", 
        "https://www.theguardian.com/film/rss"
    ],
    # Pitchfork & NME Reviews (Solo album usciti)
    "MUSIC": [
        "https://pitchfork.com/rss/reviews/albums/", 
        "https://www.nme.com/reviews/feed"
    ]
}

# --- UTILITÀ ---
def load_existing_data():
    try:
        with open("data.js", "r", encoding="utf-8") as f:
            content = f.read().replace("const mshData = ", "").replace(";", "")
            data = json.loads(content)
            if "cinema" not in data: data["cinema"] = []
            if "music" not in data: data["music"] = []
            return data
    except Exception as e:
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
    
    # Se abbiamo news dal feed, le usiamo come spunto
    titles_context = ""
    if news_items:
        titles_context = "\n".join([f"- {item['title']}" for item in news_items[:8]])
    
    if category == "CINEMA":
        role = "Critico Cinematografico d'Essai (Marte 2050)"
        task = """
        Scegli DALLA LISTA un film che è APPENA USCITO (Recensione).
        Se la lista contiene solo gossip o film vecchi, IGNORALA e scegli tu un film importante uscito realmente sulla Terra negli ultimi 3-6 mesi (es. un film di Nolan, Villeneuve, Lanthimos, blockbuster o indie acclamato).
        Devi recensire un film che il lettore può guardare OGGI.
        """
    else:
        role = "Critico Musicale Underground (Marte 2050)"
        task = """
        Scegli DALLA LISTA un album APPENA USCITO.
        Se la lista è vuota o irrilevante, scegli tu un album importante uscito negli ultimi 3 mesi (Rock, Elettronica, Rap, Indie).
        Devi recensire musica che il lettore può ascoltare OGGI.
        """

    prompt = f"""
    Sei {role} per la rivista "VELVET".
    
    Spunti dai Feed RSS (se utili): 
    {titles_context}

    COMPITO:
    {task}
    
    REGOLE SCRITTURA:
    1. Scrivi una VERA recensione critica (100-130 parole).
    2. Parla di regia, fotografia, suono (se Cinema) o produzione, mix, vibes (se Musica).
    3. Tono: Competente, leggermente distaccato, spaziale.
    4. Niente riassunti della trama. Solo critica pura.
    5. Inserisci un VOTO in decimi.

    OUTPUT JSON OBBLIGATORIO:
    {{
        "title": "Titolo della Recensione (IN ITALIANO, es: 'IL RITORNO DEL RE')",
        "author": "Nome del Critico (es. Xylar V.)",
        "excerpt": "Il testo completo della recensione...",
        "vote": "Voto (es. 8.5/10)",
        "streaming_search_query": "Titolo esatto film/album per ricerca"
    }}
    """
    try:
        response = model.generate_content(prompt)
        return extract_json(response.text)
    except Exception as e:
        print(f"Errore AI: {e}")
        return None

# --- ESECUZIONE ---
print("--- INIZIO SCANSIONE VELVET (MODE: REVIEWS ONLY) ---")
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}
news_basket = {"CINEMA": [], "MUSIC": []}

# Scarica Feed
for cat, urls in SOURCES.items():
    print(f"📡 Scansione {cat}...")
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as response:
                tree = ET.fromstring(response.read())
                items = tree.findall(".//item")
                if not items: items = tree.findall("{http://purl.org/rss/1.0/}item")
                for item in items[:5]: # Prendiamo più item per dare scelta
                    t = item.find("title").text
                    news_basket[cat].append({"title": t})
        except: pass

current_data = load_existing_data()
today_str = datetime.now().strftime("%d.%m.%Y")

# Genera Cinema
print("🧠 Elaborazione Critica Cinema...")
c_rev = generate_review("CINEMA", news_basket["CINEMA"])
if c_rev and c_rev.get("title"): 
    c_rev["date"] = today_str
    current_data["cinema"].insert(0, c_rev)
    current_data["cinema"] = current_data["cinema"][:10] # Max 10 recensioni
    print(f"✅ Cinema aggiunto: {c_rev['title']}")

# Genera Musica
print("🧠 Elaborazione Critica Musica...")
m_rev = generate_review("MUSIC", news_basket["MUSIC"])
if m_rev and m_rev.get("title"): 
    m_rev["date"] = today_str
    current_data["music"].insert(0, m_rev)
    current_data["music"] = current_data["music"][:10] # Max 10 recensioni
    print(f"✅ Musica aggiunta: {m_rev['title']}")

# SALVATAGGIO
json
