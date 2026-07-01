import requests
import time
import logging
from bs4 import BeautifulSoup
from config import *

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def set_log_level(debug=False):
    """Active ou désactive le mode debug."""
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Mode DEBUG activé")
    else:
        logger.setLevel(logging.INFO)


def get_igdb_access_token():
    """Génère un token d'accès pour l'API IGDB."""
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": IGDB_CLIENT_ID,
        "client_secret": IGDB_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    logger.debug(f"Requête pour obtenir le token IGDB avec client_id: {IGDB_CLIENT_ID[:5]}...")
    try:
        response = requests.post(url, params=params)
        if response.status_code == 200:
            token = response.json()["access_token"]
            logger.debug("Token IGDB obtenu avec succès")
            return token
        else:
            logger.error(f"Erreur lors de l'obtention du token IGDB: {response.status_code} - {response.text}")
            raise Exception(f"Erreur IGDB Token: {response.text}")
    except Exception as e:
        logger.error(f"Exception lors de l'obtention du token IGDB: {str(e)}")
        raise


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
    logger.debug(f"Requête IGDB pour l'ID {igdb_id}: {body}")
    
    try:
        response = requests.post(url, headers=headers, data=body)
        logger.debug(f"Réponse IGDB: {response.status_code} - {response.text[:100]}...")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                cover_url = data[0]["url"]
                # Remplace pour obtenir la taille cover_big et le format webp
                final_url = cover_url.replace("t_thumb", "t_cover_big").replace(".jpg", ".webp")
                # Ajoute https: si nécessaire
                if final_url.startswith("//"):
                    final_url = "https:" + final_url
                logger.debug(f"URL de couverture trouvée: {final_url}")
                return final_url
            else:
                logger.warning(f"Aucune couverture trouvée pour l'ID IGDB {igdb_id}")
                return None
        else:
            logger.error(f"Erreur IGDB pour l'ID {igdb_id}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception lors de la récupération de la couverture IGDB pour {igdb_id}: {str(e)}")
        return None


def scrape_hltb_image(hltb_url):
    """Récupère l'URL de l'image d'un jeu depuis HowLongToBeat (scraping)."""
    if not hltb_url:
        logger.warning("Aucune URL HLTB fournie")
        return None
        
    logger.debug(f"Scraping HLTB pour: {hltb_url}")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(hltb_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Erreur HTTP lors du scraping HLTB: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, "html.parser")
        img_tag = soup.find("img", {"class": "gameimg"})
        if img_tag and "src" in img_tag.attrs:
            image_url = f"https://howlongtobeat.com/{img_tag['src'].lstrip('/')}"
            logger.debug(f"Image HLTB trouvée: {image_url}")
            return image_url
        else:
            logger.warning(f"Aucune image trouvée sur la page HLTB: {hltb_url}")
            return None
    except Exception as e:
        logger.error(f"Exception lors du scraping HLTB pour {hltb_url}: {str(e)}")
        return None


def get_notion_pages():
    """Récupère toutes les pages de la base de données Notion."""
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    logger.debug(f"Requête Notion pour la base: {NOTION_DATABASE_ID}")
    
    try:
        # Filtre pour ne récupérer que les pages sans image
        # Utilisation du type 'files' pour la propriété Image
        payload = {
            "filter": {
                "property": NOTION_IMAGE_PROPERTY,
                "files": {
                    "is_empty": True
                }
            }
        }
        logger.debug(f"Payload de filtrage: {payload}")
        
        response = requests.post(url, headers=NOTION_HEADERS, json=payload)
        logger.debug(f"Réponse Notion: {response.status_code}")
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            logger.info(f"Trouvé {len(results)} jeux sans image dans Notion")
            return results
        else:
            logger.error(f"Erreur Notion API: {response.status_code} - {response.text}")
            raise Exception(f"Erreur Notion API: {response.text}")
    except Exception as e:
        logger.error(f"Exception lors de la récupération des pages Notion: {str(e)}")
        raise


