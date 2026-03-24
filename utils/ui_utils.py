import streamlit as st

def set_page_theme():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        .main {
            background: radial-gradient(circle at top right, #1e293b, #0f172a);
            color: #f8fafc;
            font-family: 'Outfit', sans-serif;
        }
        
        [data-testid="stSidebar"] {
            background-color: rgba(15, 23, 42, 0.95);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }
        
        .stMetric {
            background: rgba(15, 23, 42, 0.4) !important;
            padding: 12px 18px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
        }
        
        .stMetric label {
            color: #94a3b8 !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            color: #f8fafc !important;
            font-size: 1.4rem !important;
            font-weight: 700 !important;
        }

        .product-card {
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 25px;
            margin-bottom: 25px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .product-card:hover {
            transform: translateY(-8px);
            background: rgba(30, 41, 59, 0.6);
            border-color: #10b981;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }
        
        .price-tag {
            font-size: 28px;
            font-weight: 800;
            background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
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
        
        .amazon-badge { background: linear-gradient(90deg, #FF9900, #FFB84D); color: #000; }
        .flipkart-badge { background: linear-gradient(90deg, #2874F0, #6197EF); color: #fff; }
        
        .sidebar-stats {
            background: linear-gradient(45deg, #059669 0%, #3b82f6 100%);
            padding: 20px;
            border-radius: 18px;
            margin-bottom: 25px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        h1, h2, h3, h4, .stSubheader {
            color: #f8fafc !important;
            font-weight: 700 !important;
        }
        
        .stButton>button {
            background: linear-gradient(90deg, #10b981 0%, #059669 100%) !important;
            color: white !important;
            border: none !important;
            padding: 10px 24px !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton>button:hover {
            opacity: 0.9 !important;
            transform: scale(1.02) !important;
            box-shadow: 0 8px 15px rgba(16, 185, 129, 0.3) !important;
        }

        .stAlert {
            background-color: rgba(30, 41, 59, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #f8fafc !important;
        }

        div[data-baseweb="tab-list"] {
            background-color: transparent !important;
        }

        div[data-baseweb="tab"] {
            color: #94a3b8 !important;
        }

        div[aria-selected="true"] {
            color: #10b981 !important;
            border-bottom-color: #10b981 !important;
        }
        
        p, span, label {
            color: #cbd5e1 !important;
        }
        
        input {
            background-color: rgba(30, 41, 59, 0.8) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
    </style>
    """, unsafe_allow_html=True)
