"""
Dashboard page - Main overview of user's price tracking
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta


def show_dashboard():
    """Display dashboard page"""
    st.title("📊 Dashboard")
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Products Watching", 5, delta="2 new")
    
    with col2:
        st.metric("Price Alerts", 3, delta=1)
    
    with col3:
        st.metric("Avg. Savings", "₹2,450", delta="↓ 12%")
    
    with col4:
        st.metric("Best Deal Today", "Laptop", delta="₹5,000 drop")
    
    st.divider()
    
    # Price trends section
    st.subheader("📈 Recent Price Trends")
    
    # Sample data
    dates = pd.date_range(end=datetime.now(), periods=7)
    sample_data = {
        "Date": dates,
        "Product 1": [15000, 14800, 14500, 14300, 14200, 14100, 14000],
        "Product 2": [8000, 8200, 8100, 7900, 7800, 7600, 7500],
        "Product 3": [5500, 5600, 5700, 5600, 5500, 5400, 5300]
    }
    
    fig = go.Figure()
    
    for product in ["Product 1", "Product 2", "Product 3"]:
        fig.add_trace(go.Scatter(
            x=sample_data["Date"],
            y=sample_data[product],
            mode='lines+markers',
            name=product
        ))
    
    fig.update_layout(
        title="Price History (7 Days)",
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        hovermode="x unified",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Recent activity
    st.subheader("🔔 Recent Activity")
    
    activity_data = {
        "Product": ["Laptop", "Phone", "Headphones", "Smartwatch"],
        "Price Change": ["-₹5,000", "-₹2,000", "+₹500", "-₹1,000"],
        "Status": ["🔴 Alert!", "🟢 Down", "🔵 Up", "🟢 Down"],
        "Time": ["2 hours ago", "4 hours ago", "6 hours ago", "8 hours ago"]
    }
    
    df_activity = pd.DataFrame(activity_data)
    st.dataframe(df_activity, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Top recommendations
    st.subheader("💡 Recommendations")
    
    rec_col1, rec_col2 = st.columns(2)
    
    with rec_col1:
        st.info("**Laptop** is at its 30-day low! Now is a good time to buy.")
    
    with rec_col2:
        st.warning("**Headphones** price increased. Wait for discount.")


if __name__ == "__main__":
    show_dashboard()
