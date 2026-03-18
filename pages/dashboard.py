"""
Dashboard page - Main overview of user's price tracking (Connected to Firebase)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from database.firebase_db import FirebaseDB

def init_db():
    if "db" not in st.session_state:
        try:
            st.session_state.db = FirebaseDB()
        except Exception as e:
            st.error(f"Failed to connect to Firebase: {e}")
            st.stop()

def show_dashboard():
    """Display dashboard page"""
    init_db()
    st.title("📊 Dashboard")
    
    if not st.session_state.get("user_logged_in"):
        st.warning("Please login first.")
        return

    db = st.session_state.db
    user_id = st.session_state.current_user
    
    watchlist = db.get_watchlist(user_id)
    alerts = db.get_user_alerts(user_id)
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Products Watching", len(watchlist))
    
    with col2:
        st.metric("Price Alerts", len(alerts))
    
    with col3:
        st.metric("Avg. Savings", "₹0")
    
    with col4:
        st.metric("Best Deal Today", "N/A")
    
    st.divider()
    
    # Recent activity
    st.subheader("🔔 Recent Activity")
    
    if watchlist:
        activity_data = []
        for item in watchlist[:5]:
            product_data = item.get("product_data", {})
            added_at = item.get("added_at")
            time_str = added_at.strftime("%Y-%m-%d") if hasattr(added_at, "strftime") else "Recently"
            
            activity_data.append({
                "Product": product_data.get("title", "New Product"),
                "Price": f"₹{product_data.get('price', 0.0):,.2f}",
                "Status": "🟢 Monitoring",
                "Time": time_str
            })
        
        df_activity = pd.DataFrame(activity_data)
        st.dataframe(df_activity, use_container_width=True, hide_index=True)
    else:
        st.info("No activity found. Start adding products to see them here!")

if __name__ == "__main__":
    show_dashboard()
