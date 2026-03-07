"""
Scrapers module for e-commerce price tracking
"""

from .amazon_scraper import AmazonScraper
from .flipkart_scraper import FlipkartScraper

__all__ = ["AmazonScraper", "FlipkartScraper"]
