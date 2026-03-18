import requests
from bs4 import BeautifulSoup
import logging
from config import REQUEST_TIMEOUT, USER_AGENT

logger = logging.getLogger(__name__)


class FlipkartScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": USER_AGENT
        }
    
    def scrape_product(self, url: str) -> dict:
        """
        Scrape product information from Flipkart URL
        
        Args:
            url: Flipkart product URL
            
        Returns:
            dict with product details (price, title, rating, etc.)
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract title (multiple selectors)
            title = None
            title_tag = soup.find("span", {"class": "B_NuCI"}) or soup.find("h1")
            
            if title_tag:
                title = title_tag.get_text().strip()
            else:
                # Fallback: Extract from URL
                parts = url.split('/')
                for part in parts:
                    if part and '-' in part and not any(x in part.lower() for x in ['flipkart', 'p']):
                        title = part.replace('-', ' ')
                        break
            
            if not title: title = "Flipkart Product"
            
            # Extract price (multiple selectors)
            price = 0.0
            price_selectors = [
                ("div", {"class": "_30jeq3 _16J6S6"}),
                ("div", {"class": "_30jeq3"}),
                ("div", {"class": "_16J6S6"})
            ]
            
            for tag, attrs in price_selectors:
                price_tag = soup.find(tag, attrs)
                if price_tag:
                    price_str = price_tag.get_text().replace(",", "").replace("₹", "").strip()
                    try:
                        price = float(price_str)
                        break
                    except ValueError:
                        continue
            
            # Extract image
            image_tag = soup.find("img", {"class": "_396csP"}) or soup.find("img", {"class": "_2r_T1_"}).find("img")
            if not image_tag:
                image_tag = soup.find("img")
            
            image_url = image_tag.get("src") if image_tag else "https://via.placeholder.com/150"
            
            product_data = {
                "title": title[:100],
                "price": price,
                "currency": "INR",
                "image_url": image_url,
                "url": url,
                "platform": "flipkart"
            }
            
            logger.info(f"Scraped Flipkart: {title} | Price: {price}")
            return product_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping Flipkart: {e}")
            return {
                "error": str(e),
                "url": url,
                "platform": "flipkart"
            }
    
    def validate_url(self, url: str) -> bool:
        """Check if URL is a valid Flipkart product page"""
        return "flipkart.com" in url and "/p/" in url
