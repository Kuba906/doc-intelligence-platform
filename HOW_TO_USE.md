# 📦 How to Use This Starter

## Option 1: Copy from Desktop (Easiest)

```bash
# The project is ready at:
/Users/jakubszuper/Desktop/doc-intelligence-platform/

# Just cd into it:
cd /Users/jakubszuper/Desktop/doc-intelligence-platform

# Initialize git
git init
git add .
git commit -m "Initial commit: Doc Intelligence Platform"

# Create GitHub repo (web), then:
git remote add origin https://github.com/YOUR_USERNAME/doc-intelligence-platform.git
git push -u origin main
```

## Option 2: Create ZIP for Backup

```bash
cd /Users/jakubszuper/Desktop

# Create ZIP
tar -czf doc-intelligence-platform.tar.gz doc-intelligence-platform/

# Or use Finder: Right-click → Compress
```

---

## 🗂️ Project Structure

```
doc-intelligence-platform/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt        # Python dependencies
│   ├── api/                    # API routes
│   │   ├── routes_upload.py    # Upload endpoints
│   │   ├── routes_documents.py # CRUD endpoints
│   │   └── routes_analytics.py # Stats endpoints
│   ├── services/               # Business logic
│   │   ├── storage_service.py        # Azure Blob Storage
│   │   ├── document_intelligence.py  # Azure Form Recognizer
│   │   ├── openai_service.py         # GPT classification/summary
│   │   └── ner_service.py            # Transformers NER
│   ├── workers/                # Background jobs
│   │   ├── celery_app.py
│   │   └── process_documents.py
│   ├── models/                 # Data models
│   │   ├── database.py         # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   └── core/                   # Core utilities
│       ├── config.py
│       └── database.py
├── tests/                      # Tests (TODO)
├── frontend/                   # Streamlit dashboard (TODO)
├── infra/                      # Terraform (TODO)
├── docker-compose.yml          # Local dev environment
├── Dockerfile                  # Container image
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── Makefile                    # Helper commands
├── README.md                   # Project overview
├── QUICKSTART.md               # 15-min setup guide
└── GET_STARTED.md              # Your next steps
```

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd doc-intelligence-platform

# Copy env file
cp .env.example .env

# Edit .env (optional - mocks work without Azure)
nano .env
```

### 2. Start Services

```bash
# Start PostgreSQL + Redis + Azurite
docker-compose up -d

# Wait for services to be ready
sleep 10
```

### 3. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install
pip install -r app/requirements.txt
```

### 4. Run API

```bash
cd app
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Open:** http://localhost:8000/docs

### 5. Test Upload

```bash
# Create test file
echo "Invoice #123 from Acme Corp, Total: $999.99" > invoice.txt

# Upload
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@invoice.txt" \
  -F "tenant_id=demo"

# List
curl "http://localhost:8000/api/documents?tenant_id=demo"
```

### 6. Start Worker (for processing)

```bash
# In new terminal
cd app
source venv/bin/activate
celery -A workers.celery_app worker --loglevel=info
```

---

## 📝 What's Included

### ✅ Working Features:
- FastAPI REST API with Swagger docs
- Document upload to Blob Storage
- Database models (PostgreSQL)
- Background job processing (Celery + Redis)
- Mock AI services (no Azure needed initially)
- Multi-tenant architecture
- Error handling & logging
- Docker Compose for local dev

### 🔄 With Mock Responses (works without Azure):
- Document Intelligence (returns fake extracted fields)
- OpenAI classification (returns mock document type)
- NER (transformers work locally!)

### 🔧 To Implement (Week 1-4):
- Real Azure Document Intelligence integration
- Real Azure OpenAI integration
- Frontend dashboard (Streamlit or Angular)
- Tests
- Terraform infrastructure
- CI/CD pipeline

---

## 🎯 Development Workflow

### Typical Development Session:

```bash
# Terminal 1: Start services
docker-compose up

# Terminal 2: Run API
cd app
source venv/bin/activate
uvicorn main:app --reload

# Terminal 3: Run worker
cd app
source venv/bin/activate
celery -A workers.celery_app worker --loglevel=info

# Terminal 4: Development (coding, testing)
code .
```

### Making Changes:

1. **Edit code** in app/
2. **FastAPI auto-reloads** (see Terminal 2)
3. **Test in Swagger:** http://localhost:8000/docs
4. **Check logs** in terminal
5. **Commit:** `git add . && git commit -m "Added feature X"`

---

## 🔑 Environment Variables

**Minimum (works with mocks):**
```bash
DATABASE_URL=postgresql://docuser:docpass@localhost:5432/docintel
REDIS_URL=redis://localhost:6379/0
```

**With Azure (production):**
```bash
# Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://...
AZURE_DOCUMENT_INTELLIGENCE_KEY=...

# OpenAI (reuse from RAG project!)
AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT_CHAT=gpt-4o-mini

# Storage
AZURE_STORAGE_CONNECTION_STRING=...
```

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_upload.py -v
```

---

## 📦 Deployment

### Local Docker:
```bash
docker-compose up --build
```

### Azure (TODO Week 6):
```bash
cd infra
terraform init
terraform apply
```

---

## 🆘 Troubleshooting

### API won't start:
```bash
# Check if port 8000 is free
lsof -i :8000

# Kill process if needed
kill -9 <PID>
```

### Database connection error:
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart
docker-compose restart postgres
```

### Worker not processing:
```bash
# Check Redis
docker ps | grep redis

# Check Celery logs
celery -A workers.celery_app worker --loglevel=debug
```

### Import errors:
```bash
# Make sure you're in app/ directory
cd app

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 🎓 Learning Resources

**Read in order:**
1. README.md - Project overview
2. QUICKSTART.md - 15-min setup
3. GET_STARTED.md - Next steps
4. This file - How to use

**Code walkthrough:**
1. app/main.py - FastAPI setup
2. app/api/routes_upload.py - Upload logic
3. app/workers/process_documents.py - Background processing
4. app/services/* - AI services integration

---

## 🚀 Next Steps

1. ✅ Read GET_STARTED.md
2. ✅ Create GitHub repo
3. ✅ Test locally
4. ✅ Setup Azure Document Intelligence (FREE tier)
5. ✅ Start Week 1 development

---

## 💡 Tips

**Use make commands:**
```bash
make help        # See all commands
make setup       # Initial setup
make dev-up      # Start services
make api         # Run API
make worker      # Run Celery worker
make test        # Run tests
```

**VS Code setup:**
```bash
# Open project
code .

# Install Python extension
# Select Python interpreter: ./venv/bin/python
# Open Terminal in VS Code: auto-activates venv
```

**Git workflow:**
```bash
# Feature branch
git checkout -b feature/week1-upload
git add .
git commit -m "Implemented upload API"
git push origin feature/week1-upload
```

---

## ✅ You're All Set!

**You have:**
- Complete FastAPI starter
- Mock AI services (works without Azure)
- Background processing (Celery)
- Docker environment
- Full documentation

**Start coding!** 💻🚀
