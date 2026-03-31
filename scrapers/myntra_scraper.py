from bs4 import BeautifulSoup
import requests
import re
import logging
import time
import random
import json
from config import REQUEST_TIMEOUT
from utils.user_agents import get_headers

logger = logging.getLogger(__name__)

class MyntraScraper:
    def __init__(self):
        self.session = requests.Session()
    
    def scrape_product(self, url: str) -> dict:
        try:
            if not self.validate_url(url):
                return {"error": "Invalid Myntra product URL", "url": url, "platform": "myntra"}

            for attempt in range(2):
                headers = get_headers()
                headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                
                time.sleep(random.uniform(1.0, 3.0))
                response = self.session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    break
            
            if response.status_code != 200:
                 return {"error": f"Myntra returned HTTP {response.status_code}", "url": url, "platform": "myntra"}

            soup = BeautifulSoup(response.content, 'lxml')
            
            script_tags = soup.find_all("script")
            pdp_data = None
            for tag in script_tags:
                if tag.string and "window.__myx =" in tag.string:
                    try:
                        json_text = re.search(r"window\.__myx\s*=\s*({.*?});", tag.string).group(1)
                        data = json.loads(json_text)
                        pdp_data = data.get("pdpData", {})
                        break
                    except Exception as e:
                        logger.error(f"Error extracting JSON from myntra: {e}")
                        continue
            
            if not pdp_data:
                 return self._fallback_scrape(soup, url)
                 
            try:
                title = pdp_data.get("name", "Unknown Myntra Product")
                priceDetails = pdp_data.get("price", {})
                price = float(priceDetails.get("discounted", 0))
                if price == 0:
                    price = float(priceDetails.get("mrp", 0))
                
                media = pdp_data.get("media", {}).get("albums", [])
                image_url = "https://via.placeholder.com/300?text=No+Image"
                if media and media[0].get("images"):
                    image_url = media[0]["images"][0].get("imageURL", image_url)
                    
                descriptions = pdp_data.get("productDetails", [])
                description = descriptions[0].get("description", "No description") if descriptions else "No description"
                
                return {
                    "title": title[:200],
                    "price": price,
                    "currency": "INR",
                    "image_url": image_url,
                    "description": str(description)[:500],
                    "url": url,
                    "platform": "myntra",
                    "success": True if price > 0 else False
                }
            except Exception as e:
                logger.error(f"Error parsing Myntra structured data: {e}")
                return self._fallback_scrape(soup, url)
            
        except Exception as e:
            logger.error(f"Error scraping Myntra {url}: {e}")
            return {
                "error": str(e),
                "url": url,
                "platform": "myntra",
                "success": False
            }
            
    def _fallback_scrape(self, soup, url):
        title_tag = soup.find("h1", {"class": "pdp-title"}) or soup.find("h1", {"class": "pdp-name"})
        title = title_tag.get_text().strip() if title_tag else "Unknown Myntra Product"
        
        price_tag = soup.find("span", {"class": "pdp-price"}) or soup.find("strong", {"class": "pdp-price"})
        price = 0.0
        if price_tag:
            price_str = re.sub(r'[^\d.]', '', price_tag.get_text())
            if price_str: price = float(price_str)
            
        return {
            "title": title[:200],
            "price": price,
            "currency": "INR",
            "image_url": "https://via.placeholder.com/300?text=No+Image",
            "description": "Fallback scraping used.",
            "url": url,
            "platform": "myntra",
            "success": True if price > 0 else False
        }
    
    def validate_url(self, url: str) -> bool:
        return "myntra" in url.lower()
