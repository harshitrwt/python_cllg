import streamlit as st
import logging
from datetime import datetime
from database.firebase_db import FirebaseDB

# Configure page
st.set_page_config(
    page_title="SmartPriceWatcher",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Initialize FirebaseDB
if "db" not in st.session_state:
    try:
        st.session_state.db = FirebaseDB()
    except Exception as e:
        st.error(f"Failed to connect to Firebase: {e}")
        st.stop()


def show_login_page():
    """Display login/signup page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>💰 SmartPriceWatcher</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>AI-Powered Product Price Tracker</p>", unsafe_allow_html=True)
        st.divider()
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.subheader("Login")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True):
                if email and password:
                    email = email.lower().strip()
                    user_data = st.session_state.db.get_user(email)
                    if user_data:
                        # In a real app, hash and check passwords
                        if user_data.get("password") == password:
                            st.session_state.user_logged_in = True
                            st.session_state.current_user = email
                            st.success(f"Welcome back, {email}!")
                            st.rerun()
                        else:
                            st.error("Incorrect password")
                    else:
                        st.error("User not found. Please sign up.")
                else:
                    st.error("Please enter email and password")
        
        with tab2:
            st.subheader("Create Account")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            
            if st.button("Sign Up", use_container_width=True):
                if new_email and new_password and confirm_password:
                    new_email = new_email.lower().strip()
                    if new_password == confirm_password:
                        # Check if user already exists
                        if st.session_state.db.get_user(new_email):
                            st.error("User already exists with this email")
                        else:
                            # Add to Firebase
                            success = st.session_state.db.add_user(new_email, {
                                "email": new_email,
                                "password": new_password # Simplified for now
                            })
                            if success:
                                st.session_state.user_logged_in = True
                                st.session_state.current_user = new_email
                                st.success(f"Account created! Welcome, {new_email}!")
                                st.rerun()
                            else:
                                st.error("Failed to create account in database")
                    else:
                        st.error("Passwords don't match")
                else:
                    st.error("Please fill all fields")


def show_main_app():
    """Display main application"""
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 Menu")
        
        page = st.radio(
            "Navigate to:",
            ["Dashboard", "Watchlist", "AI Assistant", "Settings"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        st.markdown("### 📊 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Watching", "5")
        with col2:
            st.metric("Alerts", "3")
        
        st.divider()
        
        st.markdown("### 👤 Account")
        st.write(f"**Logged in as:**\n{st.session_state.current_user}")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_logged_in = False
            st.session_state.current_user = None
            st.rerun()
    
    # Main content
    if page == "Dashboard":
        show_dashboard()
    elif page == "Watchlist":
        show_watchlist()
    elif page == "AI Assistant":
        show_ai_assistant()
    elif page == "Settings":
        show_settings()


def show_dashboard():
    """Dashboard view"""
    st.title("📊 Dashboard")
    
    watchlist = st.session_state.db.get_watchlist(st.session_state.current_user)
    alerts = st.session_state.db.get_user_alerts(st.session_state.current_user)
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Products Watching", len(watchlist))
    with col2:
        st.metric("Price Alerts", len(alerts))
    with col3:
        st.metric("Avg. Savings", "₹0", delta="0%")
    with col4:
        st.metric("Best Deal", "N/A", delta="None")
    
    st.divider()
    
    # Price trends
    st.subheader("📈 Recent Activity")
    
    import pandas as pd
    
    if watchlist:
        activity_data = []
        for item in watchlist[:5]: # Show last 5
            product_data = item.get("product_data", {})
            activity_data.append({
                "Product": product_data.get("title", "New Product"),
                "Platform": product_data.get("platform", "Unknown").capitalize(),
                "Current Price": f"₹{product_data.get('price', 0.0):,.2f}",
                "Status": "🔍 Tracking"
            })
        
        df = pd.DataFrame(activity_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No activity yet. Add products to see them here.")


def show_watchlist():
    """Watchlist view"""
    st.title("📌 My Watchlist")
    
    st.subheader("➕ Add New Product")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url = st.text_input("Product URL", placeholder="https://amazon.com/dp/...")
    with col2:
        if st.button("Add", use_container_width=True):
            if url:
                # Basic validation
                if "amazon" in url or "flipkart" in url:
                    # Minimal data for now
                    dummy_data = {
                        "title": url.split("/")[-1][:30] + "...", # Basic title from URL
                        "price": 0.0,
                        "currency": "INR",
                        "platform": "amazon" if "amazon" in url else "flipkart"
                    }
                    with st.spinner("Saving to database..."):
                        success = st.session_state.db.add_to_watchlist(st.session_state.current_user, url, dummy_data)
                        if success:
                            st.toast(f"Added {url} to your list!")
                            # Small delay to let toast show or just rerun
                            st.success("✅ Added to watchlist!")
                            st.rerun()
                        else:
                            st.error(f"❌ Database error: Could not save to 'watchlists' collection for user {st.session_state.current_user}")
                else:
                    st.error("Please enter a valid Amazon or Flipkart URL")
            else:
                st.error("Please enter a URL")
    
    st.divider()
    st.subheader("📦 Your Products")
    
    watchlist = st.session_state.db.get_watchlist(st.session_state.current_user)
    
    if watchlist:
        # Create header row
        header_cols = st.columns([2, 1, 1, 1, 0.5])
        header_cols[0].markdown("**Product**")
        header_cols[1].markdown("**Price**")
        header_cols[2].markdown("**Target**")
        header_cols[3].markdown("**Added**")
        header_cols[4].markdown("**Action**")
        
        st.divider()
        
        for item in watchlist:
            product_data = item.get("product_data", {})
            added_at = item.get("added_at")
            if hasattr(added_at, "strftime"):
                added_date = added_at.strftime("%Y-%m-%d")
            else:
                added_date = "N/A"
            
            cols = st.columns([2, 1, 1, 1, 0.5])
            
            # Display info
            cols[0].text(product_data.get("title", "Unknown")[:40] + "...")
            cols[1].text(f"₹{product_data.get('price', 0.0):,.2f}")
            cols[2].text(f"₹{item.get('target_price', 0.0) or 0.0:,.2f}")
            cols[3].text(added_date)
            
            # Remove button
            if cols[4].button("🗑️", key=f"remove_{item.get('id')}"):
                if st.session_state.db.remove_from_watchlist(item.get("id")):
                    st.success("Removed!")
                    st.rerun()
                else:
                    st.error("Failed to remove")
    else:
        st.info("Your watchlist is empty. Add a product to get started!")


def show_ai_assistant():
    """AI Assistant view"""
    st.title("🤖 AI Price Assistant")
    
    st.write("Ask me anything about your products!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("📊 Show trends")
        st.button("🏆 Best deals")
    with col2:
        st.button("⬇️ Price drops")
        st.button("💰 Compare prices")
    
    st.divider()
    
    # Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if user_input := st.chat_input("Ask me..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        response = "Great question! Based on your watchlist, the laptop is at its lowest price right now."
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)


def show_settings():
    """Settings view"""
    st.title("⚙️ Settings")
    
    st.subheader("🔔 Notifications")
    email_alerts = st.checkbox("Email alerts for price drops", value=True)
    alert_threshold = st.slider("Alert threshold (%)", 1, 50, 5)
    
    st.divider()
    
    st.subheader("🛒 Preferences")
    platforms = st.multiselect("Select platforms", ["Amazon", "Flipkart"], default=["Amazon", "Flipkart"])
    
    st.divider()
    
    if st.button("💾 Save Settings", use_container_width=True):
        st.success("Settings saved successfully!")


# Main app logic
def main():
    """Main application entry point"""
    if st.session_state.user_logged_in:
        show_main_app()
    else:
        show_login_page()


if __name__ == "__main__":
    main()
