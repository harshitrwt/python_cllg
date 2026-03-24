"""
Watchlist page - Manage products on watchlist (Connected to Firebase)
"""

import streamlit as st
import pandas as pd
from database.firebase_db import FirebaseDB
from scrapers.amazon_scraper import AmazonScraper
from scrapers.flipkart_scraper import FlipkartScraper
from utils.ui_utils import set_page_theme

def init_db():
    if "db" not in st.session_state:
        try:
            st.session_state.db = FirebaseDB()
        except Exception as e:
            st.error(f"Failed to connect to Firebase: {e}")
            st.stop()
    
    if "amazon_scraper" not in st.session_state:
        st.session_state.amazon_scraper = AmazonScraper()
    if "flipkart_scraper" not in st.session_state:
        st.session_state.flipkart_scraper = FlipkartScraper()

def show_watchlist():
    set_page_theme()
    init_db()
    st.title("📌 My Watchlist")
    
    if not st.session_state.get("user_logged_in"):
        st.warning("Please login first.")
        return

    db = st.session_state.db
    user_id = st.session_state.current_user

    # --- Add New Product ---
    st.subheader("➕ Add New Product")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        product_url = st.text_input("Enter product URL", placeholder="https://amazon.com/dp/...")
    with col2:
        check_button = st.button("Check Product", use_container_width=True)

    if check_button or st.session_state.get("adding_product"):
        if product_url:
            platform = "amazon" if "amazon" in product_url else "flipkart" if "flipkart" in product_url else None
            
            if platform:
                # Scrape if needed
                if st.session_state.get("preview_url") != product_url:
                    with st.spinner(f"Scraping {platform.capitalize()}..."):
                        if platform == "amazon":
                            data = st.session_state.amazon_scraper.scrape_product(product_url)
                        else:
                            data = st.session_state.flipkart_scraper.scrape_product(product_url)
                        
                        # Fallback for name from URL if scraper failed
                        if "error" in data or not data.get("title") or data.get("title") == "Unknown Product":
                            parts = product_url.split('/')
                            fallback_title = "Product from " + platform.capitalize()
                            for part in parts:
                                if len(part) > 10 and '-' in part:
                                    fallback_title = part.replace('-', ' ').title()
                                    break
                            data["title"] = data.get("title") or fallback_title
                        
                        st.session_state.scraped_data = data
                        st.session_state.preview_url = product_url
                        st.session_state.adding_product = True
                
                # Show Preview & Set Target
                data = st.session_state.get("scraped_data", {})
                st.divider()
                p_col1, p_col2 = st.columns([1, 2])
                
                with p_col1:
                    st.image(data.get("image_url", "https://via.placeholder.com/150"), width=150)
                
                with p_col2:
                    final_title = st.text_input("Product Name", value=data.get("title", ""))
                    current_price = st.number_input("Current Price (₹)", value=float(data.get("price", 1.0)))
                    target_price = st.number_input("Set your Target Price (₹)", min_value=1.0, value=current_price * 1.0 if current_price > 0 else 1.0)
                    
                    if current_price > 0 and target_price < current_price * 0.5:
                        st.warning("⚠️ Target is >50% lower than current price. Might take a long time!")
                    
                    if st.button("🚀 Confirm & Add to Watchlist", type="primary"):
                        if final_title and target_price > 0:
                            save_data = data.copy()
                            save_data["title"] = final_title
                            save_data["price"] = current_price
                            save_data["target_price"] = target_price
                            if db.add_to_watchlist(user_id, product_url, save_data):
                                st.success(f"✅ {final_title} added!")
                                st.session_state.adding_product = False
                                st.session_state.scraped_data = None
                                st.session_state.preview_url = None
                                st.rerun()
                        else:
                            st.error("Please ensure Name and Target Price are set.")
            else:
                st.error("Please enter a valid Amazon or Flipkart URL")
        else:
            st.error("Please enter a URL")

    st.divider()
    # --- Watchlist Display ---
    st.subheader("📦 Your Watched Products")
    watchlist = db.get_watchlist(user_id)
    
    if watchlist:
        for item in watchlist:
            product_data = item.get("product_data", {})
            doc_id = item.get("id")
            
            with st.expander(f"**{product_data.get('title', 'Unknown')[:60]}...**"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image(product_data.get("image_url", "https://via.placeholder.com/150"), width=150)
                
                with col2:
                    st.write(f"Platform: **{product_data.get('platform', 'Unknown').capitalize()}**")
                    st.write(f"Current Price: **₹{product_data.get('price', 0.0):,.2f}**")
                    st.write(f"Target Price: **₹{item.get('target_price', 0.0) or 0.0:,.2f}**")
                    
                    added_at = item.get("added_at")
                    date_str = added_at.strftime("%Y-%m-%d") if hasattr(added_at, "strftime") else "N/A"
                    st.button("❌ Remove", key=f"remove_p_{doc_id}", on_click=lambda id=doc_id: db.remove_from_watchlist(id))
                    st.write(f"[Open Product Page]({item.get('product_url')})")
    else:
        st.info("Watchlist is empty.")

if __name__ == "__main__":
    show_watchlist()
