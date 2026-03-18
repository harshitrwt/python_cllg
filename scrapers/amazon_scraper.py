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
            
            # Extract title (multiple selectors)
            title = None
            title_tag = soup.find("span", {"id": "productTitle"}) or soup.find("h1", {"id": "title"})
            if title_tag:
                title = title_tag.get_text().strip()
            else:
                # Fallback: Extract from URL slug
                parts = url.split('/')
                if len(parts) > 3:
                    for part in parts:
                        if part and not any(x in part for x in ['dp', 'gp', 'product', 'amazon']):
                            title = part.replace('-', ' ')
                            break
            
            if not title: title = "Amazon Product"
            
            # Extract price (multiple selectors)
            price = 0.0
            price_selectors = [
                ("span", {"class": "a-price-whole"}),
                ("span", {"id": "priceblock_ourprice"}),
                ("span", {"id": "priceblock_dealprice"}),
                ("span", {"class": "a-color-price"})
            ]
            
            for tag, attrs in price_selectors:
                price_tag = soup.find(tag, attrs)
                if price_tag:
                    price_str = price_tag.get_text().replace(",", "").replace("₹", "").replace("$", "").strip()
                    try:
                        price = float(price_str)
                        break
                    except ValueError:
                        continue
            
            # Extract image
            image_tag = soup.find("img", {"id": "landingImage"}) or soup.find("img", {"id": "main-image"})
            image_url = image_tag.get("src") if image_tag else "https://via.placeholder.com/150"
            
            product_data = {
                "title": title[:100],
                "price": price,
                "currency": "INR",
                "image_url": image_url,
                "url": url,
                "platform": "amazon"
            }
            
            logger.info(f"Scraped Amazon: {title} | Price: {price}")
            return product_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping Amazon: {e}")
            return {
                "error": str(e),
                "url": url,
                "platform": "amazon"
            }
    
    def validate_url(self, url: str) -> bool:
        """Check if URL is a valid Amazon product page"""
        return "amazon.com" in url and "/dp/" in url
