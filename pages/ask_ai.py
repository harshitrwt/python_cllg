import streamlit as st
from database.firebase_db import FirebaseDB
from ai_assistant.groq_assistant import GroqAssistant
from utils.ui_utils import set_page_theme

def init_db():
    if "db" not in st.session_state:
        try:
            st.session_state.db = FirebaseDB()
        except:
            pass
    if "ai" not in st.session_state:
        try:
            st.session_state.ai = GroqAssistant()
        except Exception as e:
            st.error(f"Failed to load AI Assistant: {e}")
            st.stop()

def show_ai_assistant():
    set_page_theme()
    init_db()
    st.title("AI Price Assistant")
    
    if not st.session_state.get("user_logged_in"):
        st.warning("Please login first.")
        return

    db = st.session_state.db
    user_id = st.session_state.current_user
    watchlist = db.get_watchlist(user_id)

    st.write(f"Hi {user_id}! Ask me anything about your {len(watchlist)} tracked products.")
    
    st.divider()
    
    # Quick prompts
    st.subheader("💡 Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Show my watchlist summary"):
            if watchlist:
                summary = "**Your current watchlist:**\n\n"
                for item in watchlist:
                    p = item.get("product_data", {})
                    summary += f"- **{p.get('title', 'Unknown')}**: INR {p.get('price', 0.0):,.2f} on {p.get('platform', 'Unknown').capitalize()}\n"
                st.info(summary)
            else:
                st.warning("Your watchlist is empty!")
    
    with col2:
        if st.button(" Best time to buy?"):
            if watchlist:
                with st.spinner("Analyzing your entire watchlist..."):
                    enriched_watchlist = []
                    for item in watchlist:
                        hist = db.get_price_history(item['product_url'], limit=5)
                        item_with_hist = item.copy()
                        item_with_hist['history_summary'] = [f"{h.get('timestamp')}: INR {h.get('price')}" for h in hist if h.get('timestamp')]
                        enriched_watchlist.append(item_with_hist)
                    deal = st.session_state.ai.find_best_deal(enriched_watchlist)
                    st.success(deal)
            else:
                st.warning("Your watchlist is empty!")
    
    st.divider()
    
    # Chat interface
    st.subheader("Chat with AI")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm your price tracking assistant. I can see you have " + str(len(watchlist)) + " products. Ask me anything!"}
        ]
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    if user_input := st.chat_input("Ask me about prices..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing data..."):
                enriched_watchlist = []
                for item in watchlist:
                    hist = db.get_price_history(item['product_url'], limit=5)
                    item_with_hist = item.copy()
                    item_with_hist['history_summary'] = [f"{h.get('timestamp')}: INR {h.get('price')}" for h in hist if h.get('timestamp')]
                    enriched_watchlist.append(item_with_hist)
                
                response = st.session_state.ai.ask_ai(user_input, watchlist_context=enriched_watchlist)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    show_ai_assistant()
