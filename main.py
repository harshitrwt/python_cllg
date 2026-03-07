import streamlit as st
import logging
from datetime import datetime

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
                    st.session_state.user_logged_in = True
                    st.session_state.current_user = email
                    st.success(f"Welcome back, {email}!")
                    st.rerun()
                else:
                    st.error("Please enter email and password")
        
        with tab2:
            st.subheader("Create Account")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            
            if st.button("Sign Up", use_container_width=True):
                if new_email and new_password and confirm_password:
                    if new_password == confirm_password:
                        st.session_state.user_logged_in = True
                        st.session_state.current_user = new_email
                        st.success(f"Account created! Welcome, {new_email}!")
                        st.rerun()
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
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Products Watching", 5, delta="2 new")
    with col2:
        st.metric("Price Alerts", 3, delta=1)
    with col3:
        st.metric("Avg. Savings", "₹2,450", delta="↓ 12%")
    with col4:
        st.metric("Best Deal Today", "Laptop", delta="↓ ₹5,000")
    
    st.divider()
    
    # Price trends
    st.subheader("📈 Recent Activity")
    
    import pandas as pd
    
    # im using dummy data 
    activity_data = {
        "Product": ["Laptop", "Phone", "Headphones", "Smartwatch"],
        "Platform": ["Amazon", "Flipkart", "Amazon", "Flipkart"],
        "Current Price": ["₹1,24,999", "₹84,999", "₹24,499", "₹41,999"],
        "Change": ["-₹5,000", "-₹2,000", "+₹500", "-₹1,000"],
        "Status": ["🔴 Alert!", "🟢 Down", "🔵 Up", "🟢 Down"]
    }
    
    df = pd.DataFrame(activity_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def show_watchlist():
    """Watchlist view"""
    st.title("📌 My Watchlist")
    
    st.subheader("➕ Add New Product")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url = st.text_input("Product URL", placeholder="https://amazon.com/dp/...")
    with col2:
        if st.button("Add", use_container_width=True):
            st.success("✅ Added to watchlist!")
    
    st.divider()
    st.subheader("📦 Your Products")
    
    import pandas as pd
    data = {
        "Product": ["Dell XPS 13", "iPhone 15 Pro", "Sony Headphones"],
        "Price": ["₹1,24,999", "₹84,999", "₹24,499"],
        "Target": ["₹1,10,000", "₹75,000", "₹20,000"],
        "Change": ["-₹5,000", "-₹2,000", "-₹3,499"]
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)


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
