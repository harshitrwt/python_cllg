"""
Configuration management for SmartPriceWatcher
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "mixtral-8x7b-32768"

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")

# Application Settings
DEBUG = os.getenv("DEBUG", "False") == "True"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Scraper Settings
REQUEST_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Price Tracking
MIN_PRICE_CHANGE_ALERT = 5  # Alert if price drops by at least 5%
SCRAPE_INTERVAL_MINUTES = 60  # Check prices every hour

# Database Collections
USERS_COLLECTION = "users"
WATCHLISTS_COLLECTION = "watchlists"
PRICE_HISTORY_COLLECTION = "price_history"
ALERTS_COLLECTION = "alerts"

# Supported e-commerce platforms
SUPPORTED_PLATFORMS = {
    "amazon": "amazon.com",
    "flipkart": "flipkart.com"
}
