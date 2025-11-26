import os
import random
import datetime
import feedparser
import google.generativeai as genai
from bs4 import BeautifulSoup

# --- CONFIGURAZIONE ---
GENAI_API_KEY = os.environ["GEMINI_API_KEY"]
genai.configure(api_key=GENAI_API_KEY)

# LISTA DI FEED (Se il primo fallisce, prova il secondo)
RSS_SOURCES = {
    'cinema': [
        'https://www.cinemaitaliano.info/rss/notizie.xml',
        'https://movieplayer.it/feed/news/',
        'https://www.cineblog.it/feed'
    ],
    'musica': [
        'https://www.rollingstone.it/feed/',
        'https://www.soundsblog.it/feed',
        'https://www.rockol.it/rss/news/musica-italiana'
    ]
}

# --- PROMPT SYSTEM ---
PROMPTS = {
    'cinema_news': """Sei un critico cinematografico del 1978 di 'Marte Velvet'. 
    Scrivi una news (max 120 parole) basata sui dati forniti.
    TONO: Impegnato, politico ma stiloso. Usa termini come "pellicola", "cinepresa", "il sistema", "tax credit", "la sala".
    FORMAT: HTML semplice (<p>).""",

    'cinema_vintage': """Scegli un FILM ITALIANO CULT (Poliziottesco, Neorealismo, Horror Argento/Bava o Commedia all'italiana) tra il 1960 e il 1989.
    Scrivi una breve recensione "Cult della Settimana" (max 100 parole).
    TONO: Ammirato, nostalgico, citazionista.
    OUTPUT FORMAT:
    TITOLO: [Titolo del film - Regista]
    RECENSIONE: [Tuo testo]""",

    'musica_news': """Sei un DJ radiofonico notturno anni '80. 
    Scrivi una news (max 120 parole) basata sui dati forniti.
    TONO: "Groovy", caldo, usa slang come "vibes", "basso", "ritmo", "sound", "la classifica".
    FOCUS: Se la news è moderna, trattala con curiosità o critica lo stato attuale della musica rispetto al passato.
    FORMAT: HTML semplice (<p>).""",

    'musica_vintage': """Scegli un ALBUM o BRANO (Disco, Funky, Italo-Disco, old school Rap) tra il 1975 e il 1989.
    Scrivi una breve scheda "Vinyl Gold" (max 100 parole).
    TONO: Da audiofilo esperto, parla di bassline e sintetizzatori.
    OUTPUT FORMAT:
    TITOLO: [Titolo Album/Brano - Artista]
    RECENSIONE: [Tuo testo]"""
}

def ask_gemini(prompt, data_context=""):
    """Funzione generica per chiamare Gemini"""
    model = genai.GenerativeModel('gemini-2.0-flash')
    full_prompt = f"{prompt}\n\nDATI:\n{data_context}"
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Errore Gemini: {e}")
        return "Errore nella generazione AI."

def update_marquee(soup, new_text):
    """Aggiunge il titolo al testo scorrevole in alto"""
    marquee = soup.find(id="archive-marquee")
    if marquee:
        current_text = marquee.text
        # Pulisce spazi extra
        current_text = " ".join(current_text.split())
        updated_text = f"{new_text.upper()} +++ {current_text}"
        if len(updated_text) > 2000: 
            updated_text = updated_text[:2000]
        marquee.string = updated_text

def get_valid_feed(topic):
    """Prova i feed in lista finché non ne trova uno funzionante"""
    urls = RSS_SOURCES[topic]
    for url in urls:
        print(f"Tentativo feed: {url}...")
        try:
            # User Agent per non farsi bloccare
            d = feedparser.parse(url, agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            if d.entries and len(d.entries) > 0:
                print("✅ Feed valido trovato!")
                return d.entries[0]
        except Exception as e:
            print(f"Errore lettura feed: {e}")
            continue
    return None

def main():
    topic = random.choice(['cinema', 'musica'])
    # Se vuoi forzare un argomento per testare, scommenta la riga sotto:
    # topic = 'musica' 
    
    print(f"📡 MARTE VELVET ON AIR: Oggi parliamo di {topic.upper()}")
    target_file = f"{topic}.html"
    
    # 1. NEWS REALI (RSS con Fallback)
    news_item = get_valid_feed(topic)
    
    if not news_item:
        print(f"❌ IMPOSSIBILE TROVARE NEWS PER {topic.upper()}. TUTTI I FEED SONO VUOTI O BLOCCATI.")
        # Fallback di emergenza: Generiamo una news vintage inventata se non c'è internet
        news_title = "Segnale Interrotto..."
        news_link = "#"
        news_summary = "Impossibile recuperare dati dal presente."
        news_body = "Oggi le frequenze sono disturbate. Restate sintonizzati per aggiornamenti."
    else:
        print(f"📰 News trovata: {news_item.title}")
        news_title = news_item.title
        news_link = news_item.link
        # Genera Articolo News
        news_body = ask_gemini(PROMPTS[f'{topic}_news'], f"Titolo: {news_item.title}\nSummary: {news_item.get('summary', '')}")

    # 2. VINTAGE FEATURE (Generato da zero)
    print("📼 Generazione contenuto Vintage...")
    vintage_raw = ask_gemini(PROMPTS[f'{topic}_vintage'])
    
    v_title = "Archivio Segreto"
    v_body = vintage_raw
    if "TITOLO:" in vintage_raw and "RECENSIONE:" in vintage_raw:
        try:
            parts = vintage_raw.split("RECENSIONE:")
            v_title = parts[0].replace("TITOLO:", "").strip()
            v_body = parts[1].strip()
        except:
            pass

    # 3. AGGIORNAMENTO HTML
    if not os.path.exists(target_file):
        print(f"❌ Errore: Il file {target_file} non esiste!")
        return

    with open(target_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    today = datetime.datetime.now().strftime("%d.%m.%Y")

    # A) Inserimento News
    news_container = soup.find(id="news-feed")
    if news_container:
        new_article = soup.new_tag("article")
        
        # Immagine News Fissa per stabilità
        if topic == 'cinema':
            img_url = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=800&auto=format&fit=crop"
        else:
            img_url = "https://images.unsplash.com/photo-1493225255756-d9584f8606e9?q=80&w=800&auto=format&fit=crop"

        html_content = f"""
            <div style="border-top:1px solid #333; margin-top:2rem; padding-top:1rem; animation: fadeIn 1.5s;">
                <span style="color:#d4af37; font-size:0.7rem;">{today} • FLASH NEWS</span>
                <h3 style="font-family:'Playfair Display'; font-size:1.5rem; margin:5px 0;"><a href="{news_link}" target="_blank">{news_title}</a></h3>
                <img src="{img_url}" class="article-img">
                <div style="font-size:0.9rem; color:#bbb;">{news_body}</div>
            </div>
        """
        new_article.append(BeautifulSoup(html_content, 'html.parser'))
        news_container.insert(0, new_article)

    # B) Sostituzione Vintage
    vintage_container = soup.find(id="vintage-feed")
    if vintage_container:
        vintage_container.clear()
        v_html = f"""
            <h3 style="color:#fff; font-size:1.8rem; margin-bottom:10px;">{v_title}</h3>
            <p style="font-style:italic; color:#aaa; font-size:1.1rem;">"{v_body}"</p>
        """
        vintage_container.append(BeautifulSoup(v_html, 'html.parser'))

    # C) Aggiorna Marquee
    update_marquee(soup, f"{today}: {news_title}")

    # SALVATAGGIO
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
    
    print("✅ Sito aggiornato correttamente!")

if __name__ == "__main__":
    main()
