# Population Dynamics AI Backend

Backend API cho hệ thống dự báo dân số với AI sử dụng Python, FastAPI, XGBoost, và GenAI.

## Tính năng chính

1. **Mô hình XGBoost thực sự**: Huấn luyện và dự báo dân số với XGBoost Python
2. **Tích hợp GenAI**: Sử dụng OpenAI hoặc Google Gemini API cho phân tích và chat
3. **RAG System**: Hệ thống RAG để điều chỉnh dự báo dựa trên tin tức/chính sách
4. **Data Pipeline**: Tự động thu thập dữ liệu từ World Bank và UN
5. **Database**: Lưu trữ dữ liệu với PostgreSQL

## Cài đặt

### 1. Cài đặt dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Cấu hình môi trường

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Điền các API keys:
- `OPENAI_API_KEY` hoặc `GEMINI_API_KEY`
- `DATABASE_URL` (PostgreSQL connection string)

### 3. Khởi tạo database

```bash
python -c "from app.database import init_db; init_db()"
```

### 4. Chạy server

```bash
python -m app.main
```

Server sẽ chạy tại `http://localhost:8000`

## API Endpoints

### Prediction
- `POST /api/predict` - Dự báo dân số
- `GET /api/model/status` - Trạng thái mô hình

### Training
- `POST /api/train` - Huấn luyện mô hình
- `GET /api/train/status` - Trạng thái training

### AI Insights
- `POST /api/ai-insights` - Tạo phân tích AI

### Chat
- `POST /api/chat` - Chat với AI assistant

### Data Pipeline
- `POST /api/data-pipeline/update` - Cập nhật dữ liệu
- `POST /api/data-pipeline/scrape` - Scrape dữ liệu một quốc gia

## Cấu trúc dự án

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py          # Database models
│   ├── models/
│   │   └── xgboost_model.py # XGBoost model
│   ├── services/
│   │   ├── genai_service.py # GenAI integration
│   │   ├── rag_service.py   # RAG system
│   │   └── data_pipeline.py # Data collection
│   └── routers/
│       ├── predict.py       # Prediction endpoints
│       ├── train.py         # Training endpoints
│       ├── ai_insights.py   # AI insights endpoints
│       ├── chat.py          # Chat endpoints
│       └── data_pipeline.py # Data pipeline endpoints
├── requirements.txt
├── .env.example
└── README.md
```

## Sử dụng

### 1. Train model

```python
import requests

data = {
    "countries_data": [
        # Your country data here
    ]
}

response = requests.post("http://localhost:8000/api/train", json=data)
print(response.json())
```

### 2. Predict

```python
data = {
    "country_data": {
        "name": "Việt Nam",
        "population": 98800000,
        "birthRate": 14.8,
        "deathRate": 7.2,
        # ... other features
    },
    "years": 10,
    "use_rag": True  # Enable RAG adjustments
}

response = requests.post("http://localhost:8000/api/predict", json=data)
print(response.json())
```

## Lưu ý

- Cần có API key của OpenAI hoặc Gemini để sử dụng GenAI
- Cần cài đặt PostgreSQL để lưu trữ dữ liệu
- Model sẽ được lưu tại `./models/xgboost_model.pkl`
- Vector DB cho RAG tại `./vector_db`

