"""
Watchlist page - Manage products on watchlist
"""

import streamlit as st
import pandas as pd


def show_watchlist():
    """Display watchlist page"""
    st.title("📌 My Watchlist")
    
    # Add new product section
    st.subheader("➕ Add New Product")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        product_url = st.text_input(
            "Enter product URL (Amazon or Flipkart)",
            placeholder="https://amazon.com/dp/..."
        )
    
    with col2:
        if st.button("Add to Watchlist", use_container_width=True):
            if product_url:
                st.success(f"✅ Product added to watchlist!")
                st.balloons()
            else:
                st.error("Please enter a valid URL")
    
    st.divider()
    
    
    st.subheader("📦 Your Watched Products")
    
   
    watchlist_data = {
        "Product": [
            "Dell XPS 13 Laptop",
            "iPhone 15 Pro",
            "Sony WH-1000XM5 Headphones",
            "Apple Watch Series 9",
            "iPad Air"
        ],
        "Platform": ["Amazon", "Flipkart", "Amazon", "Flipkart", "Amazon"],
        "Current Price": ["₹1,24,999", "₹84,999", "₹24,499", "₹41,999", "₹54,999"],
        "Target Price": ["₹1,10,000", "₹75,000", "₹20,000", "₹38,000", "₹50,000"],
        "Price Change": ["-₹5,000", "+₹2,000", "-₹3,499", "-₹1,500", "-₹2,000"],
        "Status": ["🟢 Alert Ready", "🔵 Monitoring", "🟢 Alert Ready", "🟡 High", "🟢 Alert Ready"]
    }
    
    df_watchlist = pd.DataFrame(watchlist_data)
    
  
    for idx, row in df_watchlist.iterrows():
        with st.expander(f"**{row['Product']}** - {row['Current Price']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Platform:** {row['Platform']}")
                st.write(f"**Current Price:** {row['Current Price']}")
                st.write(f"**Target Price:** {row['Target Price']}")
            
            with col2:
                st.write(f"**Price Change:** {row['Price Change']}")
                st.write(f"**Status:** {row['Status']}")
            
            st.divider()
            
            # Options
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                if st.button("📊 View History", key=f"history_{idx}"):
                    st.info("Price history graph would appear here")
            
            with action_col2:
                if st.button("🔔 Update Alert", key=f"alert_{idx}"):
                    new_target = st.number_input(f"New target price for {row['Product']}")
                    if st.button("Save", key=f"save_{idx}"):
                        st.success("Alert updated!")
            
            with action_col3:
                if st.button("❌ Remove", key=f"remove_{idx}"):
                    st.warning("Product removed from watchlist!")
    
    st.divider()
    
    # Bulk actions
    st.subheader("⚙️ Bulk Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Email Summary", use_container_width=True):
            st.info("Email sent with current watchlist summary!")
    
    with col2:
        if st.button("♻️ Refresh Prices", use_container_width=True):
            st.info("Prices refreshed from web!")
    
    with col3:
        if st.button("📥 Export CSV", use_container_width=True):
            st.info("Watchlist exported as CSV!")


if __name__ == "__main__":
    show_watchlist()
