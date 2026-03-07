import requests
from bs4 import BeautifulSoup
import logging
from config import REQUEST_TIMEOUT, USER_AGENT

logger = logging.getLogger(__name__)


class AmazonScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": USER_AGENT
        }
    
    def scrape_product(self, url: str) -> dict:
        """
        Scrape product information from Amazon URL
        
        Args:
            url: Amazon product URL
            
        Returns:
            dict with product details (price, title, rating, etc.)
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract product information (placeholder - adjust based on actual HTML structure)
            product_data = {
                "title": "Sample Product",
                "price": 999.99,
                "currency": "INR",
                "rating": 4.5,
                "reviews": 150,
                "in_stock": True,
                "url": url,
                "platform": "amazon"
            }
            
            logger.info(f"Successfully scraped Amazon product: {product_data['title']}")
            return product_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping Amazon product: {e}")
            return {
                "error": str(e),
                "url": url,
                "platform": "amazon"
            }
    
    def validate_url(self, url: str) -> bool:
        """Check if URL is a valid Amazon product page"""
        return "amazon.com" in url and "/dp/" in url
