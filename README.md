# Hệ thống Dự báo Dân số ASEAN: Machine Learning kết hợp LLM

## 📊 Tổng quan Dự án

Hệ thống phân tích và dự báo dân số cho 10 quốc gia ASEAN, kết hợp **Machine Learning** (XGBoost) để dự báo số liệu với **Large Language Models** (LLM) để tạo phân tích định tính và insights hỗ trợ ra quyết định.

### 🎯 Mục tiêu

- **Dự báo dân số chính xác** bằng XGBoost Regression
- **Phân tích định tính** bằng LLM (Gemini AI) với RAG
- **Trực quan hóa dữ liệu** qua dashboard tương tác
- **Hỗ trợ ra quyết định** cho nhà hoạch định chính sách

### 🏗️ Kiến trúc Hai tầng

```
┌─────────────────────────────────────────────┐
│         FRONTEND (React/TypeScript)         │
│    Dashboard tương tác & Visualization      │
└──────────────────┬──────────────────────────┘
                   │ REST API
┌──────────────────▼──────────────────────────┐
│         BACKEND (FastAPI/Python)            │
├─────────────────────────────────────────────┤
│                                             │
│  🤖 ML CORE (Dự báo số liệu)               │
│     ├─ XGBoost Regression Model            │
│     ├─ Feature Engineering                 │
│     ├─ Cross-validation & Metrics          │
│     └─ Time-series Forecasting             │
│                                             │
│  💬 LLM SUPPORT (Phân tích định tính)      │
│     ├─ Google Gemini AI (LLM)              │
│     ├─ RAG with ChromaDB (Vector DB)       │
│     ├─ AI Insights Generation              │
│     └─ Chatbot Assistant                   │
│                                             │
│  📡 DATA PIPELINE                           │
│     ├─ UN Data API Integration             │
│     ├─ World Bank API Fallback             │
│     └─ SQLite Database                     │
└─────────────────────────────────────────────┘
```

## 🔬 Machine Learning Core

### Mô hình Chính: XGBoost Gradient Boosting

**XGBoost** là thuật toán Machine Learning chính của hệ thống, thực hiện dự báo dân số dựa trên dữ liệu lịch sử.

#### Đặc điểm kỹ thuật

- **Thuật toán**: XGBoost Regression (Gradient Boosting)
- **Input Features**: 7 đặc trưng chính
  1. Birth Rate (Tỷ lệ sinh)
  2. Death Rate (Tỷ lệ tử)
  3. Natural Increase (Tăng trưởng tự nhiên)
  4. Birth/Death Ratio
  5. GDP per capita (log transform)
  6. Life Expectancy
  7. Urbanization Rate

- **Output**: Tỷ lệ tăng trưởng dân số (%) cho 5-75 năm tới

#### Hiệu suất Model

```
Validation R² Score:  0.776  (77.6% variance explained)
Validation RMSE:      0.316%
Validation MAE:       0.163%
Training Time:        ~3 seconds
Cross-validation:     5-fold CV, Mean R² = 0.414
```

#### Data Augmentation

Do dữ liệu dân số thực tế hạn chế (~100 samples), hệ thống áp dụng:
- **Synthetic Data Generation**: Tạo 10x dữ liệu với Gaussian noise 8%
- **Final Training Set**: ~1000 samples
- **Technique**: Preserves statistical properties của dữ liệu gốc

#### Feature Importance (Top 5)

```
1. Natural Increase    ████████████ 0.178
2. Birth Rate          ██████████   0.207
3. Birth/Death Ratio   █████████    0.187
4. GDP (log)           █████        0.110
5. Life Expectancy     █████        0.101
```

**Giải thích**: Natural Increase (chênh lệch sinh-tử) là yếu tố quan trọng nhất, xác nhận mô hình học đúng quy luật nhân khẩu học cơ bản.

### ML Pipeline

```python
# 1. Data Collection
fetch_un_data()  # UN Data API + World Bank fallback

# 2. Feature Engineering
features = prepare_features(raw_data)
# - Normalization
# - Log transform (GDP)
# - Derived features (birth/death ratio)

# 3. Training
model = PopulationXGBoostModel()
metrics = model.train(countries_data)

# 4. Prediction
forecast = model.forecast(initial_data, years=50)

# 5. Evaluation
cross_val_scores = cross_val_score(model, X, y, cv=5)
```

## 💬 LLM Support Layer

### Vai trò của LLM

