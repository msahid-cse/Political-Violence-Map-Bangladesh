
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re
import time
import os
from urllib.parse import urljoin
from dotenv import load_dotenv

# .env ফাইল থেকে এনভায়রনমেন্ট ভ্যারিয়েবল লোড করা
load_dotenv()

# --- ধাপ ক: MongoDB Atlas এর সাথে কানেকশন স্থাপন ---
MONGO_CONNECTION_STRING = os.getenv('MONGO_URI')

if not MONGO_CONNECTION_STRING:
    print("Error: MONGO_URI not found. Please create a .env file with your MongoDB connection string.")
    exit()

try:
    client = MongoClient(MONGO_CONNECTION_STRING)
    db = client['political_violence_db'] 
    incidents_collection = db['incidents'] 
    print("MongoDB connection successful.")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    exit()

# --- ধাপ খ: লেখা বিশ্লেষণ এবং তথ্য সনাক্তকরণ ---
DISTRICTS_BN = [
    "ঢাকা", "গাজীপুর", "নারায়ণগঞ্জ", "নরসিংদী", "মুন্সিগঞ্জ", "মানিকগঞ্জ", "টাঙ্গাইল", "কিশোরগঞ্জ", "ফরিদপুর", "মাদারীপুর",
    "শরীয়তপুর", "রাজবাড়ী", "গোপালগঞ্জ", "চট্টগ্রাম", "কক্সবাজার", "বান্দরবান", "রাঙ্গামাটি", "খাগড়াছড়ি", "কুমিল্লা", "ব্রাহ্মণবাড়িয়া",
    "চাঁদপুর", "নোয়াখালী", "ফেনী", "লক্ষ্মীপুর", "সিলেট", "সুনামগঞ্জ", "হবিগঞ্জ", "মৌলভীবাজার", "রাজশাহী", "বগুড়া",
    "পাবনা", "সিরাজগঞ্জ", "নওগাঁ", "জয়পুরহাট", "চাঁপাইনবাবগঞ্জ", "নাটোর", "খুলনা", "বাগেরহাট", "সাতক্ষীরা", "যশোর",
    "নড়াইল", "মাগুরা", "ঝিনাইদহ", "কুষ্টিয়া", "চুয়াডাঙ্গা", "মেহেরপুর", "বরিশাল", "ভোলা", "পটুয়াখালী", "পিরোজপুর",
    "বরগুনা", "ঝালকাঠি", "রংপুর", "দিনাজপুর", "গাইবান্ধা", "কুড়িগ্রাম", "লালমনিরহাট", "নীলফামারী", "পঞ্চগড়", "ঠাকুরগাঁও",
    "ময়মনসিংহ", "জামালপুর", "শেরপুর", "নেত্রকোনা"
]
POLITICAL_PARTIES_KEYWORDS = {
    "আওয়ামী লীগ": ["আওয়ামী লীগ", "লীগ", "ছাত্রলীগ", "যুবলীগ"],
    "বিএনপি": ["বিএনপি", "দল", "ছাত্রদল", "যুবদল"],
    "জামায়াত": ["জামায়াত", "শিবির"],
    "জাতীয় পার্টি": ["জাতীয় পার্টি", "জাপা"]
}

def analyze_article_content(text):
    fatalities = re.search(r'(\d+)\s*জন?\s*(নিহত|মারা গেছেন)', text)
    injuries = re.search(r'(\d+)\s*জন?\s*আহত', text)
    
    found_location = next((dist for dist in DISTRICTS_BN if dist in text), None)
    
    found_parties = []
    for party, keywords in POLITICAL_PARTIES_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            found_parties.append(party)

    return {
        'fatalities': int(fatalities.group(1)) if fatalities else 0,
        'injuries': int(injuries.group(1)) if injuries else 0,
        'location': found_location,
        'political_parties': ", ".join(list(set(found_parties)))
    }

# ... (বাকি ফাংশনগুলো আগের মতোই থাকবে) ...
# get_coordinates_from_location, get_article_details, generic_scraper

def get_coordinates_from_location(location_name):
    if not location_name: return None, None
    print(f"Geocoding for: {location_name}, বাংলাদেশ")
    try:
        time.sleep(1.5) 
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': f"{location_name}, বাংলাদেশ", 'format': 'json', 'limit': 1},
            timeout=20
        )
        response.raise_for_status()
        results = response.json()
        if results: return results[0].get('lat'), results[0].get('lon')
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None, None

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def get_article_details(url, content_selector):
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.content, 'html.parser')
        content_body = soup.select_one(content_selector)
        return content_body.get_text(strip=True) if content_body else None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article details from {url}: {e}")
        return None

