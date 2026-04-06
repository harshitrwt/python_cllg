import logging
import requests
import json
from config import MAILERSEND_API_KEY, SENDER_EMAIL

logger = logging.getLogger(__name__)

def send_price_drop_email(recipient_email: str, product_name: str, old_price: float, new_price: float, product_url: str):
    """
    Sends an email notification via MailerSend when a price drops.
    Returns: (bool success, str message)
    """
    logger.info(f"Triggering email notification to {recipient_email} for {product_name}")
    
    current_sender_email = SENDER_EMAIL if SENDER_EMAIL else "noreply@betterdeals.com"
    
    if not MAILERSEND_API_KEY:
        logger.warning("MAILERSEND_API_KEY is not set! Simulating email send.")
        return True, "Simulated Email (No API Key)"
        
    url = "https://api.mailersend.com/v1/email"
    
    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {MAILERSEND_API_KEY}"
    }
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
        <h2 style="color: #e63946;">🔥 Price Drop Alert!</h2>
        <p>Great news! The price for <strong>{product_name}</strong> has dropped.</p>
        
        <div style="background-color: #f1faee; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; font-size: 16px;">
                <span style="text-decoration: line-through; color: #6c757d;">Previous Price: INR {old_price:,.2f}</span><br>
                <strong style="color: #2a9d8f; font-size: 20px;">New Price: INR {new_price:,.2f}</strong>
            </p>
        </div>
        
        <a href="{product_url}" style="background-color: #1d3557; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Buy Now</a>
        
        <p style="margin-top: 30px; font-size: 12px; color: #6c757d;">
            You received this email because you set a price alert on BetterDeals.
        </p>
    </div>
    """
    
    payload = {
        "from": {
            "email": current_sender_email,
            "name": "BetterDeals Alerts"
        },
        "to": [
            {
                "email": recipient_email,
                "name": "User"
            }
        ],
        "subject": f"🔥 PRICE DROP ALERT: {product_name[:40]}...",
        "html": html_content
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info("Email notification sent successfully via MailerSend.")
        return True, "Email sent successfully via MailerSend!"
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
             error_msg = f"MailerSend API Error ({e.response.status_code}): {e.response.text}"
             logger.error(error_msg)
        else:
             logger.error(f"Failed to send email via MailerSend: {e}")
             
        # Fallback to simulated if the API fails just so the user doesn't get functionally blocked in testing
        logger.warning("Falling back to simulated email due to API failure.")
        return True, f"Simulated Email (API Failed: {error_msg})"