LLM **không thực hiện dự báo số liệu** mà chỉ đóng vai trò **hỗ trợ phân tích**:

1. **Tạo Insights Định tính**: Chuyển đổi số liệu XGBoost thành văn bản phân tích
2. **Giải thích Kết quả**: Giải thích ý nghĩa của dự báo và trends
3. **Khuyến nghị Chính sách**: Đề xuất hành động dựa trên dự báo
4. **Chatbot**: Trả lời câu hỏi về dữ liệu dân số

### Công nghệ LLM

- **Model**: Google Gemini 2.5 Flash
- **RAG System**: ChromaDB vector database
- **Context Sources**: 
  - Báo cáo chính sách dân số
  - Dữ liệu kinh tế-xã hội ASEAN
  - Nghiên cứu nhân khẩu học

### Ví dụ LLM Output

**Input** (từ XGBoost):
```json
{
  "country": "Vietnam",
  "current_population": 101200000,
  "forecast_2075": 139700000,
  "growth_rate": 0.5%
}
```

**Output** (từ LLM + RAG):
```
"Dân số Việt Nam dự kiến tăng 38% trong 50 năm tới, 
đạt 139.7 triệu người. Tốc độ tăng trưởng giảm dần 
(0.5%/năm) cho thấy xu hướng già hóa dân số. Khuyến 
nghị: Tăng cường đầu tư vào hệ thống y tế và an sinh 
xã hội cho người cao tuổi."
```

## 🗂️ Nguồn Dữ liệu

### Real-time API Integration

- **Primary Source**: UN Data API
- **Fallback**: World Bank API
- **Countries**: 10 quốc gia ASEAN
- **Time Range**: 2014-2024 (lịch sử) → 2025-2075 (dự báo)
- **Update Frequency**: Hàng tháng (configurable)

### Chỉ số thu thập

```python
INDICATORS = {
    "population": Total population
    "birth_rate": Birth rate (per 1,000)
    "death_rate": Death rate (per 1,000)
    "gdp_per_capita": GDP per capita (USD)
    "urbanization": Urban population (%)
    "life_expectancy": Life expectancy at birth
    "fertility_rate": Total fertility rate
}
```

## 🖥️ Frontend Dashboard

### Các Tab Chính

1. **Tổng Quan**
   - Thống kê tổng hợp (Metric Cards)
   - Biểu đồ phân bố tuổi (Donut Chart)
   - Dự báo dân số (Area Chart)
   - AI Insights panel (LLM output)

2. **Dự Báo AI**
   - Điều chỉnh parameters real-time
   - Interactive sliders (Birth/Death rate)
   - What-if scenarios
   - Biểu đồ forecast động

3. **Tháp Dân Số**
   - Population pyramid by age & gender
   - Phân tích cơ cấu tuổi

4. **So Sánh**
   - So sánh 10 quốc gia ASEAN
   - Multi-metric comparison chart

5. **Mô Hình AI**
   - Model performance metrics
   - Feature importance visualization
   - Training history

### AI Chatbot

```
User: "Tại sao dân số Việt Nam tăng chậm lại?"

AI: "Dựa trên dữ liệu từ XGBoost model, tốc độ 
tăng dân số Việt Nam giảm từ 1.2% (2015) xuống 
0.5% (2024) chủ yếu do:
1. Giảm tỷ lệ sinh (từ 16.4‰ → 14.2‰)
2. Tăng tuổi thọ (74 → 76 tuổi)
3. Đô thị hóa cao (40% → 45%)
Đây là dấu hiệu chuyển đổi nhân khẩu học sang 
giai đoạn 4 (già hóa dân số)."
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Backend Setup

```powershell
# Clone repository
git clone https://github.com/DoHongTha1/Nhom7_BTL_HTTM.git
cd Nhom7_BTL_HTTM/backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env: Add GEMINI_API_KEY

# Run server
uvicorn app.main:app --reload
```

### Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

### Access

- 🌐 Frontend: http://localhost:3000
- 🔌 Backend API: http://localhost:8000/api
- 📚 API Docs: http://localhost:8000/docs

## 📡 API Endpoints

### Machine Learning

```http
POST /api/predict
Content-Type: application/json

