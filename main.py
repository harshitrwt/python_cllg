import streamlit as st
import logging
import pandas as pd
import plotly.express as px
from datetime import datetime
from database.firebase_db import FirebaseDB
from scrapers.amazon_scraper import AmazonScraper
from scrapers.myntra_scraper import MyntraScraper
from ai_assistant.groq_assistant import GroqAssistant
from utils.notifications import send_price_drop_email
from utils.helpers import format_price, get_price_change_percentage, format_timestamp
import time
import json
import os
import random
from config import GROQ_API_KEY, GROQ_MODEL
from ml_model.predictor import FashionPredictor

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
    page_icon="🛍️",
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
myntra_scraper = MyntraScraper()

@st.cache_resource
def get_cnn():
    return FashionPredictor()

cnn_predictor = get_cnn()

if st.session_state.user_logged_in and "current_name" not in st.session_state:
    user_data = db.get_user(st.session_state.current_user)
    st.session_state.current_name = user_data.get("name", st.session_state.current_user.split('@')[0].capitalize()) if user_data else st.session_state.current_user.split('@')[0].capitalize()

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
                            st.session_state.current_name = user.get("name", st.session_state.current_user.split('@')[0].capitalize())
                            save_session(st.session_state.current_user)
                            st.success("Welcome back!")
                            db.log_action("User Login", f"User logged in: {st.session_state.current_user}")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    else:
                        st.warning("Please fill all fields")
                        
        with tab2:
            with st.form("signup_form"):
                new_name = st.text_input("Your Name")
                new_email = st.text_input("Choose User ID (Email)")
                new_pass = st.text_input("Create Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                signup_submit = st.form_submit_button("Join Now")
                
                if signup_submit:
                    if new_name and new_email and new_pass == confirm_pass:
                        email_clean = new_email.lower().strip()
                        if db.get_user(email_clean):
                            st.error("User already exists")
                        else:
                            if db.add_user(email_clean, {"email": email_clean, "name": new_name.strip(), "password": new_pass}):
                                st.success("Account created! Please log in.")
                                time.sleep(1)
                            else:
                                st.error("Database error. Please try again.")
                    else:
                        st.error("Passwords don't match or fields empty")

@st.dialog("Product Details", width="large")
def show_product_details(item, history):
    data = item['product_data']
    st.subheader(data.get('title', 'Unknown Product'))
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(data.get('image_url'), width=True)
        st.markdown(f"**Current Price:** ₹{data.get('price', 0):,.2f}")
        if item.get('target_price'):
            st.markdown(f"**Target Price:** ₹{item.get('target_price'):,.2f}")
            diff = item.get('target_price') - data.get('price')
            if diff >= 0:
                st.markdown(f"✅ **Below Target by ₹{diff:,.2f}**")
            else:
                st.markdown(f"❌ **Above Target by ₹{abs(diff):,.2f}**")
        st.markdown(f"[Buy on {data.get('platform', 'Store').capitalize()}]({item.get('product_url')})")
        
    with col2:
        if history:
            prices = [h['price'] for h in history]
            st.markdown(f"**Highest Price:** ₹{max(prices):,.2f}")
            st.markdown(f"**Lowest Price:** ₹{min(prices):,.2f}")
            st.markdown(f"**Average Price:** ₹{sum(prices)/len(prices):,.2f}")
            
            df = pd.DataFrame(history)
            fig = px.line(df, x='timestamp', y='price', title='Price History Timeline', template='plotly_dark', markers=True)
            fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No historical data available yet.")


def show_dashboard():
    st.title("User Dashboard")
    
    # Live Price Sync Fragment (Runs in background)
    if hasattr(st, "fragment"):
        @st.fragment(run_every=300)
        def auto_sync():
            if "current_user" in st.session_state and st.session_state.current_user:
                if watchlist := db.get_watchlist(st.session_state.current_user):
                    for item in watchlist:
                        url = item['product_url']
                        scraper = amazon_scraper if "amazon" in url.lower() else myntra_scraper
                        new_data = scraper.scrape_product(url)
                        db.log_action("Auto Sync", f"Checking {url}")
                        if new_data.get("success"):
                            old_price = item['product_data'].get('price', 0)
                            new_price = new_data['price']
                            if old_price != new_price:
                                db.update_product_price(item['id'], new_price)
                                db.log_action("Price Update", f"{new_data['title'][:30]}... price changed {old_price} -> {new_price}")
                                target = item.get('target_price')
                                if target and new_price <= target and old_price > target:
                                    success, msg = send_price_drop_email(st.session_state.current_user, new_data['title'], old_price, new_price, url)
                                    db.log_action("Notification Triggered", f"Email sent for {new_data['title'][:30]} - {msg}")
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
        st.metric("Products Tracked", len(watchlist))
    with c2:
        st.metric("Target Reached", len(triggered_alerts))
    with c3:
        st.metric("Best Drop", f"{best_drop:.1f}%" if best_drop > 0 else "0%", best_product)
    with c4:
        st.metric("Est. Savings", f"INR {total_savings:,.2f}")

    # ─── CNN Category Distribution ───────────────────────────────
    if cnn_predictor.is_ready() and watchlist:
        st.divider()
        st.subheader("🧠 CNN Product Categories")
        categories = []
        for item in watchlist:
            cat = item.get('product_data', {}).get('cnn_category')
            if cat:
                categories.append(cat)
        if categories:
            cat_df = pd.DataFrame({"Category": categories})
            cat_counts = cat_df["Category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            fig = px.pie(cat_counts, names="Category", values="Count",
                         title="Watchlist — CNN Classified Categories",
                         template="plotly_dark",
                         color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("CNN categories will appear here once products are classified. Try the Visual Search page!")

    if triggered_alerts:
        for alert in triggered_alerts:
            st.success(f"🔥 TARGET MET! {alert['product_data']['title'][:40]}... is now INR {alert['product_data']['price']:,.2f}")

    st.divider()
    
    if not watchlist:
        st.info("Start adding products to your watch list to see metrics.")
    else:
        st.subheader("Interactive Price Tracking")
        
        # Dashboard cards view instead of simple array
        cols = st.columns(3)
        for i, item in enumerate(watchlist):
            with cols[i % 3]:
                data = item['product_data']
                history = db.get_price_history(item['product_url'])
                target = item.get('target_price')
                curr_price = data['price']
                
                status_color = "gray"
                status_text = "Tracking"
                badge = ""
                
                if history and len(history) > 1:
                    if curr_price < history[-1]['price']:
                        badge = "📉 Price Drop"
                    if curr_price == min([h['price'] for h in history]):
                        badge = "🔥 Lowest in 30 Days"
                        
                if target:
                    diff_pct = abs((curr_price - target) / target) * 100
                    if curr_price <= target:
                        status_color = "#22c55e" # Green
                        status_text = "✅ Target Reached"
                    elif diff_pct <= 5:
                        status_color = "#eab308" # Orange
                        status_text = "⏳ Near Target (Within 5%)"
                    else:
                        status_color = "#ef4444" # Red
                        status_text = f"↗️ Above Target (+{diff_pct:.1f}%)"
                        
                html_content = f"""<div style="background: #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #334155; overflow: hidden;">
<div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
<span style="font-size: 0.8rem; background: #3b82f6; padding: 2px 6px; border-radius: 4px;">{data['platform'].capitalize()}</span>
{f'<span style="font-size: 0.8rem; background: #eab308; color: black; padding: 2px 6px; border-radius: 4px;">{badge}</span>' if badge else ''}
</div>
<div style="height: 120px; overflow: hidden; display: flex; align-items: center; justify-content: center; background: white; border-radius: 6px;">
<img src="{data.get('image_url', '')}" style="max-height: 100%; max-width: 100%; object-fit: contain;">
</div>
<h5 style="margin: 10px 0; font-size: 1rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{data['title']}">{data['title']}</h5>
<div style="display: flex; gap: 10px; align-items: baseline;">
<h3 style="margin: 0; color: #f8fafc;">₹{curr_price:,.2f}</h3>
{f'<span style="font-size: 0.8rem; color: #94a3b8;">Target: ₹{target:,.2f}</span>' if target else ''}
</div>
<p style="color: {status_color}; font-size: 0.85rem; margin-top: 5px; font-weight: bold;">{status_text}</p>
</div>"""
                st.markdown(html_content, unsafe_allow_html=True)
                
                # Mini chart
                if history:
                    df = pd.DataFrame(history)
                    if len(df) > 1:
                        fig = px.line(df, x='timestamp', y='price', template='plotly_dark')
                        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=80, xaxis_visible=False, yaxis_visible=False)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                card_cols = st.columns([1,1])
                with card_cols[0]:
                    if st.button("Details", key=f"details_{item['id']}", use_container_width=True):
                        show_product_details(item, history)
                with card_cols[1]:
                    if st.button("Remove", key=f"dash_del_{item['id']}", use_container_width=True):
                        if db.remove_from_watchlist(item['id']):
                            st.toast("Item removed")
                            st.rerun()

def show_watchlist():
    st.title("Add & Manage Products")
    
    with st.expander("Add New Product", expanded=True):
        col1, col2 = st.columns([4, 1])
        url = col1.text_input("Paste Amazon or Myntra URL here", placeholder="https://...")
        target_price = col2.number_input("Target Price (optional)", min_value=0.0, step=100.0)
        
        if st.button("Analyze and Add", use_container_width=True):
            if url:
                with st.spinner("Extracting product intelligence..."):
                    scraper = None
                    if "amazon" in url.lower(): scraper = amazon_scraper
                    elif "myntra" in url.lower(): scraper = myntra_scraper
                    
                    if scraper:
                        product_data = scraper.scrape_product(url)
                        if product_data.get("success"):
                            if target_price > 0:
                                product_data["target_price"] = target_price
                            
                            # ─── CNN Auto-Classification ─────────────
                            if cnn_predictor.is_ready() and product_data.get('image_url'):
                                with st.spinner("🧠 CNN classifying product..."):
                                    cnn_result = cnn_predictor.predict_from_url(product_data['image_url'])
                                    if cnn_result.get('success'):
                                        product_data['cnn_category'] = cnn_result['top_class']
                                        product_data['cnn_confidence'] = round(cnn_result['confidence'] * 100, 1)
                                        st.info(f"🏷️ CNN classified as: **{cnn_result['top_class']}** ({product_data['cnn_confidence']}% confidence)")
                            
                            res = db.add_to_watchlist(st.session_state.current_user, url, product_data)
                            if res:
                                db.add_price_history(url, product_data['price'])
                                if target_price > 0:
                                    db.create_alert(st.session_state.current_user, url, target_price)
                                db.log_action("Add Product", f"Added {product_data['title'][:30]}...")
                                st.success(f"Successfully added {product_data['title'][:50]}!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to save to database")
                        else:
                            st.error(f"Scraping failed: {product_data.get('error', 'Unknown error')}")
                    else:
                        st.error("Platform not supported yet. We support Amazon & Myntra.")
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
                    st.image(data.get('image_url'), width=True)
                
                with c2:
                    change_text = ""
                    if len(history) > 1:
                        prev_price = history[1]['price']
                        curr_price = data['price']
                        pct_change = get_price_change_percentage(prev_price, curr_price)
                        if pct_change < 0:
                            change_text = f" <span style='color:#22c55e;'>▼ {abs(pct_change)}% drop</span>"
                        elif pct_change > 0:
                            change_text = f" <span style='color:#ef4444;'>▲ {pct_change}% increase</span>"
                    
                    st.markdown(f"**{data['title']}**")
                    st.markdown(f"<span class='platform-badge {data['platform']}-badge'>{data['platform']}</span>{change_text}", unsafe_allow_html=True)
                    st.write(f"Current Price: **{format_price(data['price'])}**")
                    target = item.get('target_price', 0.0)
                    if target:
                        st.write(f"Target Price: **₹{target:,.2f}**")
                    
                    if st.button("View Insights", key=f"ai_{item['id']}"):
                        with st.spinner("AI analysis in progress..."):
                            insight = ai.get_price_insights(data, history)
                            st.info(insight)
                
                with c3:
                    st.write(f"Added: {format_timestamp(item.get('added_at'))}")
                    if st.button("View Full Details", key=f"view_{item['id']}", use_container_width=True):
                        show_product_details(item, history)
                    if st.button("Remove", key=f"del_{item['id']}", use_container_width=True):
                        if db.remove_from_watchlist(item['id']):
                            db.log_action("Remove Product", f"Removed {item['id']}")
                            st.toast("Item removed")
                            st.rerun()
                st.divider()
    else:
        st.info("Watchlist is empty. Add your first product above!")

def show_developer_panel():
    st.title("Developer & Testing Tools")
    
    st.markdown("### 1. Mock/Test Tracking System")
    st.info("Use this section to trigger manual price drops when testing the notification and status system, without waiting for Amazon/Flipkart to actually drop the price.")
    
    watchlist = db.get_watchlist(st.session_state.current_user)
    if not watchlist:
        st.warning("No items in watchlist. Please add an item first.")
    else:
        test_item = st.selectbox("Select Product to Manipulate", options=[(i['id'], i['product_data']['title']) for i in watchlist], format_func=lambda x: x[1][:50] + "...")
        item_id = test_item[0]
        selected_item = next(i for i in watchlist if i['id'] == item_id)
        
        current_price = selected_item['product_data']['price']
        st.write(f"**Current Price:** ₹{current_price:,.2f}")
        
        new_override_price = st.number_input("Override Price", min_value=0.0, value=float(current_price * 0.9))
        
        if st.button("Force Price Drop & Run Sync"):
            db.log_action("Test Action", f"Forced price change for {item_id} to {new_override_price}")
            db.update_product_price(item_id, new_override_price)
            
            # Simulate auto_sync behavior
            old_price = current_price
            target = selected_item.get('target_price')
            
            if target and new_override_price <= target and old_price > target:
                success, msg = send_price_drop_email(st.session_state.current_user, selected_item['product_data']['title'], old_price, new_override_price, selected_item['product_url'])
                if success:
                    st.success(f"✅ Email notification triggered! Status: {msg}")
                    db.log_action("Notification Triggered", f"Mock email sent for {selected_item['product_data']['title'][:30]}")
            elif not target:
                st.warning("⚠️ **No notification sent.** You never set a 'Target Price' for this product when adding it to your watchlist! The system doesn't know when to alert you.")
            elif new_override_price > target:
                st.warning(f"⚠️ **No notification sent.** The mock price (₹{new_override_price:,.2f}) is still HIGHER than your Target Price (₹{target:,.2f}).")
            elif old_price <= target:
                st.info(f"ℹ️ **No notification sent.** The previous price (₹{old_price:,.2f}) was ALREADY below the target price. Notifications only fire when a price crosses the threshold.")
            
            st.success("Price overwritten successfully! Check dashboard to see visual updates.")
            time.sleep(1)
            st.rerun()
            
    st.divider()
    st.markdown("### 2. System Logs")
    if st.button("Refresh Logs"):
        st.rerun()
        
    logs = db.get_system_logs(limit=50)
    if logs:
        # Convert list of dicts to dataframe for nice view
        # We need to format the datetime objects properly for display
        formatted_logs = []
        for l in logs:
            l_copy = l.copy()
            if 'timestamp' in l_copy and hasattr(l_copy['timestamp'], 'strftime'):
                l_copy['timestamp'] = l_copy['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            formatted_logs.append(l_copy)
        
        log_df = pd.DataFrame(formatted_logs)
        st.dataframe(log_df, use_container_width=True)
    else:
        st.write("No system logs found.")
    
    # ─── CNN Model Metrics ────────────────────────────────────────
    st.divider()
    st.markdown("### 3. CNN Model Metrics")
    if cnn_predictor.is_ready():
        summary = cnn_predictor.get_model_summary()
        if summary:
            c1, c2, c3 = st.columns(3)
            c1.metric("Classes", summary['num_classes'])
            c2.metric("Parameters", f"{summary['total_params']:,}")
            c3.metric("Model Size", f"{summary['model_size_mb']} MB")
            st.write(f"**Classes:** {', '.join(summary['classes'])}")
        
        history = cnn_predictor.get_training_history()
        if history:
            st.markdown("#### Training History")
            col1, col2 = st.columns(2)
            with col1:
                hist_df = pd.DataFrame({
                    "Epoch": list(range(1, len(history.get('accuracy', [])) + 1)),
                    "Train": history.get('accuracy', []),
                    "Validation": history.get('val_accuracy', [])
                })
                fig = px.line(hist_df, x="Epoch", y=["Train", "Validation"],
                              title="Accuracy", template="plotly_dark", markers=True)
                fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=250)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                loss_df = pd.DataFrame({
                    "Epoch": list(range(1, len(history.get('loss', [])) + 1)),
                    "Train": history.get('loss', []),
                    "Validation": history.get('val_loss', [])
                })
                fig = px.line(loss_df, x="Epoch", y=["Train", "Validation"],
                              title="Loss", template="plotly_dark", markers=True)
                fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=250)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("CNN model not trained yet. Run: `python -m ml_model.train_model`")

