"""
AI Assistant page - Ask questions about price data
"""

import streamlit as st


def show_ai_assistant():
    """Display AI assistant page"""
    st.title("🤖 AI Price Assistant")
    
    st.write("Ask me anything about your products and get AI-powered insights!")
    
    st.divider()
    
    # Quick prompts
    st.subheader("💡 Quick Questions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Show price trends"):
            st.info(
                "Based on your watchlist:\n\n"
                "**Laptop** - Price is trending downward over the last 7 days. "
                "Dropped from ₹1,29,999 to ₹1,24,999. Best time to buy would be "
                "in the next 2-3 days if the trend continues."
            )
        
        if st.button("🏆 Find best deal"):
            st.success(
                "**Best Deal:** iPhone 15 Pro on Flipkart\n"
                "- Price: ₹84,999 (₹2,000 cheaper than Amazon)\n"
                "- Cashback: 5% on credit cards\n"
                "- Delivery: Free 2-day delivery"
            )
    
    with col2:
        if st.button("⬇️ Show price drops"):
            st.warning(
                "Products with significant price drops:\n\n"
                "1. **Sony Headphones** - ₹26,999 → ₹24,499 (9% drop)\n"
                "2. **Apple Watch** - ₹43,499 → ₹41,999 (4% drop)\n"
                "3. **iPad** - ₹57,999 → ₹54,999 (5% drop)"
            )
        
        if st.button("💰 Compare prices"):
            st.info(
                "Price comparison for iPhone 15 Pro:\n\n"
                "- **Amazon:** ₹84,999\n"
                "- **Flipkart:** ₹82,999 ✅ Best Price\n"
                "- Savings: ₹2,000 on Flipkart"
            )
    
    st.divider()
    
    # Chat interface
    st.subheader("💬 Chat with AI")
    
    # Chat history (session state)
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi! I'm your price tracking AI assistant. Ask me about product prices, trends, or get buying recommendations!"
            }
        ]
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # User input
    if user_input := st.chat_input("Ask me about prices..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)
        
        # Generate AI response (placeholder)
        ai_response = generate_ai_response(user_input)
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        with st.chat_message("assistant"):
            st.write(ai_response)


def generate_ai_response(user_input: str) -> str:
    """Generate AI response based on user input"""
    # Placeholder responses
    responses = {
        "laptop": "The laptop in your watchlist has dropped ₹5,000! It's now at ₹1,24,999. This is the lowest price in 30 days. I recommend buying now!",
        "phone": "The iPhone 15 Pro is available at ₹82,999 on Flipkart, which is ₹2,000 cheaper than Amazon. Great time to grab it!",
        "trend": "Overall, prices are trending downward. 3 out of 5 products in your watchlist have seen price drops in the last week.",
        "alert": "You have 3 active price alerts. 1 of them has been triggered for the Laptop!",
        "recommend": "Based on your preferences, I recommend buying the Sony Headphones now - they're at a 9% discount and getting positive reviews.",
    }
    
    # Check if any keywords match
    input_lower = user_input.lower()
    for keyword, response in responses.items():
        if keyword in input_lower:
            return response
    
    # Default response
    return (
        "That's an interesting question! Based on current market trends and your watchlist, "
        "I can help you find the best deals. Could you be more specific about which product "
        "or category you're interested in?"
    )


if __name__ == "__main__":
    show_ai_assistant()
