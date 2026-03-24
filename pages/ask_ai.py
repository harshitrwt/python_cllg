import streamlit as st
from database.firebase_db import FirebaseDB
from utils.ui_utils import set_page_theme

def init_db():
    if "db" not in st.session_state:
        try:
            st.session_state.db = FirebaseDB()
        except Exception as e:
            st.error(f"Failed to connect to Firebase: {e}")
            st.stop()

def show_ai_assistant():
    set_page_theme()
    init_db()
    st.title("🤖 AI Price Assistant")
    
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
        if st.button("📊 Show my watchlist summary"):
            if watchlist:
                summary = "**Your current watchlist:**\n\n"
                for item in watchlist:
                    p = item.get("product_data", {})
                    summary += f"- **{p.get('title', 'Unknown')}**: ₹{p.get('price', 0.0):,.2f} on {p.get('platform', 'Unknown').capitalize()}\n"
                st.info(summary)
            else:
                st.warning("Your watchlist is empty!")
    
    with col2:
        if st.button("🏆 Best time to buy?"):
            st.success("Analysis suggests waiting for weekend sales for electronics in your list.")
    
    st.divider()
    
    # Chat interface
    st.subheader("💬 Chat with AI")
    
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
        
        # Simple response logic
        response = "I see you're interested in prices. Once our web scrapers are fully automated, I'll be able to give you precise per-second trends!"
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

if __name__ == "__main__":
    show_ai_assistant()
