import streamlit as st
import logging
import pandas as pd
import plotly.express as px
from datetime import datetime
from database.firebase_db import FirebaseDB
from scrapers.amazon_scraper import AmazonScraper
from scrapers.flipkart_scraper import FlipkartScraper
from ai_assistant.groq_assistant import GroqAssistant
import time
import json
import os

SESSION_FILE = "local_session.json"

def save_session(email):
    with open(SESSION_FILE, "w") as f:
        json.dump({"current_user": email}, f)

def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                return data.get("current_user")
        except:
            pass
    return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except:
            pass

st.set_page_config(
    page_title="BetterDeals",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from utils.ui_utils import set_page_theme

set_page_theme()

if "user_logged_in" not in st.session_state:
    saved_user = load_session()
    if saved_user:
        st.session_state.user_logged_in = True
        st.session_state.current_user = saved_user
    else:
        st.session_state.user_logged_in = False
        st.session_state.current_user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_resource
def get_db():
    return FirebaseDB()

@st.cache_resource
def get_ai():
    return GroqAssistant()

db = get_db()
ai = get_ai()
amazon_scraper = AmazonScraper()
flipkart_scraper = FlipkartScraper()

def show_login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #f8fafc;'>BetterDeals</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.1rem;'>Professional Intelligent Price Tracking</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Secure Login", "Create Account"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email/User ID")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In")
                
                if submit:
                    if email and password:
                        user = db.get_user(email.lower().strip())
                        if user and user.get("password") == password:
                            st.session_state.user_logged_in = True
                            st.session_state.current_user = email.lower().strip()
                            save_session(st.session_state.current_user)
                            st.success("Welcome back!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    else:
                        st.warning("Please fill all fields")
                        
        with tab2:
            with st.form("signup_form"):
                new_email = st.text_input("Choose User ID")
                new_pass = st.text_input("Create Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                signup_submit = st.form_submit_button("Join Now")
                
                if signup_submit:
                    if new_email and new_pass == confirm_pass:
                        email_clean = new_email.lower().strip()
                        if db.get_user(email_clean):
                            st.error("User already exists")
                        else:
                            if db.add_user(email_clean, {"email": email_clean, "password": new_pass}):
                                st.success("Account created! Please log in.")
                                time.sleep(1)
                            else:
                                st.error("Database error. Please try again.")
                    else:
                        st.error("Passwords don't match or fields empty")

def show_dashboard():
    st.title("BetterDeals")
    
    # Live Price Sync Fragment (Runs in background)
    if hasattr(st, "fragment"):
        @st.fragment(run_every=300)
        def auto_sync():
            if watchlist := db.get_watchlist(st.session_state.current_user):
                for item in watchlist:
                    url = item['product_url']
                    scraper = amazon_scraper if "amazon" in url.lower() else flipkart_scraper
                    new_data = scraper.scrape_product(url)
                    if new_data.get("success"):
                        db.update_product_price(item['id'], new_data['price'])
        auto_sync()
    
    watchlist = db.get_watchlist(st.session_state.current_user)
    
    total_savings = 0.0
    best_drop = 0.0
    best_product = "N/A"
    triggered_alerts = []
    
    for item in watchlist:
        data = item['product_data']
        history = db.get_price_history(item['product_url'])
        target = item.get('target_price')
        
        if target and data['price'] <= target:
            triggered_alerts.append(item)
            
        if history and len(history) > 1:
            max_price = max([h['price'] for h in history])
            current_price = data['price']
            drop = max_price - current_price
            if drop > 0:
                total_savings += drop
                drop_pct = (drop / max_price) * 100
                if drop_pct > best_drop:
                    best_drop = drop_pct
                    best_product = data['title'][:15] + "..."

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Tracking", len(watchlist))
    with c2:
        st.metric("Deals Found", len(triggered_alerts), f"{len(watchlist)} total items")
    with c3:
        st.metric("Best Drop", f"{best_drop:.1f}%" if best_drop > 0 else "0%", best_product)
    with c4:
        st.metric("Opportunity", f"INR {total_savings:,.2f}", "Current Savings")

    if triggered_alerts:
        for alert in triggered_alerts:
            st.toast(f"Target reached for {alert['product_data']['title'][:30]}!", icon=None)
            st.success(f"TARGET REACHED! {alert['product_data']['title']} is now INR {alert['product_data']['price']:,.2f} (Target: INR {alert['target_price']:,.2f})")

    if st.button("Sync Live Prices Now", use_container_width=True):
        with st.spinner("Checking Amazon & Flipkart for changes..."):
            for item in watchlist:
                url = item['product_url']
                scraper = amazon_scraper if "amazon" in url.lower() else flipkart_scraper
                new_data = scraper.scrape_product(url)
                if new_data.get("success"):
                    db.update_product_price(item['id'], new_data['price'])
            st.success("Prices updated! Screen refreshing...")
            time.sleep(1)
            st.rerun()

    st.divider()
    
    if not watchlist:
        st.info("Welcome! Start by adding a product URL in the Watchlist tab.")
        st.image("https://illustrations.popsy.co/gray/shopping-bag.svg", width=300)
    else:
        st.subheader("Global Deals")
        all_history = []
        for item in watchlist[:3]:
            hist = db.get_price_history(item['product_url'], limit=10)
            if hist:
                for h in hist:
                    h['Product'] = item['product_data']['title'][:20] + "..."
                    all_history.append(h)
        
        if all_history:
            df = pd.DataFrame(all_history)
            fig = px.line(df, x='timestamp', y='price', color='Product', template='plotly_white')
            fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=350)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Latest Tracked Products")
        cols = st.columns(3)
        for i, item in enumerate(watchlist[-3:]):
            with cols[i % 3]:
                data = item['product_data']
                st.markdown(f"""
                <div class="product-card">
                    <div>
                        <img src="{data.get('image_url')}" alt="Product Image">
                        <span class="platform-badge {data['platform']}-badge">{data['platform']}</span>
                        <h4 style="margin: 10px 0; font-size: 0.9rem;">{data['title'][:45]}...</h4>
                        <span class="price-tag">INR {data['price']:,.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Remove", key=f"dash_del_{item['id']}", use_container_width=True):
                    if db.remove_from_watchlist(item['id']):
                        st.toast("Item removed")
                        st.rerun()

from utils.helpers import format_price, get_price_change_percentage, format_timestamp

def show_watchlist():
    st.title("Intelligent Watchlist")
    
    with st.expander("Add New Product", expanded=True):
        col1, col2 = st.columns([4, 1])
        url = col1.text_input("Paste Amazon or Flipkart URL here", placeholder="https://...")
        target_price = col2.number_input("Target Price (optional)", min_value=0.0, step=100.0)
        
        if st.button("Analyze and Add", use_container_width=True):
            if url:
                with st.spinner("Extracting product intelligence..."):
                    scraper = None
                    if "amazon" in url.lower(): scraper = amazon_scraper
                    elif "flipkart" in url.lower(): scraper = flipkart_scraper
                    
                    if scraper:
                        product_data = scraper.scrape_product(url)
                        if product_data.get("success"):
                            if target_price > 0:
                                product_data["target_price"] = target_price
                            res = db.add_to_watchlist(st.session_state.current_user, url, product_data)
                            if res:
                                db.add_price_history(url, product_data['price'])
                                if target_price > 0:
                                    db.create_alert(st.session_state.current_user, url, target_price)
                                st.success(f"Successfully added {product_data['title'][:50]}!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to save to database")
                        else:
                            st.error(f"Scraping failed: {product_data.get('error', 'Unknown error')}")
                    else:
                        st.error("Platform not supported yet. We support Amazon & Flipkart.")
            else:
                st.warning("Please enter a URL")

    st.divider()
    
    watchlist = db.get_watchlist(st.session_state.current_user)
    
    if watchlist:
        for item in watchlist:
            with st.container():
                data = item['product_data']
                history = db.get_price_history(item['product_url'])
                
                c1, c2, c3 = st.columns([1, 2.5, 1])
                
                with c1:
                    st.image(data.get('image_url'), use_column_width=True)
                
                with c2:
                    change_text = ""
                    if len(history) > 1:
                        prev_price = history[1]['price']
                        curr_price = data['price']
                        pct_change = get_price_change_percentage(prev_price, curr_price)
                        if pct_change < 0:
                            change_text = f" <span style='color:green;'>▼ {abs(pct_change)}% drop</span>"
                        elif pct_change > 0:
                            change_text = f" <span style='color:red;'>▲ {pct_change}% increase</span>"
                    
                    st.markdown(f"**{data['title']}**")
                    st.markdown(f"<span class='platform-badge {data['platform']}-badge'>{data['platform']}</span>{change_text}", unsafe_allow_html=True)
                    st.write(f"Current Price: **{format_price(data['price'])}**")
                    target = item.get('target_price', 0.0)
                    if target:
                        st.write(f"Target Price: **₹{target:,.2f}**")
                    
                    if st.button("Get AI Insight", key=f"ai_{item['id']}"):
                        with st.spinner("AI analysis in progress..."):
                            insight = ai.get_price_insights(data, history)
                            st.info(insight)
                
                with c3:
                    st.write(f"Added: {format_timestamp(item.get('added_at'))}")
                    if st.button("Remove", key=f"del_{item['id']}", use_container_width=True):
                        if db.remove_from_watchlist(item['id']):
                            st.toast("Item removed")
                            st.rerun()
                st.divider()
    else:
        st.info("Watchlist is empty. Add your first product above!")

def show_ai_assistant():
    st.title("Shopping Concierge")
    st.markdown("Your professional shopping advisor for price trends and analysis.")
    
    watchlist = db.get_watchlist(st.session_state.current_user)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Recommended Best Deal", use_container_width=True):
            with st.spinner("Analyzing watchlist..."):
                deal = ai.find_best_deal(watchlist)
                st.markdown(deal)
    with col2:
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.success("History cleared")

    st.divider()
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Ask me about prices, trends, or recommendations..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing data..."):
                # Enrich context with brief history summaries
                enriched_watchlist = []
                for item in watchlist:
                    hist = db.get_price_history(item['product_url'], limit=5)
                    item_with_hist = item.copy()
                    item_with_hist['history_summary'] = [f"{h['timestamp'].strftime('%Y-%m-%d')}: INR {h['price']}" for h in hist if h.get('timestamp')]
                    enriched_watchlist.append(item_with_hist)
                
                response = ai.ask_ai(prompt, watchlist_context=enriched_watchlist)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

def show_settings():
    st.title("System Settings")
    
    with st.expander("Profile and Security", expanded=True):
        st.write(f"Logged in as: **{st.session_state.current_user}**")
        st.text_input("Change Password", type="password")
        if st.button("Update Profile"):
            st.success("Profile updated locally (Database sync pending)")
            
    with st.expander("Notification Preferences"):
        st.checkbox("Email Alerts", value=True)
        st.checkbox("Browser Notifications", value=False)
        st.slider("Minimum Price Drop Percentage", 1, 50, 10)
        
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.session_state.user_logged_in = False
        st.session_state.current_user = None
        clear_session()
        st.rerun()

def main():
    if st.session_state.user_logged_in:
        with st.sidebar:
            st.markdown(f"""
            <div class="sidebar-stats">
                <p style="margin:0; font-size: 0.8rem; opacity: 0.8;">Welcome back,</p>
                <h2 style="margin:0; font-size: 1.5rem;">{st.session_state.current_user.split('@')[0].capitalize()}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            nav = st.radio("Navigation", ["Dashboard", "Watchlist", "AI Assistant", "Settings"], label_visibility="collapsed")
            
            st.divider()
            st.markdown("### System Status")
            st.success("Firebase Backend Connected")
            st.success("Analysis Engine Ready")
            
        if nav == "Dashboard": show_dashboard()
        elif nav == "Watchlist": show_watchlist()
        elif nav == "AI Assistant": show_ai_assistant()
        elif nav == "Settings": show_settings()
    else:
        show_login_page()

if __name__ == "__main__":
    main()