def update_notion_page_image(page_id, image_url):
    """Met à jour l'image d'une page Notion."""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    # Format correct pour la propriété de type 'files' dans Notion
    payload = {
        "properties": {
            NOTION_IMAGE_PROPERTY: {
                "files": [
                    {
                        "name": "Game Cover",
                        "type": "external",
                        "external": {
                            "url": image_url
                        }
                    }
                ]
            }
        }
    }
    
    logger.debug(f"Mise à jour de la page {page_id} avec l'image: {image_url}")
    logger.debug(f"Payload: {payload}")
    
    try:
        response = requests.patch(url, headers=NOTION_HEADERS, json=payload)
        if response.status_code == 200:
            logger.info(f"✅ Page {page_id} : Image mise à jour avec {image_url}")
            return True
        else:
            logger.error(f"❌ Page {page_id} : Échec de la mise à jour. Code: {response.status_code}, Réponse: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception lors de la mise à jour de la page {page_id}: {str(e)}")
        return False


def extract_property_value(property_data):
    """Extrait la valeur d'une propriété Notion (quelle que soit son type)."""
    if not property_data:
        return None
    
    property_type = property_data.get("type")
    
    if property_type == "number":
        return property_data.get("number")
    elif property_type == "rich_text":
        rich_text_list = property_data.get("rich_text", [])
        if rich_text_list:
            return rich_text_list[0].get("plain_text")
    elif property_type == "title":
        title_list = property_data.get("title", [])
        if title_list:
            return title_list[0].get("plain_text")
    elif property_type == "url":
        return property_data.get("url")
    elif property_type == "files":
        files = property_data.get("files", [])
        if files:
            return files[0].get("external", {}).get("url")
    
    return None


def main(debug=False):
    """Fonction principale avec option de debug."""
    set_log_level(debug)
    
    logger.info("Début de l'exécution du script...")
    
    try:
        pages = get_notion_pages()
    except Exception as e:
        logger.error(f"Impossible de récupérer les pages Notion: {str(e)}")
        return
    
    updated = 0
    errors = 0
    
    for page in pages:
        properties = page["properties"]
        page_id = page["id"]
        logger.debug(f"\nTraitement de la page: {page_id}")
        
        # Récupère l'IGDB ID
        igdb_id_raw = properties.get(NOTION_IGDB_ID_PROPERTY, {})
        igdb_id = extract_property_value(igdb_id_raw)
        logger.debug(f"IGDB ID brut: {igdb_id_raw}")
        logger.debug(f"IGDB ID extrait: {igdb_id}")
        
        # Récupère le lien HLTB
        hltb_url_raw = properties.get(NOTION_HLTB_URL_PROPERTY, {})
        hltb_url = extract_property_value(hltb_url_raw)
        logger.debug(f"HLTB URL brute: {hltb_url_raw}")
        logger.debug(f"HLTB URL extraite: {hltb_url}")
        
        image_url = None
        
        # Essaye IGDB en priorité
        if igdb_id:
            try:
                logger.info(f"🔍 Recherche image IGDB pour ID {igdb_id}...")
                image_url = get_igdb_game_cover(int(igdb_id))
            except ValueError as e:
                logger.error(f"ID IGDB invalide pour la page {page_id}: {igdb_id} - {str(e)}")
                errors += 1
                continue
        
        # Si pas trouvé, essaie HLTB
        if not image_url and hltb_url:
            logger.info(f"🔍 Recherche image HLTB pour {hltb_url}...")
            image_url = scrape_hltb_image(hltb_url)
        
        if image_url:
            success = update_notion_page_image(page_id, image_url)
            if success:
                updated += 1
            else:
                errors += 1
        else:
            logger.warning(f"⚠️ Page {page_id} : Aucune image trouvée (IGDB: {igdb_id}, HLTB: {hltb_url})")
            errors += 1
        
        time.sleep(0.5)  # Respecte les limites de taux de Notion
    
    logger.info(f"\n📊 Résumé : {updated} images mises à jour, {errors} erreurs.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Mise à jour des images des jeux dans Notion")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug pour plus de logs")
    args = parser.parse_args()
    
    main(debug=args.debug)