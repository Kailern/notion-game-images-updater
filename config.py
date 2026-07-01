import os
from dotenv import load_dotenv

load_dotenv()

# Notion
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_IMAGE_PROPERTY = os.getenv("NOTION_IMAGE_PROPERTY", "Image")
NOTION_IGDB_ID_PROPERTY = os.getenv("NOTION_IGDB_ID_PROPERTY", "IGDB ID")
NOTION_HLTB_URL_PROPERTY = os.getenv("NOTION_HLTB_URL_PROPERTY", "HowLongToBeat")

# IGDB
IGDB_CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
IGDB_CLIENT_SECRET = os.getenv("IGDB_CLIENT_SECRET")
IGDB_ACCESS_TOKEN = None  # sera généré dynamiquement

# Headers pour l'API Notion
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}