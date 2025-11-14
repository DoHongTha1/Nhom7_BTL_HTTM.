"""
GenAI Service for AI Insights and Chat
"""
import os
from typing import Dict, List, Optional
from app.config import settings

class GenAIService:
    """Service for interacting with GenAI APIs (OpenAI/Gemini)"""
    
    def __init__(self):
        self.use_gemini = settings.USE_GEMINI
        if self.use_gemini:
            self._init_gemini()
        else:
            self._init_openai()
    
    def _init_gemini(self):
        """Initialize Google Gemini API"""
        try:
            import google.generativeai as genai
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                preferred_model = settings.GEMINI_MODEL or "models/gemini-1.5-pro-latest"
                fallback_model = "models/gemini-1.5-flash-latest"

                try:
                    self.model = genai.GenerativeModel(preferred_model)
                    self.gemini_model_name = preferred_model
                except Exception as model_error:
                    print(
                        f"Warning: Failed to initialise Gemini model '{preferred_model}': {model_error}. "
                        f"Falling back to '{fallback_model}'."
                    )
                    self.model = genai.GenerativeModel(fallback_model)
                    self.gemini_model_name = fallback_model

                self.client = genai
            else:
                print("Warning: GEMINI_API_KEY not set, using mock responses")
                self.model = None
        except ImportError:
            print("google-generativeai not installed, using mock responses")
            self.model = None
    
    def _init_openai(self):
        """Initialize OpenAI API"""
        try:
            from openai import OpenAI
            if settings.OPENAI_API_KEY:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                self.model = "gpt-3.5-turbo"
            else:
                print("Warning: OPENAI_API_KEY not set, using mock responses")
                self.client = None
        except ImportError:
            print("openai not installed, using mock responses")
            self.client = None
    
    def generate_ai_insights(self, model_metrics: Dict, forecast_data: Dict, country_data: Dict) -> List[str]:
        """
        Generate AI insights based on model results
        Args:
            model_metrics: Training metrics from XGBoost model
            forecast_data: Forecast results
            country_data: Country demographic data
        Returns:
            List of insight strings
        """
        prompt = f"""Tôi có một mô hình XGBoost dự báo dân số cho {country_data.get('name', 'quốc gia')}.

Kết quả mô hình:
- R² Score: {model_metrics.get('val_r2', 0):.3f} ({model_metrics.get('val_r2', 0)*100:.1f}%)
- RMSE: {model_metrics.get('val_rmse', 0):.3f}%
- MAE: {model_metrics.get('val_mae', 0):.3f}%
- Biến quan trọng nhất: {self._get_top_feature(model_metrics.get('feature_importance', {}))}

Dữ liệu quốc gia:
- Dân số hiện tại: {country_data.get('population', 0):,.0f}
- Tỷ lệ sinh: {country_data.get('birthRate', 0)}%
- Tỷ lệ tử: {country_data.get('deathRate', 0)}%
- Giai đoạn chuyển đổi nhân khẩu: {country_data.get('stage', 0)}
- Tuổi trung bình: {country_data.get('medianAge', 0)}

Dự báo:
- Tăng trưởng dự kiến: {forecast_data.get('growthRate', 0):.2f}%
- Dân số dự kiến sau {forecast_data.get('years', 10)} năm: {forecast_data.get('finalPopulation', 0):,.0f}

Hãy viết 3-5 gạch đầu dòng phân tích ngắn gọn tình hình này như một chuyên gia nhân khẩu học, tập trung vào:
1. Đánh giá độ chính xác của mô hình
2. Phân tích xu hướng dân số
3. Đề xuất chính sách (nếu cần)
4. Cảnh báo rủi ro (nếu có)

Viết bằng tiếng Việt, ngắn gọn, dễ hiểu."""

        if self.use_gemini and self.model:
            return self._call_gemini(prompt)
        elif not self.use_gemini and self.client:
            return self._call_openai(prompt)
        else:
            return self._mock_insights(model_metrics, forecast_data, country_data)
    
    def chat(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Chat with AI assistant
        Args:
            message: User message
            context: Optional context (country data, model results, etc.)
        Returns:
            AI response
        """
        context_str = ""
        if context:
            context_str = f"\n\nContext:\n- Country: {context.get('country', 'N/A')}\n"
            if context.get('model_metrics'):
                context_str += f"- Model R²: {context['model_metrics'].get('val_r2', 0):.3f}\n"
        
        prompt = f"""Bạn là một trợ lý AI chuyên về phân tích dân số và nhân khẩu học. 
Bạn có thể trả lời các câu hỏi về dân số, xu hướng nhân khẩu, dự báo dân số, và các chính sách liên quan.
{context_str}

Câu hỏi của người dùng: {message}

Hãy trả lời một cách chuyên nghiệp, chính xác và dễ hiểu bằng tiếng Việt."""

        if self.use_gemini and self.model:
            response = self._call_gemini_chat(prompt)
            return response
        elif not self.use_gemini and self.client:
            response = self._call_openai_chat(prompt)
            return response
        else:
            return self._mock_chat(message)
    
    def _call_gemini(self, prompt: str) -> List[str]:
        """Call Gemini API"""
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            # Parse response into bullet points
            insights = [line.strip() for line in text.split('\n') if line.strip() and line.strip().startswith(('•', '-', '*', '1.', '2.', '3.'))]
            if not insights:
                insights = [text]
            return insights[:5]  # Return max 5 insights
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return ["Lỗi khi gọi GenAI API. Vui lòng kiểm tra API key."]
    
    def _call_openai(self, prompt: str) -> List[str]:
        """Call OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            text = response.choices[0].message.content
            insights = [line.strip() for line in text.split('\n') if line.strip() and line.strip().startswith(('•', '-', '*', '1.', '2.', '3.'))]
            if not insights:
                insights = [text]
            return insights[:5]
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return ["Lỗi khi gọi GenAI API. Vui lòng kiểm tra API key."]
    
    def _call_gemini_chat(self, prompt: str) -> str:
        """Call Gemini for chat"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return "Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại."
    
    def _call_openai_chat(self, prompt: str) -> str:
        """Call OpenAI for chat"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return "Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại."
    
    def _get_top_feature(self, feature_importance: Dict) -> str:
        """Get top important feature"""
        if not feature_importance:
            return "N/A"
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        return sorted_features[0][0] if sorted_features else "N/A"
    
    def _mock_insights(self, model_metrics: Dict, forecast_data: Dict, country_data: Dict) -> List[str]:
        """Mock insights when API is not available"""
        insights = []
        r2 = model_metrics.get('val_r2', 0)
        
        if r2 > 0.9:
            insights.append(f"🤖 Mô hình AI với độ chính xác R²={r2*100:.1f}% - Độ chính xác rất cao")
        elif r2 > 0.8:
            insights.append(f"📊 Độ chính xác R²={r2*100:.1f}% - Độ chính xác cao")
        else:
            insights.append(f"📊 Độ chính xác R²={r2*100:.1f}% - Tốt")
        
        insights.append(f"⚡ RMSE: {model_metrics.get('val_rmse', 0):.3f}% - Sai số trung bình")
        
        stage = country_data.get('stage', 3)
        if stage == 2:
            insights.append("🚀 Giai đoạn bùng nổ - Cần đầu tư mạnh")
        elif stage == 3:
            insights.append("⚡ Cơ cấu dân số vàng - Cơ hội kinh tế lớn")
        elif stage >= 4:
            insights.append("⚠️ Già hóa dân số - Cần chính sách hỗ trợ")
        
        growth = forecast_data.get('growthRate', 0)
        if growth > 0:
            insights.append(f"🔮 AI dự báo tăng {growth:.2f}% trong {forecast_data.get('years', 10)} năm")
        else:
            insights.append(f"🔮 AI dự báo giảm {abs(growth):.2f}% trong {forecast_data.get('years', 10)} năm")
        
        return insights
    
    def _mock_chat(self, message: str) -> str:
        """Mock chat response when API is not available"""
        message_lower = message.lower()
        
        if 'dân số' in message_lower or 'population' in message_lower:
            return "Tôi có thể giúp bạn phân tích dân số. Hãy cho tôi biết quốc gia bạn muốn tìm hiểu."
        elif 'dự báo' in message_lower or 'forecast' in message_lower:
            return "Mô hình XGBoost của chúng tôi sử dụng các yếu tố như tỷ lệ sinh, tử, GDP, và các chỉ số xã hội để dự báo dân số."
        elif 'mô hình' in message_lower or 'model' in message_lower:
            return "Chúng tôi sử dụng XGBoost, một mô hình machine learning mạnh mẽ để dự báo tăng trưởng dân số."
        else:
            return "Tôi hiểu câu hỏi của bạn. Để có câu trả lời chính xác hơn, vui lòng cung cấp thêm context hoặc kết nối GenAI API."

