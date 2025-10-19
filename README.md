# 📄 Document Intelligence Platform

AI-powered document processing platform with OCR, classification, and NER using Azure AI services.

## 🎯 Overview

Multi-tenant SaaS for intelligent document processing:
- 📤 Upload documents (PDF, images, DOCX)
- 🤖 Automated OCR & field extraction (Azure Document Intelligence)
- 🏷️ AI classification (8+ document types)
- 📊 Named Entity Recognition (vendors, amounts, dates)
- 💬 GPT-4o summarization
- ⚙️ Async background processing
- 👥 Multi-tenant architecture

## 🛠️ Tech Stack

**Backend:**
- Python 3.11+
- FastAPI (async web framework)
- SQLAlchemy + PostgreSQL
- Celery + Redis (background jobs)
- Pydantic (validation)

**AI Services:**
- Azure Document Intelligence (Form Recognizer)
- Azure OpenAI (GPT-4o-mini)
- Transformers + PyTorch (NER)

**Storage:**
- Azure Blob Storage (documents)
- PostgreSQL (metadata)
- Redis (cache + queue)

**Frontend:**
- Streamlit (quick dashboard)
- OR Angular 17 (for full SPA)
- still in progress

**Infrastructure:**
- Docker + Docker Compose
- Terraform (Azure IaC)
- GitHub Actions (CI/CD)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker Desktop
- Azure subscription (Document Intelligence + OpenAI + Storage)

### Local Setup

```bash
# Clone repo
git clone <your-repo-url>
cd doc-intelligence-platform

# Copy environment
cp .env.example .env
# Edit .env with your Azure credentials

# Start services
docker-compose up -d

# Wait for services to be ready
sleep 10

# Run API
cd app
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000
Docs: http://localhost:8000/docs

### Test Upload

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@test-invoice.pdf" \
  -F "tenant_id=demo"
```

## 📁 Project Structure

```
doc-intelligence-platform/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── api/
│   │   ├── routes_documents.py    # Document CRUD
│   │   ├── routes_upload.py       # Upload endpoints
│   │   └── routes_analytics.py    # Stats & metrics
│   ├── services/
│   │   ├── document_intelligence.py  # Azure Form Recognizer
│   │   ├── openai_service.py         # GPT classification/summary
│   │   ├── ner_service.py            # Transformers NER
│   │   └── storage_service.py        # Blob storage
│   ├── workers/
│   │   └── process_documents.py   # Celery background tasks
│   ├── models/
│   │   ├── database.py            # SQLAlchemy models
│   │   └── schemas.py             # Pydantic schemas
│   ├── core/
│   │   ├── config.py              # Settings
│   │   ├── database.py            # DB connection
│   │   └── deps.py                # Dependencies
│   └── requirements.txt
├── tests/
│   ├── test_upload.py
│   └── test_processing.py
├── frontend/                      # Streamlit dashboard
│   └── app.py
├── infra/                         # Terraform
│   ├── main.tf
│   └── variables.tf
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── README.md
```

## 🎓 Features Roadmap

### ✅ Phase 1: Core Backend (Week 1)
- [x] FastAPI setup
- [ ] Document upload API
- [ ] Blob storage integration
- [ ] Database models
- [ ] Basic CRUD operations

### 🔄 Phase 2: AI Processing (Week 2)
- [ ] Azure Document Intelligence integration
- [ ] OCR & field extraction
- [ ] Background job processing (Celery)
- [ ] Document classification (GPT-4o)

### 📋 Phase 3: NLP & Enhancement (Week 3)
- [ ] NER with transformers
- [ ] GPT-4o summarization
- [ ] Multi-language support
- [ ] Confidence scoring

### 🎨 Phase 4: Frontend (Week 4)
- [ ] Streamlit dashboard
- [ ] Document library UI
- [ ] Upload interface
- [ ] Analytics charts

### 🔐 Phase 5: Multi-tenancy (Week 5)
- [ ] JWT authentication
- [ ] Tenant isolation
- [ ] Role-based access
- [ ] Usage tracking

### 🚢 Phase 6: DevOps (Week 6)
- [ ] Docker optimization
- [ ] Terraform infrastructure
- [ ] GitHub Actions CI/CD
- [ ] Azure deployment

## 🔧 API Endpoints

```
POST   /api/documents/upload          Upload document
GET    /api/documents                 List documents
GET    /api/documents/{id}            Get document details
POST   /api/documents/{id}/reprocess  Trigger reprocessing
DELETE /api/documents/{id}            Delete document
GET    /api/analytics/stats           Usage statistics
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_upload.py -v
```

## 📚 Resources

- [Azure Document Intelligence](https://learn.microsoft.com/azure/ai-services/document-intelligence/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Celery](https://docs.celeryq.dev/)
- [Transformers](https://huggingface.co/docs/transformers/)

## 📝 License

MIT

## 👤 Author

Jakub Szuper
