# Quick Start Guide

## Hướng dẫn nhanh để chạy Backend

### 1. Cài đặt dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Cấu hình môi trường (Tùy chọn)

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Chỉnh sửa `.env` nếu cần:
- `OPENAI_API_KEY` hoặc `GEMINI_API_KEY` - Để sử dụng GenAI
- `DATABASE_URL` - PostgreSQL connection string (hoặc để mặc định dùng SQLite)

### 3. Khởi tạo database (Tùy chọn)

Nếu muốn sử dụng dữ liệu mẫu:

```bash
python scripts/init_data.py
```

### 4. Chạy server

```bash
python -m app.main
```

Hoặc:

```bash
uvicorn app.main:app --reload
```

Server sẽ chạy tại `http://localhost:8000`

### 5. Test API

Mở browser: `http://localhost:8000/docs` để xem Swagger UI

Hoặc chạy example:

```bash
python example_usage.py
```

## API Endpoints chính

### 1. Train Model
```bash
POST /api/train
Body: {
  "countries_data": [...]
}
```

### 2. Predict Population
```bash
POST /api/predict
Body: {
  "country_data": {...},
  "years": 10,
  "use_rag": false
}
```

### 3. Get AI Insights
```bash
POST /api/ai-insights
Body: {
  "model_metrics": {...},
  "forecast_data": {...},
  "country_data": {...}
}
```

### 4. Chat with AI
```bash
POST /api/chat
Body: {
  "message": "Câu hỏi của bạn",
  "context": {...}
}
```

## Lưu ý

1. **Database**: Nếu không có PostgreSQL, hệ thống sẽ tự động dùng SQLite (phù hợp cho development)
2. **GenAI API**: Nếu không có API key, hệ thống sẽ dùng mock responses
3. **Model**: Model sẽ được lưu tại `./models/xgboost_model.pkl` sau khi train
4. **Vector DB**: RAG system sẽ lưu vector database tại `./vector_db`

## Troubleshooting

### Lỗi "Model chưa được huấn luyện"
- Chạy `POST /api/train` trước khi predict

### Lỗi database connection
- Kiểm tra `DATABASE_URL` trong `.env`
- Hoặc để mặc định để dùng SQLite

### Lỗi GenAI API
- Kiểm tra API key trong `.env`
- Hệ thống vẫn hoạt động với mock responses nếu không có API key

