"""
Response Formatter Module
Styles and formats LLM responses for better presentation
"""

import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ResponseFormatter:
    """Formats LLM responses with HTML styling"""
    
    def __init__(self):
        self.product_keywords = [
            "smartphone", "laptop", "headphone", "phone", "computer", 
            "tablet", "earphone", "speaker", "camera", "watch"
        ]
        self.brand_keywords = [
            "samsung", "apple", "xiaomi", "realme", "oneplus", "google", 
            "sony", "lg", "huawei", "oppo", "vivo", "motorola"
        ]
    
    def format_response(self, response: str) -> str:
        """Main method to format LLM responses"""
        try:
            # Clean the response
            cleaned_response = self._clean_response(response)
            
            # Detect if it's a product recommendation
            if self._is_product_recommendation(cleaned_response):
                return self._format_product_recommendation(cleaned_response)
            else:
                return self._format_general_response(cleaned_response)
                
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            return self._format_fallback_response(response)
    
    def _clean_response(self, response: str) -> str:
        """Clean and normalize the response"""
        # Remove extra whitespace
        response = re.sub(r'\s+', ' ', response.strip())
        
        # Fix common formatting issues
        response = response.replace('**', '')  # Remove markdown bold
        response = response.replace('*', '')   # Remove markdown italic
        
        return response
    
    def _is_product_recommendation(self, response: str) -> bool:
        """Check if response contains product recommendations"""
        response_lower = response.lower()
        
        # Check for product-related keywords
        has_product_keywords = any(keyword in response_lower for keyword in self.product_keywords)
        has_brand_keywords = any(brand in response_lower for brand in self.brand_keywords)
        has_recommendation_words = any(word in response_lower for word in [
            "recommend", "suggest", "best", "top", "good", "excellent", "great"
        ])
        
        # Check for numbered lists or bullet points
        has_numbered_list = bool(re.search(r'\d+\.', response))
        has_bullet_points = bool(re.search(r'[-•*]\s', response))
        
        return (has_product_keywords or has_brand_keywords) and (
            has_recommendation_words or has_numbered_list or has_bullet_points
        )
    
    def _format_product_recommendation(self, response: str) -> str:
        """Format product recommendation responses"""
        # Extract product information
        products = self._extract_products(response)
        
        if products:
            return self._create_product_cards(products, response)
        else:
            return self._format_general_response(response)
    
    def _extract_products(self, response: str) -> List[Dict[str, str]]:
        """Extract product information from response"""
        products = []
        
        # Look for numbered lists
        numbered_items = re.findall(r'(\d+)\.\s*([^.\n]+)', response)
        
        for number, content in numbered_items:
            # Extract product name (usually the first part)
            product_name = content.split(' - ')[0].strip()
            if product_name:
                # Extract price if present
                price_match = re.search(r'[₹$]\s*[\d,]+', content)
                price = price_match.group(0) if price_match else ""
                
                # Extract rating if present
                rating_match = re.search(r'(\d+\.?\d*)/5', content)
                rating = rating_match.group(1) if rating_match else ""
                
                products.append({
                    'name': product_name,
                    'price': price,
                    'rating': rating,
                    'description': content.strip()
                })
        
        return products
    
    def _create_product_cards(self, products: List[Dict[str, str]], original_response: str) -> str:
        """Create styled product cards"""
        html = f'''
        <div class="product-recommendation">
            <h4><i class="fas fa-star"></i>Product Recommendations</h4>
            <p class="recommendation-intro">{self._get_recommendation_intro(original_response)}</p>
            <div class="product-list">
        '''
        
        for i, product in enumerate(products, 1):
            # Generate star rating HTML
            stars_html = ""
            if product['rating']:
                rating_num = float(product['rating'])
                stars_html = "".join(["<i class='fas fa-star stars'></i>" for _ in range(int(rating_num))])
                if rating_num % 1 >= 0.5:
                    stars_html += "<i class='fas fa-star-half-alt stars'></i>"
            
            html += f'''
                <div class="product-item">
                    <div class="product-name">
                        <i class="fas fa-mobile-alt"></i>
                        <strong>{i}. {product['name']}</strong>
                    </div>
                    <div class="product-description">
                        {product['description']}
                    </div>
                    {f'<div class="product-price">{product["price"]}</div>' if product['price'] else ''}
                    {f'<div class="product-rating"><span class="stars">{stars_html}</span> <span>{product["rating"]}/5</span></div>' if product['rating'] else ''}
                </div>
            '''
        
        html += '''
            </div>
            <div class="disclaimer">
                <i class="fas fa-info-circle"></i>
                Recommendations are based on available product data and reviews.
            </div>
        </div>
        '''
        
        return html
    
    def _get_recommendation_intro(self, response: str) -> str:
        """Extract the introduction text from the response"""
        # Find the first sentence or paragraph before the numbered list
        sentences = response.split('.')
        intro_parts = []
        
        for sentence in sentences:
            if re.search(r'\d+\.', sentence):
                break
            intro_parts.append(sentence.strip())
        
        intro = '. '.join(intro_parts).strip()
        if intro and not intro.endswith('.'):
            intro += '.'
        
        return intro if intro else "Here are some product recommendations based on your query:"
    
    def _format_general_response(self, response: str) -> str:
        """Format general responses with basic styling"""
        # Split into paragraphs
        paragraphs = response.split('\n\n')
        
        html = '<div class="general-response">'
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # Check if it's a list
            if re.search(r'^[-•*]\s', paragraph) or re.search(r'^\d+\.\s', paragraph):
                html += self._format_list(paragraph)
            else:
                html += f'<p class="response-paragraph">{paragraph}</p>'
        
        html += '</div>'
        return html
    
    def _format_list(self, text: str) -> str:
        """Format list items"""
        lines = text.split('\n')
        html = '<ul class="response-list">'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Remove list markers
            line = re.sub(r'^[-•*]\s*', '', line)
            line = re.sub(r'^\d+\.\s*', '', line)
            
            if line:
                html += f'<li class="response-list-item">{line}</li>'
        
        html += '</ul>'
        return html
    
    def _format_fallback_response(self, response: str) -> str:
        """Fallback formatting for errors"""
        return f'''
        <div class="general-response">
            <p class="response-paragraph">{response}</p>
        </div>
        '''

# Global formatter instance
response_formatter = ResponseFormatter()

def format_llm_response(response: str) -> str:
    """Main function to format LLM responses"""
    return response_formatter.format_response(response)
