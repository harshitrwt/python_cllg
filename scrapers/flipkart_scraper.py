from bs4 import BeautifulSoup
import requests
import re
import logging
import time
import random
from config import REQUEST_TIMEOUT
from utils.user_agents import get_headers

logger = logging.getLogger(__name__)

class FlipkartScraper:
    def __init__(self):
        self.session = requests.Session()
    
    def scrape_product(self, url: str) -> dict:
        try:
            if not self.validate_url(url):
                return {"error": "Invalid Flipkart product URL", "url": url, "platform": "flipkart"}

            headers = get_headers()
            time.sleep(random.uniform(1.0, 2.5))
            
            response = self.session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            title = None
            title_selectors = [
                ("span", {"class": "B_NuCI"}),
                ("h1", {"class": "yhB1nd"}),
                ("span", {"class": "_35Ky9a"}),
                ("span", {"class": "VU-Z7M"}),
                ("span", {"class": "m_1WcE"}),
            ]
            
            for tag, attrs in title_selectors:
                title_tag = soup.find(tag, attrs)
                if title_tag:
                    title = title_tag.get_text().strip()
                    break
            
            if not title:
                parts = url.split('/')
                for part in parts:
                    if part and '-' in part and not any(x in part.lower() for x in ['flipkart', 'p', 'itm']):
                        title = part.replace('-', ' ').title()
                        break
            
            title = title or "Unknown Flipkart Product"

            price = 0.0
            price_selectors = [
                ("div", {"class": "_30jeq3 _16J6S6"}),
                ("div", {"class": "_30jeq3"}),
                ("div", {"class": "Nx9bqj _4b5DiR"}),
                ("div", {"class": "Nx9bqj"}),
                ("div", {"class": "_16J6S6"}),
                ("div", {"class": "fP6977"})
            ]
            
            for tag, attrs in price_selectors:
                price_tag = soup.find(tag, attrs)
                if price_tag:
                    price_str = price_tag.get_text().strip()
                    price_str = re.sub(r'[^\d.]', '', price_str.replace(',', '').replace('₹', ''))
                    try:
                        if price_str:
                            price = float(price_str)
                            break
                    except ValueError:
                        continue
            
            image_url = "https://via.placeholder.com/300?text=No+Image"
            image_selectors = [
                ("img", {"class": "_396csP _3exPp9"}),
                ("img", {"class": "j-f872"}),
                ("img", {"class": "_30XB9F"}),
                ("img", {"class": "_2r_T1_"}),
                ("img", {"class": "DByo9Z"})
            ]
            
            for tag, attrs in image_selectors:
                img_tag = soup.find(tag, attrs)
                if img_tag:
                    image_url = img_tag.get("src")
                    src_sets = img_tag.get("srcset")
                    if src_sets:
                        image_url = src_sets.split(",")[-1].split(" ")[0]
                    break
            
            description = ""
            desc_tag = soup.find("div", {"class": "_1mXcCf"}) or soup.find("div", {"class": "RmoSge"})
            if desc_tag:
                description = desc_tag.get_text().strip()
            else:
                highlights = soup.find("div", {"class": "_2418kt"})
                if highlights:
                    description = " | ".join([li.get_text() for li in highlights.find_all("li")])

            product_data = {
                "title": title[:200],
                "price": price,
                "currency": "INR",
                "image_url": image_url,
                "description": description[:500] if description else "No description available",
                "url": url,
                "platform": "flipkart",
                "success": True if price > 0 else False
            }
            
            logger.info(f"Scraped Flipkart: {title[:50]}... | Price: {price}")
            return product_data
            
        except Exception as e:
            logger.error(f"Error scraping Flipkart {url}: {e}")
            return {
                "error": str(e),
                "url": url,
                "platform": "flipkart",
                "success": False
            }
    
    def validate_url(self, url: str) -> bool:
        return "flipkart" in url.lower() and ("/p/" in url.lower() or "/itm" in url.lower())


