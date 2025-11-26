import os
import random
import datetime
import feedparser
import google.generativeai as genai
from bs4 import BeautifulSoup

# --- CONFIGURAZIONE ---
# Chiave API presa dai Segreti di GitHub
GENAI_API_KEY = os.environ["GEMINI_API_KEY"]
genai.configure(api_key=GENAI_API_KEY)

# Fonti RSS Reali (Cinema Italiano e Musica)
RSS_FEEDS = {
    'cinema': 'https://www.cinemaitaliano.info/rss/notizie.xml', # News Cinema Italiano
    'musica': 'https://www.rockol.it/rss/news/musica-italiana'    # News Musica (filtriamo dopo)
}

# --- FUNZIONI ---

def get_gemini_article(topic, source_title, source_summary):
    """Chiede a Gemini di scrivere l'articolo con il tono giusto"""
    
    # Configuriamo il modello (Gemini 2.0 Flash è veloce ed economico)
    model = genai.GenerativeModel('gemini-2.0-flash')

    if topic == 'cinema':
        prompt_sys = """Sei un giornalista di 'Marte Velvet', rivista underground del 1978.
        Scrivi una news breve (max 150 parole) basata sui dati forniti.
        TONO: Cinico, competente, usa slang anni 70/80 (es: "tosto", "giusto", "la dritta", "pellicola", "il botteghino piange").
        FOCUS: Cinema Italiano, aspetti legislativi, fondi statali o box office. Sii critico verso il sistema ma ama l'arte.
        FORMATTAZIONE: Usa HTML semplice (<p>). Niente Titoli H1/H2."""
    else:
        prompt_sys = """Sei un critico musicale radiofonico anni '80 di 'Marte Velvet'.
        Scrivi una news breve (max 150 parole) basata sui dati forniti.
        TONO: Caldo, avvolgente, stile DJ notturno. Usa termini come "groove", "vibes", "basso che spinge", "funky".
        FOCUS: Cerca di collegare la notizia odierna a sonorità Rap, RnB, Disco o Funky del passato.
        FORMATTAZIONE: Usa HTML semplice (<p>). Niente Titoli H1/H2."""

    full_prompt = f"{prompt_sys}\n\nNOTIZIA ORIGINALE:\nTitolo: {source_title}\nContenuto: {source_summary}\n\nScrivi l'articolo per il blog:"
    
    response = model.generate_content(full_prompt)
    return response.text

def update_html(topic, title, content, original_link):
    """Inserisce il nuovo articolo in cima al file index.html"""
    
    file_path = 'index.html'
    
    # Immagini random da Unsplash con filtro 'vintage'
    if topic == 'cinema':
        img_url = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=800&auto=format&fit=crop"
        category = "CINEMA • ITALIA • BOX OFFICE"
    else:
        img_url = "https://images.unsplash.com/photo-1514525253440-b393452e3383?q=80&w=800&auto=format&fit=crop"
        category = "MUSICA • GROOVE • URBAN"

    today = datetime.datetime.now().strftime("%d %b %Y").upper()

    # Leggi l'HTML esistente
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Crea il nuovo blocco articolo
    new_article = soup.new_tag("article")
    new_article.attrs['class'] = 'fade-in' # Animazione opzionale
    
    html_content = f"""
        <div class="meta-data">{category} • {today}</div>
        <h2 class="article-title"><a href="{original_link}" target="_blank">{title}</a></h2>
        <img src="{img_url}" class="article-img" alt="{topic}">
        <div class="article-body">
            {content}
            <p style="font-size:0.7rem; margin-top:10px; opacity:0.6;">[Fonte: Feed RSS Automatico • Elaborazione Gemini]</p>
        </div>
    """
    new_article.append(BeautifulSoup(html_content, 'html.parser'))

    # Trova la griglia e inserisci all'inizio
    grid = soup.find(id="content-feed")
    if grid:
        grid.insert(0, new_article)
        
        # Salviamo il file modificato
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(str(soup.prettify()))
        print("✅ Articolo inserito con successo!")
    else:
        print("❌ Errore: Non ho trovato l'ID 'content-feed' nell'HTML.")

# --- MAIN ---
def main():
    # Scegliamo a caso se parlare di Cinema o Musica oggi
    topic = random.choice(['cinema', 'musica'])
    print(f"📡 Argomento del giorno: {topic.upper()}")

    feed = feedparser.parse(RSS_FEEDS[topic])
    
    if not feed.entries:
        print("❌ Nessuna news trovata nel feed RSS.")
        return

    # Prendiamo la prima notizia del feed
    news = feed.entries[0]
    print(f"📰 Notizia trovata: {news.title}")

    # Generiamo l'articolo con Gemini
    print("🤖 Chiedo a Gemini di scrivere...")
    ai_text = get_gemini_article(topic, news.title, news.summary)
    
    # Puliamo eventuale markdown dal titolo generato (se Gemini sbaglia)
    clean_title = news.title # Per ora teniamo il titolo originale per chiarezza, o potremmo far generare anche quello

    # Aggiorniamo il sito
    update_html(topic, clean_title, ai_text, news.link)

if __name__ == "__main__":
    main()
