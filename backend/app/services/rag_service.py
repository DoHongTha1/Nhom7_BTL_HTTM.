"""
RAG (Retrieval-Augmented Generation) Service
"""
import os
from typing import Dict, List, Optional
from datetime import datetime
import chromadb
from sentence_transformers import SentenceTransformer
from app.config import settings
from app.services.genai_service import GenAIService

class RAGService:
    """RAG Service for contextual prediction adjustments"""
    
    def __init__(self):
        self.genai_service = GenAIService()
        self.embedding_model = None
        self.vector_db = None
        self._init_embedding_model()
        self._init_vector_db()
    
    def _init_embedding_model(self):
        """Initialize sentence transformer for embeddings"""
        try:
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        except Exception as e:
            print(f"Error initializing embedding model: {e}")
            self.embedding_model = None
    
    def _init_vector_db(self):
        """Initialize ChromaDB vector database"""
        try:
            os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
            self.vector_db = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
            # Get or create collection
            try:
                self.collection = self.vector_db.get_collection("news_articles")
            except:
                self.collection = self.vector_db.create_collection(
                    name="news_articles",
                    metadata={"hnsw:space": "cosine"}
                )
        except Exception as e:
            print(f"Error initializing vector DB: {e}")
            self.vector_db = None
    
    def add_news_article(self, country_code: str, title: str, content: str, source: str, published_date: str):
        """
        Add news article to vector database
        Args:
            country_code: Country code
            title: Article title
            content: Article content
            source: News source
            published_date: Publication date
        """
        if not self.embedding_model or not self.vector_db:
            print("Embedding model or vector DB not initialized")
            return
        
        # Create embedding
        text = f"{title}\n{content}"
        embedding = self.embedding_model.encode(text).tolist()
        
        # Add to collection
        doc_id = f"{country_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                "country_code": country_code,
                "title": title,
                "source": source,
                "published_date": published_date
            }]
        )
    
    def retrieve_relevant_news(self, country_code: str, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant news articles for a country
        Args:
            country_code: Country code
            query: Search query
            top_k: Number of results to return
        Returns:
            List of relevant news articles
        """
        if not self.embedding_model or not self.vector_db:
            return []
        
        # Create query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search in vector DB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"country_code": country_code} if country_code else None
        )
        
        # Format results
        articles = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                articles.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return articles
    
    def generate_contextual_adjustments(self, country_code: str, country_name: str, current_features: Dict) -> Dict:
        """
        Generate contextual adjustments to model features based on RAG
        Args:
            country_code: Country code
            country_name: Country name
            current_features: Current feature values
        Returns:
            Dictionary with suggested adjustments
        """
        # Step 1: Retrieve relevant news
        query = f"dân số {country_name} chính sách khuyến sinh đại dịch thay đổi nhân khẩu"
        relevant_news = self.retrieve_relevant_news(country_code, query, top_k=3)
        
        if not relevant_news:
            # No relevant news found, return no adjustments
            return {
                'adjustments': {},
                'reasoning': 'Không tìm thấy tin tức/chính sách mới liên quan.',
                'confidence': 0.0
            }
        
        # Step 2: Generate prompt for GenAI
        news_context = "\n".join([
            f"- {article['metadata'].get('title', 'N/A')} ({article['metadata'].get('source', 'N/A')})"
            for article in relevant_news
        ])
        
        prompt = f"""Tôi đang dự báo dân số cho {country_name} sử dụng mô hình XGBoost.

Các tham số hiện tại:
- Tỷ lệ sinh (birthRate): {current_features.get('birthRate', 0)}%
- Tỷ lệ tử (deathRate): {current_features.get('deathRate', 0)}%
- GDP per capita: {current_features.get('gdpPerCapita', 0)}
- Tỷ lệ sinh sản (fertilityRate): {current_features.get('fertilityRate', 0)}

Tin tức/chính sách mới nhất liên quan:
{news_context}

Dựa trên các tin tức/chính sách này, hãy phân tích và đề xuất điều chỉnh các tham số đầu vào cho mô hình XGBoost.
Ví dụ: Nếu có chính sách khuyến sinh mới, có thể tăng birthRate và fertilityRate.
Nếu có đại dịch, có thể tăng deathRate.

Trả lời dưới dạng JSON với format:
{{
    "adjustments": {{
        "birthRate": 0.5,  // Số thay đổi (có thể âm hoặc dương)
        "deathRate": 0.2,
        "fertilityRate": 0.3
    }},
    "reasoning": "Lý do điều chỉnh",
    "confidence": 0.8  // Độ tin cậy (0-1)
}}

Chỉ trả về JSON, không có text khác."""

        # Step 3: Call GenAI
        if self.genai_service.use_gemini and self.genai_service.model:
            response = self.genai_service._call_gemini_chat(prompt)
        elif not self.genai_service.use_gemini and self.genai_service.client:
            response = self.genai_service._call_openai_chat(prompt)
        else:
            # Mock response
            return {
                'adjustments': {},
                'reasoning': 'GenAI API chưa được cấu hình.',
                'confidence': 0.0
            }
        
        # Step 4: Parse response
        try:
            import json
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                adjustments = json.loads(json_str)
                return adjustments
        except Exception as e:
            print(f"Error parsing GenAI response: {e}")
        
        # Fallback: analyze news manually
        return self._manual_analysis(relevant_news, current_features)
    
    def _manual_analysis(self, news_articles: List[Dict], current_features: Dict) -> Dict:
        """Manual analysis of news articles (fallback)"""
        adjustments = {}
        reasoning_parts = []
        
        news_text = " ".join([article['content'].lower() for article in news_articles])
        
        # Check for birth rate related keywords
        if any(keyword in news_text for keyword in ['khuyến sinh', 'tăng sinh', 'trợ cấp sinh con']):
            adjustments['birthRate'] = 0.3
            adjustments['fertilityRate'] = 0.2
            reasoning_parts.append("Phát hiện chính sách khuyến sinh")
        
        # Check for pandemic/disaster keywords
        if any(keyword in news_text for keyword in ['đại dịch', 'dịch bệnh', 'thiên tai']):
            adjustments['deathRate'] = 0.5
            reasoning_parts.append("Phát hiện thông tin về đại dịch/thiên tai")
        
        # Check for economic growth
        if any(keyword in news_text for keyword in ['tăng trưởng kinh tế', 'phát triển', 'đầu tư']):
            adjustments['gdpPerCapita'] = current_features.get('gdpPerCapita', 0) * 0.05
            reasoning_parts.append("Phát hiện tăng trưởng kinh tế")
        
        return {
            'adjustments': adjustments,
            'reasoning': '. '.join(reasoning_parts) if reasoning_parts else 'Không phát hiện thay đổi đáng kể.',
            'confidence': 0.6 if adjustments else 0.3
        }

