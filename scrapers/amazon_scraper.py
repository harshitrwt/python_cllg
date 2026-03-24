from bs4 import BeautifulSoup
import requests
import re
import logging
from config import REQUEST_TIMEOUT, USER_AGENT

logger = logging.getLogger(__name__)

class AmazonScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive"
        }
    
    def scrape_product(self, url: str) -> dict:
        try:
            if not self.validate_url(url):
                return {"error": "Invalid Amazon product URL", "url": url, "platform": "amazon"}

            response = requests.get(url, headers=self.headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            if "captcha" in response.text.lower() or "api-services-support@amazon.com" in response.text.lower():
                logger.warning(f"Amazon blocked the request for {url}")
                return {"error": "Amazon blocked the request. Try again later or use a proxy.", "url": url, "platform": "amazon"}

            soup = BeautifulSoup(response.content, 'lxml')
            
            title = None
            title_selectors = [
                ("span", {"id": "productTitle"}),
                ("h1", {"id": "title"}),
                ("span", {"class": "a-size-extra-large"}),
                ("span", {"id": "ebooksProductTitle"})
            ]
            
            for tag, attrs in title_selectors:
                title_tag = soup.find(tag, attrs)
                if title_tag:
                    title = title_tag.get_text().strip()
                    break
            
            if not title:
                parts = url.split('/')
                for part in parts:
                    if part and not any(x in part.lower() for x in ['dp', 'gp', 'product', 'amazon', 'ref=']):
                        title = part.replace('-', ' ').title()
                        break
            
            title = title or "Unknown Amazon Product"

            price = 0.0
            price_selectors = [
                ("span", {"class": "a-price-whole"}),
                ("span", {"id": "priceblock_ourprice"}),
                ("span", {"id": "priceblock_dealprice"}),
                ("span", {"id": "priceblock_saleprice"}),
                ("span", {"class": "a-color-price"}),
                ("span", {"class": "priceToPay"}),
                ("span", {"class": "apexPriceToPay"})
            ]
            
            for tag, attrs in price_selectors:
                price_tag = soup.find(tag, attrs)
                if price_tag:
                    price_str = price_tag.get_text().strip()
                    price_str = re.sub(r'[^\d.]', '', price_str.replace(',', ''))
                    try:
                        if price_str:
                            price = float(price_str)
                            break
                    except ValueError:
                        continue
            
            if price > 0:
                fraction_tag = soup.find("span", {"class": "a-price-fraction"})
                if fraction_tag:
                    fraction_str = fraction_tag.get_text().strip()
                    if fraction_str and fraction_str.isdigit():
                        price += float(fraction_str) / 100

            image_url = "https://via.placeholder.com/300?text=No+Image"
            image_selectors = [
                ("img", {"id": "landingImage"}),
                ("img", {"id": "main-image"}),
                ("img", {"id": "imgBlkFront"}),
                ("img", {"class": "a-dynamic-image"})
            ]
            
            for tag, attrs in image_selectors:
                img_tag = soup.find(tag, attrs)
                if img_tag:
                    if img_tag.get("data-a-dynamic-image"):
                        import json
                        try:
                            img_data = json.loads(img_tag.get("data-a-dynamic-image"))
                            image_url = sorted(img_data.items(), key=lambda x: x[1][0]*x[1][1], reverse=True)[0][0]
                        except:
                            image_url = img_tag.get("src")
                    else:
                        image_url = img_tag.get("src")
                    break
            
            description = ""
            desc_tag = soup.find("div", {"id": "feature-bullets"})
            if desc_tag:
                bullets = desc_tag.find_all("li")
                description = " | ".join([b.get_text().strip() for b in bullets if b.get_text().strip()])
            
            if not description:
                desc_tag = soup.find("div", {"id": "productDescription"})
                if desc_tag:
                    description = desc_tag.get_text().strip()

            product_data = {
                "title": title[:200],
                "price": price,
                "currency": "INR",
                "image_url": image_url,
                "description": description[:500] if description else "No description available",
                "url": url,
                "platform": "amazon",
                "success": True if price > 0 else False
            }
            
            logger.info(f"Scraped Amazon: {title[:50]}... | Price: {price}")
            return product_data
            
        except Exception as e:
            logger.error(f"Error scraping Amazon {url}: {e}")
            return {
                "error": str(e),
                "url": url,
                "platform": "amazon",
                "success": False
            }
    
    def validate_url(self, url: str) -> bool:
        return "amazon" in url.lower() and ("/dp/" in url.lower() or "/gp/" in url.lower())


