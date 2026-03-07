import re
from urllib.parse import urlparse
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate if URL is from supported e-commerce platforms
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, platform)
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        if "amazon.com" in domain or "amazon.in" in domain:
            return True, "amazon"
        elif "flipkart.com" in domain:
            return True, "flipkart"
        else:
            return False, None
    except Exception as e:
        logger.error(f"Error validating URL: {e}")
        return False, None


def extract_product_info(html: str, platform: str) -> dict:
    """
    Extract product information from HTML
    
    Args:
        html: HTML content
        platform: e-commerce platform
        
    Returns:
        Dictionary with product information
    """
    
    return {
        "title": "Product Title",
        "price": 0.0,
        "rating": 0.0,
        "in_stock": True
    }


def format_price(price: float, currency: str = "INR") -> str:
    """
    Format price for display
    
    Args:
        price: Price value
        currency: Currency code
        
    Returns:
        Formatted price string
    """
    currency_symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£"
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol} {price:,.2f}"


def get_price_change_percentage(old_price: float, new_price: float) -> float:
    """
    Calculate percentage change in price
    
    Args:
        old_price: Previous price
        new_price: Current price
        
    Returns:
        Percentage change (positive = increase, negative = decrease)
    """
    if old_price == 0:
        return 0
    
    change = ((new_price - old_price) / old_price) * 100
    return round(change, 2)


def is_price_dropping(prices: list) -> bool:
    """
    Check if price trend is dropping
    
    Args:
        prices: List of prices in chronological order
        
    Returns:
        True if trend is downward
    """
    if len(prices) < 2:
        return False
    
    return prices[-1] < prices[0]


def get_average_price(prices: list) -> float:
    """Calculate average of prices"""
    if not prices:
        return 0
    return sum(prices) / len(prices)


def format_timestamp(timestamp) -> str:
    """Format timestamp for display"""
    try:
        if hasattr(timestamp, 'strftime'):
            return timestamp.strftime("%d %b %Y, %I:%M %p")
        return str(timestamp)
    except Exception as e:
        logger.error(f"Error formatting timestamp: {e}")
        return str(timestamp)
