# Kiến trúc hệ thống

## Tổng quan

Hệ thống Population Dynamics AI Backend được xây dựng theo kiến trúc Client-Server với các thành phần chính:

### 1. Backend API (FastAPI)
- **Framework**: FastAPI (Python)
- **Port**: 8000
- **Chức năng**: Xử lý toàn bộ logic nghiệp vụ, huấn luyện mô hình, dự báo

### 2. Mô hình XGBoost
- **Thư viện**: XGBoost Python (xgboost)
- **Lưu trữ**: `./models/xgboost_model.pkl`
- **Chức năng**: Dự báo tăng trưởng dân số

### 3. GenAI Service
- **APIs**: OpenAI hoặc Google Gemini
- **Chức năng**: 
  - Phân tích đầu ra (AI Insights)
  - Chat với người dùng

### 4. RAG System
- **Vector DB**: ChromaDB
- **Embedding Model**: Sentence Transformers
- **Chức năng**: Điều chỉnh dự báo dựa trên tin tức/chính sách

### 5. Data Pipeline
- **Nguồn dữ liệu**: World Bank API, UN Data
- **Database**: PostgreSQL (hoặc SQLite cho development)
- **Scheduler**: Tự động cập nhật dữ liệu định kỳ

## Luồng dữ liệu

### Training Flow
```
Frontend/API → POST /api/train
    ↓
XGBoost Model → Train với countries_data
    ↓
Lưu model → ./models/xgboost_model.pkl
    ↓
Lưu metrics → Database
```

### Prediction Flow
```
Frontend → POST /api/predict
    ↓
[Optional] RAG Service → Thu thập tin tức → Điều chỉnh features
    ↓
XGBoost Model → Predict
    ↓
[Optional] GenAI Service → Generate insights
    ↓
Response → JSON với forecast + insights
```

### RAG Flow
```
User request với use_rag=true
    ↓
RAG Service → Query vector DB với country code
    ↓
Retrieve relevant news/articles
    ↓
GenAI → Phân tích và đề xuất adjustments
    ↓
Apply adjustments → Features
    ↓
XGBoost → Predict với adjusted features
```

## Cấu trúc thư mục

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration settings
│   ├── database.py           # Database models & connection
│   ├── utils.py              # Utility functions
│   ├── models/
│   │   └── xgboost_model.py  # XGBoost model class
│   ├── services/
│   │   ├── genai_service.py  # GenAI integration
│   │   ├── rag_service.py    # RAG system
│   │   └── data_pipeline.py  # Data collection
│   └── routers/
│       ├── predict.py        # Prediction endpoints
│       ├── train.py          # Training endpoints
│       ├── ai_insights.py    # AI insights endpoints
│       ├── chat.py           # Chat endpoints
│       └── data_pipeline.py  # Data pipeline endpoints
├── scripts/
│   ├── init_data.py         # Initialize database with sample data
│   └── scheduler.py         # Automated data updates
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── README.md                # Documentation
├── QUICKSTART.md            # Quick start guide
└── example_usage.py          # Example API usage
```

## API Endpoints

### Training
- `POST /api/train` - Huấn luyện mô hình
- `GET /api/train/status` - Trạng thái training

### Prediction
- `POST /api/predict` - Dự báo dân số
- `GET /api/model/status` - Trạng thái mô hình

### AI Insights
- `POST /api/ai-insights` - Tạo phân tích AI

### Chat
- `POST /api/chat` - Chat với AI assistant

### Data Pipeline
- `POST /api/data-pipeline/update` - Cập nhật dữ liệu
- `POST /api/data-pipeline/scrape` - Scrape dữ liệu một quốc gia

## Database Schema

### CountryData
- `id`: Primary key
- `country_code`: ISO country code
- `country_name`: Country name
- `year`: Year
- `population`: Population
- `birthRate`, `deathRate`: Demographic rates
- `gdpPerCapita`, `urbanization`: Economic indicators
- `educationIndex`, `healthcareSpending`: Social indicators
- `fertilityRate`, `medianAge`, `lifeExpectancy`: Demographic indicators
- `growthRate`: Calculated growth rate
- `stage`: Demographic transition stage

### ModelMetrics
- `id`: Primary key
- `model_version`: Version string
- `training_date`: Training date
- `r2_score`, `rmse`, `mae`: Metrics
- `feature_importance`: JSON
- `training_time`: Training time in seconds

### NewsArticle (RAG)
- `id`: Primary key
- `country_code`: Country code
- `title`, `content`: Article content
- `source`: News source
- `published_date`: Publication date
- `embedding`: Vector embedding (JSON)

## Cấu hình

Các biến môi trường trong `.env`:

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key
- `GEMINI_API_KEY`: Google Gemini API key
- `USE_GEMINI`: Use Gemini instead of OpenAI (true/false)
- `MODEL_DIR`: Directory for saved models
- `VECTOR_DB_PATH`: Path for ChromaDB
- `EMBEDDING_MODEL`: Sentence transformer model name
- `DATA_UPDATE_SCHEDULE`: Schedule for data updates (daily/weekly/monthly)

## Deployment

### Development
```bash
python -m app.main
# hoặc
uvicorn app.main:app --reload
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Tùy chọn)
Có thể tạo Dockerfile và docker-compose.yml để containerize ứng dụng.

## Mở rộng trong tương lai

1. **Authentication**: Thêm JWT authentication
2. **Rate Limiting**: Thêm rate limiting cho API
3. **Caching**: Redis cache cho predictions
4. **Monitoring**: Prometheus metrics
5. **Logging**: Structured logging với ELK stack
6. **News API Integration**: Tích hợp NewsAPI hoặc Google News
7. **Real-time Updates**: WebSocket cho real-time predictions