def generic_scraper(source_name, base_url, list_selector):
    print(f"Scraping {source_name}: {base_url}")
    articles = []
    try:
        response = requests.get(base_url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.select(list_selector)
        for link in links[:12]:
            title = link.get_text(strip=True)
            url = link.get('href')
            if title and url and len(title) > 10:
                full_url = urljoin(base_url, url)
                articles.append({'title': title, 'url': full_url, 'source': source_name})
    except Exception as e:
        print(f"Could not scrape {source_name}. Error: {e}")
    return articles


def run_scraper():

    sources = [
        {'name': 'Prothom Alo', 'url': 'https://www.prothomalo.com/politics', 'list_selector': 'a.link_overlay', 'content_selector': '.story-content'},
        {'name': 'Jugantor', 'url': 'https://www.jugantor.com/politics', 'list_selector': '.lead-news-list-item a, .news-list-item a', 'content_selector': '.post-content-text'},
        {'name': 'Ittefaq', 'url': 'https://www.ittefaq.com.bd/politics', 'list_selector': '.news-list-item .title a', 'content_selector': '.article-content'},
        {'name': 'BD Pratidin', 'url': 'https://www.bd-pratidin.com/current-politics', 'list_selector': '.news-item a', 'content_selector': '#news-content'},
        {'name': 'Samakal', 'url': 'https://samakal.com/politics', 'list_selector': '.news-list-item a.link', 'content_selector': '.story-content'},
        {'name': 'Kalbela', 'url': 'https://www.kalbela.com/politics', 'list_selector': 'a.headline', 'content_selector': '.post-content'},
        {'name': 'Ajker Patrika', 'url': 'https://www.ajkerpatrika.com/politics', 'list_selector': '.list-item h2 a', 'content_selector': '.detail-content'},
        {'name': 'Jaijaidin', 'url': 'https://www.jaijaidinbd.com/politics', 'list_selector': '.news-item-block a', 'content_selector': '.news-details'},
        {'name': 'Janakantha', 'url': 'https://www.dailyjanakantha.com/politics/', 'list_selector': '.news-title a', 'content_selector': '.news-element-text'},
        {'name': 'Bonik Barta', 'url': 'https://bonikbarta.net/home/latest', 'list_selector': 'h2 a', 'content_selector': '.DNewsDetails'},
        {'name': 'Amader Shomoy', 'url': 'https://www.dainikamadershomoy.com/all-news/bangladesh', 'list_selector': '.cat-news-list a', 'content_selector': '.dtl-content-box'},
        {'name': 'Manob Zamin', 'url': 'https://mzamin.com/category.php?cat=24', 'list_selector': '.cat-news-list a', 'content_selector': '.details'},
        {'name': 'Protidinersangbad', 'url': 'https://www.protidinersangbad.com/politics', 'list_selector': '.list-story-item a', 'content_selector': '.story-details'},
        {'name': 'Amarsangbad', 'url': 'https://www.amarsangbad.com/politics', 'list_selector': '.category-list-item a', 'content_selector': '.details-wrapper'},
        {'name': 'Naya Diganta', 'url': 'https://www.dailynayadiganta.com/', 'list_selector': '.latest-news-list a', 'content_selector': '.news-content'},
        {'name': 'Daily Sangram', 'url': 'https://dailysangram.com/last-news', 'list_selector': '.cat-box-item a', 'content_selector': '#dtl_content_block'}
    ]

    all_articles = []
    for source in sources:
        all_articles.extend(generic_scraper(source['name'], source['url'], source['list_selector']))

    print(f"\nFound {len(all_articles)} total articles. Processing new ones...")

    for article in all_articles:
        if incidents_collection.find_one({'news_url': article['url']}):
            print(f"Skipping already saved article: {article['title']}")
            continue

        print(f"\nProcessing new article from {article['source']}: {article['title']}")
        
        source_config = next((s for s in sources if s['name'] == article['source']), None)
        if not source_config: continue
            
        content = get_article_details(article['url'], source_config['content_selector'])
        if not content:
            print(f"Could not retrieve content for: {article['title']}")
            continue

        analysis_data = analyze_article_content(content)
        
        lat, lon = get_coordinates_from_location(analysis_data['location'])

        if lat and lon:
            incident_document = {
                "news_title": article['title'],
                "news_url": article['url'],
                "source": article['source'],
                "location_name": analysis_data['location'],
                "latitude": float(lat),
                "longitude": float(lon),
                "fatalities": analysis_data['fatalities'],
                "injuries": analysis_data['injuries'],
                "political_parties": analysis_data['political_parties'],
                "summary": content[:250] + "...",
                "incident_date": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
            }
            
            incidents_collection.insert_one(incident_document)
            print(f"SUCCESS: Saved incident from '{article['title']}' to database.")
        else:
            print(f"Could not geocode location for article: {article['title']}")

    client.close()
    print("\nScraping process finished.")

if __name__ == '__main__':
    run_scraper()
