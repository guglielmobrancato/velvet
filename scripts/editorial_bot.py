import json
import urllib.request
import xml.etree.ElementTree as ET
import ssl
import os
import re
from datetime import datetime
import google.generativeai as genai

# --- CONFIGURAZIONE ---
API_KEY = os.environ.get("GEMINI_API_KEY")
print("------------------------------------------------")
if API_KEY:
    print("✅ DEBUG: Chiave API trovata.")
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash') 
else:
    print("❌ DEBUG: NESSUNA CHIAVE TROVATA.")
print("------------------------------------------------")

SOURCES = {
    "CINEMA": ["https://variety.com/feed/", "https://www.hollywoodreporter.com/c/movies/feed/"],
    "MUSIC": ["https://pitchfork.com/rss/reviews/albums/", "https://www.rollingstone.com/music/music-news/feed/"]
}

def load_existing_data():
    try:
        with open("data.js", "r", encoding="utf-8") as f:
            content = f.read().replace("const mshData = ", "").replace(";", "")
            data = json.loads(content)
            if "cinema" not in data: data["cinema"] = []
            if "music" not in data: data["music"] = []
            return data
    except:
        return {"cinema": [], "music": []}

def extract_json(text):
    try:
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if match: return json.loads(match.group())
        clean = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except: return None

def generate_review(category, news_items):
    if not API_KEY or not news_items: return None
    titles_context = "\n".join([f"- {item['title']}" for item in news_items[:5]])
    role = "Critico Marziano" if category == "CINEMA" else "DJ Spaziale"
    prompt = f"""
    Sei {role} per "VELVET". News Terra: {titles_context}.
    Scegli 1 notizia. Scrivi mini-recensione (max 30 parole).
    OUTPUT JSON: {{ "title": "Titolo ITA", "author": "Nome Alieno", "excerpt": "Testo...", "streaming_search_query": "Titolo esatto" }}
    """
    try:
        response = model.generate_content(prompt)
        return extract_json(response.text)
    except: return None

print("--- INIZIO SCANSIONE ---")
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0'}
news_basket = {"CINEMA": [], "MUSIC": []}

for cat, urls in SOURCES.items():
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as response:
                tree = ET.fromstring(response.read())
                items = tree.findall(".//item")
                if not items: items = tree.findall("{http://purl.org/rss/1.0/}item")
                for item in items[:3]:
                    t = item.find("title").text
                    news_basket[cat].append({"title": t})
        except: pass

current_data = load_existing_data()
today_str = datetime.now().strftime("%d.%m.%Y")

print("🧠 Elaborazione Cinema...")
c_rev = generate_review("CINEMA", news_basket["CINEMA"])
if c_rev: 
    c_rev["date"] = today_str
    current_data["cinema"].insert(0, c_rev)
    current_data["cinema"] = current_data["cinema"][:10]

print("🧠 Elaborazione Musica...")
m_rev = generate_review("MUSIC", news_basket["MUSIC"])
if m_rev: 
    m_rev["date"] = today_str
    current_data["music"].insert(0, m_rev)
    current_data["music"] = current_data["music"][:10]

json_output = json.dumps(current_data, indent=4)
with open("data.js", "w", encoding="utf-8") as f:
    f.write(f"const mshData = {json_output};")

print("--- COMPLETATO ---")
