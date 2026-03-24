from groq import Groq
import logging
from config import GROQ_API_KEY, GROQ_MODEL
from typing import List, Dict
import json

logger = logging.getLogger(__name__)

class GroqAssistant:
    def __init__(self):
        self.client = None
        self.model = GROQ_MODEL
        self.conversation_history = [
            {"role": "system", "content": "You are SmartPriceWatcher AI, a premium shopping consultant. You help users make informed buying decisions by analyzing price trends, comparing products across platforms like Amazon and Flipkart, and providing expert advice. Your tone is professional, helpful, and data-driven."}
        ]
        try:
            if GROQ_API_KEY:
                self.client = Groq(api_key=GROQ_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self.client = None
    
    def get_price_insights(self, product_data: Dict, price_history: List[Dict]) -> str:
        if not self.client:
            return "AI Insights are currently unavailable due to a technical issue. Please check your API key or connection."
        try:
            product_name = product_data.get('title', 'this product')
            current_price = product_data.get('price', 0)
            price_context = self._format_price_context(price_history)
            prompt = f"""
            Analyze the price history for the product: "{product_name}"
            Current Price: ₹{current_price:,.2f}
            Historical Price Data:
            {price_context}
            Based on this data, please provide a detailed analysis:
            1. **Price Trajectory**: Is the price currently at a peak, a valley, or a stable plateau?
            2. **Buy/Wait Recommendation**: Provide a clear recommendation (Buy Now, Wait for Drop, or Watch Closely) with reasoning.
            3. **Value Assessment**: How does the current price compare to the historical average (₹{self._calculate_avg(price_history):,.2f})?
            4. **Predicted Next Move**: Based on the pattern, what is the likely short-term price movement?
            Use markdown formatting for a professional look.
            """
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return "I analyzed the price trends but encountered an error generating the report."
    
    def find_best_deal(self, products: List[Dict]) -> str:
        if not self.client:
            return "Dealer identification AI is currently offline. You can manually compare prices in your dashboard."
        try:
            if not products:
                return "You haven't added any products to compare yet."
            product_context = self._format_products(products)
            prompt = f"""
            I need you to act as a value-focused shopping expert. Compare the following products from the user's watchlist and identify the BEST DEAL.
            Products under consideration:
            {product_context}
            Criteria for your recommendation:
            - Best price-to-feature ratio.
            - Platform reliability (Amazon vs Flipkart).
            - Current discounts or price drops.
            Format your response as a "Deal of the Day" recommendation with:
            1. **The Winner**: Clearly state which product is the best deal.
            2. **Why it wins**: 3 bullet points explaining the value.
            3. **Alternative**: A 'Runner-up' if the first choice doesn't suit some users.
            4. **Buying Tip**: A pro-tip for this specific category of products.
            Use emojis to make it engaging!
            """
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error finding best deal: {e}")
            return "I couldn't compare the deals right now."
    
    def ask_ai(self, question: str, watchlist_context: List[Dict] = None) -> str:
        if not self.client:
            return "AI Chat Assistant is currently offline. You can still track prices and manage your watchlist!"
        try:
            messages = self.conversation_history.copy()
            if watchlist_context:
                context_str = self._format_products(watchlist_context)
                messages.append({
                    "role": "system", 
                    "content": f"The user currently has these products in their watchlist: {context_str}"
                })
            messages.append({"role": "user", "content": question})
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            answer = response.choices[0].message.content
            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": answer})
            if len(self.conversation_history) > 11:
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-10:]
            return answer
        except Exception as e:
            logger.error(f"AI Assistant error: {e}")
            return "I'm having trouble thinking right now. Please try again in a moment."

    def _format_price_context(self, history: List[Dict]) -> str:
        if not history: return "No historical data available."
        return "\n".join([f"- {h.get('timestamp')}: ₹{h.get('price', 0):,.2f}" for h in history[:15]])

    def _calculate_avg(self, history: List[Dict]) -> float:
        if not history: return 0.0
        prices = [h.get('price', 0) for h in history if h.get('price', 0) > 0]
        return sum(prices) / len(prices) if prices else 0.0

    def _format_products(self, products: List[Dict]) -> str:
        formatted = ""
        for i, p in enumerate(products, 1):
            data = p.get('product_data', {})
            formatted += f"\n{i}. {data.get('title')} ({data.get('platform', 'unknown')})\n"
            formatted += f"   - Price: ₹{data.get('price', 0):,.2f}\n"
            if data.get('description'):
                formatted += f"   - Details: {data.get('description')[:150]}...\n"
        return formatted
