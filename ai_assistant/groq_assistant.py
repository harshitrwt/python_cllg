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
            {"role": "system", "content": "You are Price Pulse AI, a professional shopping consultant. You provide data-driven insights on price trends across platforms like Amazon and Flipkart. Your tone is objective, analytical, and professional. Avoid using emojis in your responses."}
        ]
        try:
            if GROQ_API_KEY:
                self.client = Groq(api_key=GROQ_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self.client = None
    
    def get_price_insights(self, product_data: Dict, price_history: List[Dict]) -> str:
        if not self.client:
            return "AI Insights are currently unavailable. Please check your configuration."
        try:
            product_name = product_data.get('title', 'this product')
            current_price = product_data.get('price', 0)
            price_context = self._format_price_context(price_history)
            prompt = f"""
            Analyze the price history for: "{product_name}"
            Current Price: INR {current_price:,.2f}
            Price History:
            {price_context}
            
            Provide a professional analysis covering:
            1. Price Trajectory: Peak, valley, or stable.
            2. Purchase Recommendation: Buy, wait, or watch, with reasoning based on historical data.
            3. Value Assessment: Comparison with historical average (INR {self._calculate_avg(price_history):,.2f}).
            4. Prediction: Likely short-term price movement based on patterns.
            
            Format with markdown and do not use emojis.
            """
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return "Technical error encountered during trend analysis."
    
    def find_best_deal(self, products: List[Dict]) -> str:
        if not self.client:
            return "AI analysis is currently offline."
        try:
            if not products:
                return "No products available for comparison."
            product_context = self._format_products(products)
            prompt = f"""
            Compare the following products and identify the best value recommendation.
            Products:
            {product_context}
            
            Identify:
            1. The Top Recommendation: Best value-to-feature ratio.
            2. Rationale: Data-backed reasons for this choice.
            3. Alternative: A secondary option for different budgets.
            4. Professional Tip: Expert advice for this product category.
            
            Use professional markdown formatting. Do not use emojis.
            """
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error finding best deal: {e}")
            return "Unable to compare deals at this time."
    
    def ask_ai(self, question: str, watchlist_context: List[Dict] = None) -> str:
        if not self.client:
            return "AI assistant is currently offline."
        try:
            messages = self.conversation_history.copy()
            if watchlist_context:
                context_str = self._format_products(watchlist_context)
                messages.append({
                    "role": "system", 
                    "content": f"User Watchlist: {context_str}"
                })
            messages.append({"role": "user", "content": question})
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.6
            )
            answer = response.choices[0].message.content
            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": answer})
            if len(self.conversation_history) > 11:
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-10:]
            return answer
        except Exception as e:
            logger.error(f"AI Assistant error: {e}")
            return "System busy. Please try again later."

    def _format_price_context(self, history: List[Dict]) -> str:
        if not history: return "No historical data available."
        return "\n".join([f"- {h.get('timestamp')}: INR {h.get('price', 0):,.2f}" for h in history[:15]])

    def _calculate_avg(self, history: List[Dict]) -> float:
        if not history: return 0.0
        prices = [h.get('price', 0) for h in history if h.get('price', 0) > 0]
        return sum(prices) / len(prices) if prices else 0.0

    def _format_products(self, products: List[Dict]) -> str:
        formatted = ""
        for i, p in enumerate(products, 1):
            data = p.get('product_data', {})
            formatted += f"\n{i}. {data.get('title')} ({data.get('platform', 'unknown')})\n"
            formatted += f"   - Current Price: INR {data.get('price', 0):,.2f}\n"
            if p.get('history_summary'):
                formatted += f"   - Price History: {', '.join(p['history_summary'])}\n"
            if data.get('description'):
                formatted += f"   - Description: {data.get('description')[:100]}...\n"
        return formatted
