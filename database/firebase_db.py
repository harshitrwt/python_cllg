import firebase_admin
from firebase_admin import credentials, firestore
import logging
from config import FIREBASE_CREDENTIALS_PATH, FIREBASE_PROJECT_ID
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class FirebaseDB:
    def __init__(self):
        self.db = None
        self.init_firebase()
    
    def init_firebase(self):
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
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        try:
            doc = self.db.collection("users").document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    def add_to_watchlist(self, user_id: str, product_url: str, product_data: Dict) -> bool:
        try:
            target_price = product_data.get("target_price")
            self.db.collection("watchlists").add({
                "user_id": user_id,
                "product_url": product_url,
                "product_data": product_data,
                "added_at": datetime.now(),
                "target_price": target_price
            })
            logger.info(f"Product added to watchlist for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")
            return False

    def update_product_price(self, doc_id: str, new_price: float) -> bool:
        try:
            doc_ref = self.db.collection("watchlists").document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                product_data = data.get("product_data", {})
                product_data["price"] = new_price
                doc_ref.update({
                    "product_data": product_data,
                    "updated_at": datetime.now()
                })
                self.add_price_history(data.get("product_url"), new_price)
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating product price: {e}")
            return False
    
    def get_watchlist(self, user_id: str) -> List[Dict]:
        try:
            from google.cloud.firestore_v1.base_query import FieldFilter
            docs = self.db.collection("watchlists").where(filter=FieldFilter("user_id", "==", user_id)).stream()
            watchlist = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                watchlist.append(data)
            logger.info(f"Fetched {len(watchlist)} watchlist items for {user_id}")
            return watchlist
        except Exception as e:
            logger.error(f"Error fetching watchlist: {e}")
            return []
    
    def remove_from_watchlist(self, doc_id: str) -> bool:
        try:
            self.db.collection("watchlists").document(doc_id).delete()
            logger.info(f"Product removed from watchlist: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing from watchlist: {e}")
            return False
    
    def add_price_history(self, product_url: str, price: float, timestamp: datetime = None) -> bool:
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
        try:
            from google.cloud.firestore_v1.base_query import FieldFilter
            docs = self.db.collection("price_history")\
                .where(filter=FieldFilter("product_url", "==", product_url))\
                .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
            
            history = [doc.to_dict() for doc in docs]
            return history
        except Exception as e:
            logger.error(f"Error fetching price history: {e}")
            return []
    
    def create_alert(self, user_id: str, product_url: str, target_price: float) -> bool:
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
        try:
            from google.cloud.firestore_v1.base_query import FieldFilter
            docs = self.db.collection("alerts").where(filter=FieldFilter("user_id", "==", user_id)).stream()
            alerts = [doc.to_dict() for doc in docs]
            return alerts
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return []

