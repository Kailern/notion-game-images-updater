import requests
import time
from bs4 import BeautifulSoup
from config import *


def get_igdb_access_token():
    """Génère un token d'accès pour l'API IGDB."""
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": IGDB_CLIENT_ID,
        "client_secret": IGDB_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Erreur IGDB Token: {response.text}")


def get_igdb_game_cover(igdb_id):
    """Récupère l'URL de la couverture d'un jeu depuis IGDB."""
    global IGDB_ACCESS_TOKEN
    if not IGDB_ACCESS_TOKEN:
        IGDB_ACCESS_TOKEN = get_igdb_access_token()
    
    url = f"https://api.igdb.com/v4/covers"
    headers = {
        "Client-ID": IGDB_CLIENT_ID,
        "Authorization": f"Bearer {IGDB_ACCESS_TOKEN}",
        "Accept": "application/json"
    }
    body = f"fields url; where game = {igdb_id}; limit 1;"
    response = requests.post(url, headers=headers, data=body)
    if response.status_code == 200 and response.json():
        return response.json()[0]["url"].replace("thumb", "cover_big")
    return None


def scrape_hltb_image(hltb_url):
    """Récupère l'URL de l'image d'un jeu depuis HowLongToBeat (scraping)."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(hltb_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        img_tag = soup.find("img", {"class": "gameimg"})
        if img_tag and "src" in img_tag.attrs:
            return f"https://howlongtobeat.com/{img_tag['src'].lstrip('/')}"
    except Exception as e:
        print(f"Erreur scraping HLTB pour {hltb_url}: {e}")
    return None


def get_notion_pages():
    """Récupère toutes les pages de la base de données Notion."""
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    response = requests.post(url, headers=NOTION_HEADERS)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        raise Exception(f"Erreur Notion API: {response.text}")


def update_notion_page_image(page_id, image_url):
    """Met à jour l'image d'une page Notion."""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            NOTION_IMAGE_PROPERTY: {
                "type": "url",
                "url": image_url
            }
        }
    }
    response = requests.patch(url, headers=NOTION_HEADERS, json=payload)
    return response.status_code == 200


def main():
    pages = get_notion_pages()
    updated = 0
    errors = 0
    
    for page in pages:
        properties = page["properties"]
        
        # Vérifie si l'image existe déjà
        image_prop = properties.get(NOTION_IMAGE_PROPERTY, {})
        if image_prop.get("type") == "url" and image_prop.get("url"):
            print(f"⏭️ Page {page['id']} : Image déjà présente.")
            continue
        
        # Récupère l'IGDB ID ou le lien HLTB
        igdb_id = properties.get(NOTION_IGDB_ID_PROPERTY, {})
        if isinstance(igdb_id, dict):
            igdb_id = igdb_id.get("number") or igdb_id.get("rich_text", [{}])[0].get("plain_text")
        
        hltb_url = properties.get(NOTION_HLTB_URL_PROPERTY, {}).get("url")
        
        image_url = None
        
        # Essaye IGDB en priorité
        if igdb_id:
            print(f"🔍 Recherche image IGDB pour ID {igdb_id}...")
            image_url = get_igdb_game_cover(int(igdb_id))
        
        # Si pas trouvé, essaie HLTB
        if not image_url and hltb_url:
            print(f"🔍 Recherche image HLTB pour {hltb_url}...")
            image_url = scrape_hltb_image(hltb_url)
        
        if image_url:
            success = update_notion_page_image(page["id"], image_url)
            if success:
                print(f"✅ Page {page['id']} : Image mise à jour avec {image_url}")
                updated += 1
            else:
                print(f"❌ Page {page['id']} : Échec de la mise à jour.")
                errors += 1
        else:
            print(f"⚠️ Page {page['id']} : Aucune image trouvée.")
            errors += 1
        
        time.sleep(0.5)  # Respecte les limites de taux de Notion
    
    print(f"\n📊 Résumé : {updated} images mises à jour, {errors} erreurs.")


if __name__ == "__main__":
    main()