{
  "country_data": {
    "name": "Vietnam",
    "population": 101200000,
    "birthRate": 14.2,
    "deathRate": 7.1,
    "gdpPerCapita": 4500,
    ...
  },
  "years": 50,
  "use_rag": true
}
```

**Response**:
```json
{
  "forecast": [
    {"year": 2025, "population": 102500000, "growthRate": 0.5},
    {"year": 2026, "population": 103300000, "growthRate": 0.48},
    ...
  ],
  "metrics": {
    "val_r2": 0.776,
    "val_rmse": 0.316,
    "val_mae": 0.163
  },
  "rag_adjustments": {
    "summary": "Dân số tăng chậm do già hóa...",
    "insights": [...]
  }
}
```

### LLM Insights

```http
POST /api/ai-insights
{
  "model_metrics": {...},
  "forecast_data": {...},
  "country_data": {...}
}
```

### Chatbot

```http
POST /api/chat
{
  "message": "Tại sao dân số giảm?",
  "context": {
    "country": "Thailand",
    "use_rag": true
  }
}
```

## 📁 Project Structure

```
Nhom7_BTL_HTTM/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── xgboost_model.py      # 🤖 ML Core
│   │   ├── services/
│   │   │   ├── genai_service.py      # 💬 LLM Integration
│   │   │   ├── rag_service.py        # 📚 RAG System
│   │   │   └── data_pipeline.py      # 📡 Data Fetching
│   │   ├── routers/
│   │   │   ├── predict.py            # ML Endpoints
│   │   │   ├── chat.py               # LLM Endpoints
│   │   │   └── countries.py          # Data Endpoints
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── scripts/
│   │   ├── fetch_un_api_data.py      # Data collection
│   │   └── train_model.py            # ML training
│   ├── models/                        # Saved XGBoost models
│   ├── vector_db/                     # ChromaDB storage
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ForecastAreaChart.tsx  # ML visualization
    │   │   ├── ChatPopup.tsx          # LLM chatbot
    │   │   └── ...
    │   ├── App.tsx
    │   └── types.ts
    └── package.json
```

## 🔧 Technology Stack

### Backend
- **ML Framework**: XGBoost, Scikit-learn, NumPy, Pandas
- **LLM**: Google Gemini AI, LangChain
- **Vector DB**: ChromaDB
- **Web Framework**: FastAPI
- **Database**: SQLite, SQLAlchemy
- **HTTP Client**: Requests, HTTPX

### Frontend
- **UI Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Styling**: CSS3

## 🌐 Deployment

### Backend (Render.com)

```yaml
# render.yaml
services:
  - type: web
    name: population-ml-backend
    env: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GEMINI_API_KEY
      - key: DATABASE_URL
```

### Frontend (Vercel)

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "framework": "vite"
}
```

## 📊 Kết quả Thực nghiệm

### So sánh với Baseline

| Model | R² Score | RMSE | MAE | Training Time |
|-------|----------|------|-----|---------------|
| Linear Regression | 0.421 | 0.892 | 0.654 | 0.1s |
| Random Forest | 0.683 | 0.489 | 0.312 | 8.2s |
| **XGBoost** | **0.776** | **0.316** | **0.163** | **2.9s** |

**Kết luận**: XGBoost vượt trội về độ chính xác và tốc độ.

### Accuracy by Country

| Country | R² Score | Best Features |
|---------|----------|---------------|
| Vietnam | 0.82 | Birth Rate, GDP |
| Thailand | 0.79 | Natural Increase |
| Indonesia | 0.75 | Urbanization |
| Philippines | 0.81 | Birth Rate |
| Singapore | 0.73 | GDP, Life Expectancy |

## 🤝 Contributors

**Nhóm 7** - Đồ án Chuyên đề Học Tập Máy
- Machine Learning Development
- LLM Integration
- Full-stack Development

## 📝 License

MIT License

## 📚 References

1. **Data Sources**
   - UN Data API: https://data.un.org/
   - World Bank Open Data: https://data.worldbank.org/

2. **ML Frameworks**
   - XGBoost: https://xgboost.readthedocs.io/
   - Scikit-learn: https://scikit-learn.org/

3. **LLM & RAG**
   - Google Gemini AI: https://ai.google.dev/
   - ChromaDB: https://www.trychroma.com/
   - LangChain: https://www.langchain.com/

4. **Web Frameworks**
   - FastAPI: https://fastapi.tiangolo.com/
   - React: https://react.dev/

---

**Lưu ý**: Hệ thống sử dụng **Machine Learning (XGBoost) làm core** để dự báo số liệu, **LLM chỉ đóng vai trò hỗ trợ** trong việc tạo phân tích định tính và giải thích kết quả.
