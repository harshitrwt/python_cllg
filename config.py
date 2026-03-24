import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "mixtral-8x7b-32768"

FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccount.json")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = "WARNING"

REQUEST_TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

MIN_PRICE_CHANGE_ALERT = 5
SCRAPE_INTERVAL_MINUTES = 60

USERS_COLLECTION = "users"
WATCHLISTS_COLLECTION = "watchlists"
PRICE_HISTORY_COLLECTION = "price_history"
ALERTS_COLLECTION = "alerts"