def show_visual_search():
    """Visual Search page — upload an image and classify it with CNN."""
    st.title("Visual Search (CNN)")
    st.markdown("Upload any fashion product image and our **MobileNetV2 CNN** will identify the product type, find similar items in your watchlist, and give you **smart price insights** for that category.")
    
    if not cnn_predictor.is_ready():
        st.error("CNN model not available. Please train the model first:")
        st.code("python -m ml_model.train_model", language="bash")
        return
    
    summary = cnn_predictor.get_model_summary()
    if summary:
        st.markdown(f"""<div style="background: #1e293b; padding: 12px 18px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 20px;">
        <span style="color: #22c55e; font-weight: bold;">Model Active</span>&nbsp;&nbsp;|&nbsp;&nbsp;
        <span style="color: #94a3b8;">MobileNetV2</span>&nbsp;&nbsp;|&nbsp;&nbsp;
        <span style="color: #94a3b8;">{summary['num_classes']} classes</span>&nbsp;&nbsp;|&nbsp;&nbsp;
        <span style="color: #94a3b8;">{summary['model_size_mb']} MB</span>
        </div>""", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Upload Image")
        uploaded_file = st.file_uploader(
            "Choose a fashion product image",
            type=["jpg", "jpeg", "png", "webp"],
            help="Upload a clear image of a fashion product (clothing, shoes, etc.)"
        )
        
        image_url = st.text_input(
            "Or paste an image URL",
            placeholder="https://example.com/product-image.jpg"
        )
    
    result = None
    display_image = None
    
    if uploaded_file is not None:
        from PIL import Image as PILImage
        display_image = PILImage.open(uploaded_file)
        with st.spinner("CNN analyzing image..."):
            uploaded_file.seek(0)
            result = cnn_predictor.predict_from_file(uploaded_file)
    elif image_url:
        if st.button("Classify from URL", use_container_width=True):
            with st.spinner("Downloading and analyzing..."):
                result = cnn_predictor.predict_from_url(image_url)
                if result.get('success'):
                    try:
                        import requests as req
                        from PIL import Image as PILImage
                        from io import BytesIO
                        resp = req.get(image_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                        display_image = PILImage.open(BytesIO(resp.content))
                    except:
                        pass
    
    with col2:
        if display_image:
            st.markdown("### Input Image")
            st.image(display_image, width=True)
    
    if result:
        st.divider()
        if result.get("success"):
            top = result['predictions'][0]
            detected_category = top['class']
            confidence = top['confidence']
        
            st.markdown("### Classification Results")
            
            st.markdown(f"""<div style="background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%); 
                padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 20px; 
                border: 1px solid #3b82f6;">
                <h2 style="margin:0; color: #f8fafc;">{detected_category}</h2>
                <p style="margin: 8px 0 0 0; color: #60a5fa; font-size: 1.4rem; font-weight: bold;">
                    {confidence*100:.1f}% Confidence
                </p>
            </div>""", unsafe_allow_html=True)
            
            # Top predictions with progress bars
            st.markdown("#### All Predictions")
            for pred in result['predictions']:
                col_a, col_b, col_c = st.columns([2, 4, 1])
                with col_a:
                    st.write(f"**{pred['class']}**")
                with col_b:
                    st.progress(pred['confidence'])
                with col_c:
                    st.write(f"{pred['confidence']*100:.1f}%")
            
            # ─── Section 2: Category Price Intelligence ─────────────
            st.divider()
            st.markdown(f"### Price Intelligence for *{detected_category}*")
            st.markdown(f"Here's what we know about **{detected_category}** products across your watchlist:")
            
            watchlist = db.get_watchlist(st.session_state.current_user)
            
            # Find all products matching this category
            matches = []
            for item in watchlist:
                item_cat = item.get('product_data', {}).get('cnn_category', '')
                if item_cat.lower() == detected_category.lower():
                    matches.append(item)
            
            if matches:
                prices = [m['product_data']['price'] for m in matches]
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                cheapest_item = min(matches, key=lambda x: x['product_data']['price'])
                
                # Price stats cards
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(f"Tracked {detected_category}", len(matches))
                c2.metric("Avg Price", f"INR {avg_price:,.0f}")
                c3.metric("Cheapest", f"INR {min_price:,.0f}")
                c4.metric("Most Expensive", f"INR {max_price:,.0f}")
                
                # Smart recommendation
                st.markdown("#### Smart Recommendation")
                
                # Check price history trends for this category
                all_drops = []
                for m in matches:
                    history = db.get_price_history(m['product_url'])
                    if history and len(history) > 1:
                        first_price = history[-1]['price']
                        current_price = m['product_data']['price']
                        change_pct = ((current_price - first_price) / first_price) * 100
                        all_drops.append(change_pct)
                
                if all_drops:
                    avg_trend = sum(all_drops) / len(all_drops)
                    if avg_trend < -5:
                        st.success(f"""**BUY NOW** — {detected_category} prices are trending DOWN (avg {abs(avg_trend):.1f}% drop). 
                        The cheapest {detected_category} in your watchlist is **{cheapest_item['product_data']['title'][:50]}** at **INR {min_price:,.2f}**.""")
                    elif avg_trend > 5:
                        st.warning(f"""**WAIT** — {detected_category} prices are trending UP (avg {avg_trend:.1f}% increase). 
                        Prices may come down during upcoming sales. Keep tracking!""")
                    else:
                        st.info(f"""**STABLE** — {detected_category} prices are holding steady. 
                        Best current deal: **{cheapest_item['product_data']['title'][:50]}** at **INR {min_price:,.2f}**.""")
                else:
                    st.info(f"Add more price history data to get buy/wait recommendations for {detected_category}.")
                
                # ─── Section 3: Matching Products ───────────────────
                st.divider()
                st.markdown(f"#### Your {detected_category} Products ({len(matches)} found)")
                
                # Show by platform for cross-platform comparison
                platforms = {}
                for m in matches:
                    plat = m['product_data'].get('platform', 'unknown')
                    if plat not in platforms:
                        platforms[plat] = []
                    platforms[plat].append(m)
                
                if len(platforms) > 1:
                    st.markdown(f"**Cross-Platform Comparison:** You're tracking {detected_category} on **{', '.join(p.capitalize() for p in platforms.keys())}**")
                    for plat, items in platforms.items():
                        plat_prices = [i['product_data']['price'] for i in items]
                        plat_avg = sum(plat_prices) / len(plat_prices)
                        st.write(f"- **{plat.capitalize()}**: {len(items)} products, avg INR {plat_avg:,.0f}")
                    
                    cheapest_platform = min(platforms.keys(), key=lambda p: sum(i['product_data']['price'] for i in platforms[p]) / len(platforms[p]))
                    st.success(f"**{cheapest_platform.capitalize()}** has the cheapest {detected_category} on average!")
                
                mcols = st.columns(min(3, len(matches)))
                for i, match in enumerate(matches[:6]):
                    with mcols[i % 3]:
                        mdata = match['product_data']
                        st.image(mdata.get('image_url', ''), width=True)
                        st.write(f"**{mdata['title'][:40]}...**")
                        st.write(f"INR {mdata['price']:,.2f} | {mdata.get('platform', '').capitalize()}")
                        target = match.get('target_price')
                        if target:
                            if mdata['price'] <= target:
                                st.success(f"Below target (INR {target:,.0f})")
                            else:
                                st.caption(f"Target: INR {target:,.0f}")
            else:
                st.info(f"No **{detected_category}** products in your watchlist yet. Add some products to get category-level price analytics!")
                st.markdown(f"""**What you'll see once you track {detected_category} products:**
- Average, min, max prices across all your tracked {detected_category}
- Buy/Wait recommendation based on price trends
- Cross-platform price comparison (Amazon vs Myntra)
- Cheapest option highlighted""")
        else:
            st.error(f"Classification failed: {result.get('error', 'Unknown error')}")
    
    # ─── Section 4: Category-Grouped Watchlist Overview ─────────
    st.divider()
    st.markdown("### Your Watchlist — Grouped by CNN Category")
    st.markdown("All your tracked products, intelligently organized by what the CNN detected:")
    
    watchlist = db.get_watchlist(st.session_state.current_user)
    
    if watchlist:
        # Group by CNN category
        category_groups = {}
        uncategorized = []
        for item in watchlist:
            cat = item.get('product_data', {}).get('cnn_category', '')
            if cat:
                if cat not in category_groups:
                    category_groups[cat] = []
                category_groups[cat].append(item)
            else:
                uncategorized.append(item)
        
        if category_groups:
            # Summary metrics
            st.markdown(f"**{len(category_groups)} categories detected** across {len(watchlist)} products")
            
            for cat_name, items in sorted(category_groups.items(), key=lambda x: -len(x[1])):
                prices = [i['product_data']['price'] for i in items]
                with st.expander(f"{cat_name} — {len(items)} product(s) | Avg INR {sum(prices)/len(prices):,.0f}", expanded=False):
                    cols = st.columns(min(3, len(items)))
                    for i, item in enumerate(items[:6]):
                        with cols[i % 3]:
                            data = item['product_data']
                            st.image(data.get('image_url', ''), width=True)
                            st.write(f"**{data['title'][:35]}...**")
                            st.write(f"INR {data['price']:,.2f}")
        
        if uncategorized:
            with st.expander(f"Uncategorized — {len(uncategorized)} product(s) (added before CNN)", expanded=False):
                st.markdown("These products were added before CNN integration. Re-add them to auto-classify.")
                for item in uncategorized:
                    st.write(f"- {item['product_data']['title'][:60]}...")
    else:
        st.info("Your watchlist is empty. Add products from the Watchlist page to see them organized by category here.")

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
                enriched_watchlist = []
                for item in watchlist:
                    hist = db.get_price_history(item['product_url'], limit=5)
                    item_with_hist = item.copy()
                    item_with_hist['history_summary'] = [f"{h['timestamp'].strftime('%Y-%m-%d')}: INR {h['price']}" for h in hist if hasattr(h.get('timestamp'), 'strftime')]
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
            <div style="padding-bottom: 20px; text-align: center;">
                <p style="margin:0; font-size: 1rem; color: rgba(248, 250, 252, 0.68);">Welcome back,</p>
                <h2 style="margin:0; font-size: 1.8rem; color: white;">{st.session_state.get('current_name', 'User')}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            nav = st.radio("Navigation", ["Dashboard", "Watchlist", "Visual Search (CNN)", "AI Assistant", "Developer Panel", "Settings"], label_visibility="collapsed")
            
            st.divider()
            st.markdown("### AI Assistant")
            if GROQ_API_KEY:
                st.success(f"Groq ready ({GROQ_MODEL})")
            else:
                st.warning("Groq API key missing")
            st.info("Auto-sync: every 5 min")
            
            st.divider()
            st.markdown("### CNN Model")
            if cnn_predictor.is_ready():
                model_info = cnn_predictor.get_model_summary()
                st.success(f"MobileNetV2 ({model_info['num_classes']} classes)")
            else:
                st.warning("Model not trained")
            
        if nav == "Dashboard": show_dashboard()
        elif nav == "Watchlist": show_watchlist()
        elif nav == "Visual Search (CNN)": show_visual_search()
        elif nav == "AI Assistant": show_ai_assistant()
        elif nav == "Developer Panel": show_developer_panel()
        elif nav == "Settings": show_settings()
    else:
        show_login_page()

if __name__ == "__main__":
    main()
