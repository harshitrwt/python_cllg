import streamlit as st

import json
import os

def load_session():
    SESSION_FILE = "local_session.json"
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                data = json.load(f)
                return data.get("current_user")
        except:
            pass
    return None

def set_page_theme():
    if "user_logged_in" not in st.session_state:
        saved_user = load_session()
        if saved_user:
            st.session_state.user_logged_in = True
            st.session_state.current_user = saved_user
        else:
            st.session_state.user_logged_in = False
            st.session_state.current_user = None

    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

        :root {
            --bd-bg-0: #000000;
            --bd-bg-1: #000000;
            --bd-surface-0: rgba(255, 255, 255, 0.04);
            --bd-surface-1: rgba(255, 255, 255, 0.03);
            --bd-border: rgba(255, 255, 255, 0.10);
            --bd-border-strong: rgba(255, 255, 255, 0.14);
            --bd-text: #f8fafc;
            --bd-text-muted: rgba(248, 250, 252, 0.68);
            --bd-text-soft: rgba(248, 250, 252, 0.82);
            --bd-accent-0: #facc15; /* yellow */
            --bd-accent-1: #eab308; /* yellow hover */
            --bd-accent-2: #facc15;
        }
        
        body, .stApp, [data-testid="stAppViewContainer"], .main {
            background: var(--bd-bg-0);
            color: var(--bd-text);
            font-family: 'Outfit', sans-serif;
        }

        [data-testid="stHeader"] {
            background: transparent !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.92);
            border-right: 1px solid var(--bd-border);
            backdrop-filter: blur(10px);
        }
        
        .stMetric {
            background: var(--bd-surface-1) !important;
            padding: 12px 18px !important;
            border-radius: 12px !important;
            border: 1px solid var(--bd-border) !important;
        }
        
        .stMetric label {
            color: var(--bd-text-muted) !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            color: var(--bd-text) !important;
            font-size: 1.4rem !important;
            font-weight: 700 !important;
        }

        .product-card {
            background: var(--bd-surface-0);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 16px;
            border: 1px solid var(--bd-border-strong);
            padding: 15px;
            margin-bottom: 20px;
            height: 380px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.3s ease;
        }
        
        .product-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(250, 204, 21, 0.65);
            box-shadow: 0 15px 30px rgba(0,0,0,0.3);
        }

        .product-card img {
            width: 100%;
            height: 160px;
            object-fit: contain;
            border-radius: 8px;
            margin-bottom: 10px;
            background: white;
        }
        
        .price-tag {
            font-size: 22px;
            font-weight: 800;
            background: none;
            color: var(--bd-accent-0);
            -webkit-background-clip: initial;
            -webkit-text-fill-color: var(--bd-accent-0);
        }
        
        .platform-badge {
            padding: 5px 12px;
            border-radius: 50px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        .amazon-badge { background: #FF9900; color: #000; }
        .flipkart-badge { background: #2874F0; color: #fff; }
        
        .sidebar-stats {
            background: rgba(250, 204, 21, 0.10);
            padding: 20px;
            border-radius: 18px;
            margin-bottom: 25px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        h1, h2, h3, h4, .stSubheader {
            color: var(--bd-text) !important;
            font-weight: 700 !important;
        }
        
        .stButton>button {
            background: var(--bd-accent-0) !important;
            color: #000 !important;
            border: none !important;
            padding: 10px 24px !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton>button:hover {
            opacity: 0.9 !important;
            transform: scale(1.02) !important;
            background: var(--bd-accent-1) !important;
            box-shadow: 0 8px 15px rgba(250, 204, 21, 0.20) !important;
        }

        .stAlert {
            background-color: rgba(15, 23, 42, 0.7) !important;
            border: 1px solid var(--bd-border-strong) !important;
            color: var(--bd-text) !important;
        }

        div[data-baseweb="tab-list"] {
            background-color: transparent !important;
        }

        div[data-baseweb="tab"] {
            color: var(--bd-text-muted) !important;
        }

        div[aria-selected="true"] {
            color: var(--bd-accent-0) !important;
            border-bottom-color: var(--bd-accent-0) !important;
        }
        
        p, span, label {
            color: var(--bd-text-soft) !important;
        }

        a, a:visited {
            color: var(--bd-accent-0) !important;
        }
        
        input {
            background-color: rgba(2, 6, 23, 0.65) !important;
            color: white !important;
            border: 1px solid var(--bd-border-strong) !important;
        }

        textarea {
            background-color: rgba(2, 6, 23, 0.65) !important;
            color: white !important;
            border: 1px solid var(--bd-border-strong) !important;
        }

        [data-testid="stExpander"] {
            border-color: var(--bd-border) !important;
        }

        [data-testid="stChatMessage"] {
            background-color: rgba(15, 23, 42, 0.45) !important;
            color: var(--bd-text) !important;
        }

        [data-testid="stDataFrame"] {
            border-color: var(--bd-border) !important;
        }
    </style>
    """, unsafe_allow_html=True)
