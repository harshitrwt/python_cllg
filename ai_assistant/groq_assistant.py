from groq import Groq
import logging
from config import GROQ_API_KEY, GROQ_MODEL
from typing import List, Dict

logger = logging.getLogger(__name__)


class GroqAssistant:
    def __init__(self):
        """Initialize Groq client"""
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
        self.conversation_history = []
    
    def get_price_insights(self, product_name: str, price_history: List[Dict]) -> str:
        """
        Get AI insights about product price trends
        
        Args:
            product_name: Name of the product
            price_history: List of historical prices with timestamps
            
        Returns:
            AI-generated insight about the price trend
        """
        try:
            # Format price history for context
            price_context = self._format_price_context(price_history)
            
            prompt = f"""
            Analyze the price history for '{product_name}' and provide insights:
            
            Price History:
            {price_context}
            
            Please provide:
            1. Current trend (increasing/decreasing/stable)
            2. Best time to buy recommendation
            3. Average price
            4. Price volatility assessment
            """
            
            response = self.client.messages.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            
            insight = response.choices[0].message.content
            logger.info(f"Generated insight for {product_name}")
            return insight
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return "Unable to generate insights at the moment."
    
    def ask_question(self, question: str, context: str = "") -> str:
        """
        Ask the AI assistant a question with optional context
        
        Args:
            question: User's question
            context: Additional context about products/prices
            
        Returns:
            AI response
        """
        try:
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": question})
            
            
            messages = self.conversation_history.copy()
            
            if context:
                messages[0] = {
                    "role": "system",
                    "content": f"You are a helpful price tracking assistant. Context: {context}"
                }
            
            response = self.client.messages.create(
                model=self.model,
                messages=messages,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            # Add to history
            self.conversation_history.append({"role": "assistant", "content": answer})
            
            logger.info("Question answered successfully")
            return answer
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return "I couldn't process that question. Please try again."
    
    def find_best_deal(self, products: List[Dict]) -> str:
        """Find the best deal among products"""
        try:
            product_context = self._format_products(products)
            
            prompt = f"""
            Compare these products and find the best deal:
            
            {product_context}
            
            Provide a recommendation on which product offers the best value.
            """
            
            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            recommendation = response.choices[0].message.content
            logger.info("Generated product recommendation")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error finding best deal: {e}")
            return "Unable to find best deal at the moment."
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    @staticmethod
    def _format_price_context(price_history: List[Dict]) -> str:
        """Format price history for display"""
        context = ""
        for entry in price_history[:10]: 
            price = entry.get("price", "N/A")
            timestamp = entry.get("timestamp", "N/A")
            context += f"- Price: {price}, Date: {timestamp}\n"
        return context
    
    @staticmethod
    def _format_products(products: List[Dict]) -> str:
        """Format products for comparison"""
        context = ""
        for i, product in enumerate(products, 1):
            context += f"\n{i}. {product.get('title', 'Unknown')}\n"
            context += f"   - Price: {product.get('price', 'N/A')}\n"
            context += f"   - Platform: {product.get('platform', 'N/A')}\n"
            context += f"   - Rating: {product.get('rating', 'N/A')}\n"
        return context
