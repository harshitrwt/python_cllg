import firebase_admin
from firebase_admin import credentials, firestore
import logging
from config import FIREBASE_CREDENTIALS_PATH, FIREBASE_PROJECT_ID
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class FirebaseDB:
    def __init__(self):
        """Initialize Firebase connection"""
        self.db = None
        self.init_firebase()
    
    def init_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                if FIREBASE_CREDENTIALS_PATH:
                    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
                    firebase_admin.initialize_app(cred)
                else:
                    firebase_admin.initialize_app()
            
            self.db = firestore.client()
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
            raise
    
    def add_user(self, user_id: str, user_data: Dict) -> bool:
        """Add a new user"""
        try:
            self.db.collection("users").document(user_id).set({
                **user_data,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })
            logger.info(f"User added: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False
    
    def add_to_watchlist(self, user_id: str, product_url: str, product_data: Dict) -> bool:
        """Add product to user's watchlist"""
        try:
            self.db.collection("watchlists").add({
                "user_id": user_id,
                "product_url": product_url,
                "product_data": product_data,
                "added_at": datetime.now(),
                "target_price": None
            })
            logger.info(f"Product added to watchlist for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")
            return False
    
    def get_watchlist(self, user_id: str) -> List[Dict]:
        """Get user's watchlist"""
        try:
            docs = self.db.collection("watchlists").where("user_id", "==", user_id).stream()
            watchlist = [doc.to_dict() for doc in docs]
            return watchlist
        except Exception as e:
            logger.error(f"Error fetching watchlist: {e}")
            return []
    
    def add_price_history(self, product_url: str, price: float, timestamp: datetime = None) -> bool:
        """Record price history for a product"""
        try:
            self.db.collection("price_history").add({
                "product_url": product_url,
                "price": price,
                "timestamp": timestamp or datetime.now()
            })
            logger.info(f"Price recorded for {product_url}: {price}")
            return True
        except Exception as e:
            logger.error(f"Error recording price history: {e}")
            return False
    
    def get_price_history(self, product_url: str, limit: int = 50) -> List[Dict]:
        """Get price history for a product"""
        try:
            docs = self.db.collection("price_history")\
                .where("product_url", "==", product_url)\
                .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
            
            history = [doc.to_dict() for doc in docs]
            return history
        except Exception as e:
            logger.error(f"Error fetching price history: {e}")
            return []
    
    def create_alert(self, user_id: str, product_url: str, target_price: float) -> bool:
        """Create a price alert for user"""
        try:
            self.db.collection("alerts").add({
                "user_id": user_id,
                "product_url": product_url,
                "target_price": target_price,
                "created_at": datetime.now(),
                "triggered": False
            })
            logger.info(f"Alert created for {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return False
    
    def get_user_alerts(self, user_id: str) -> List[Dict]:
        """Get all alerts for a user"""
        try:
            docs = self.db.collection("alerts").where("user_id", "==", user_id).stream()
            alerts = [doc.to_dict() for doc in docs]
            return alerts
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return []
