# Quick Start - Document Intelligence Platform

Get the project running in 15 minutes!

## Prerequisites

```bash
# Check Python
python --version  # Need 3.11+

# Check Docker
docker --version
docker-compose --version
```

## Step 1: Clone & Setup (2 min)

```bash
cd doc-intelligence-platform

# Copy environment
cp .env.example .env

# For now, leave Azure keys empty - we'll use mocks for quick testing
```

## Step 2: Start Services (3 min)

```bash
# Start PostgreSQL, Redis, Azurite
docker-compose up -d postgres redis azurite

# Wait for services
sleep 10
```

## Step 3: Install Python Dependencies (5 min)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r app/requirements.txt
```

## Step 4: Run API (2 min)

```bash
# Run FastAPI
cd app
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**API running:** http://localhost:8000
**Swagger docs:** http://localhost:8000/docs

## Step 5: Test Upload (1 min)

```bash
# Create test file
echo "INVOICE\nCompany: Acme Corp\nTotal: $1,234.56" > test-invoice.txt

# Upload
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@test-invoice.txt" \
  -F "tenant_id=demo"

# Should return:
# {
#   "id": "uuid-here",
#   "filename": "test-invoice.txt",
#   "status": "uploaded",
#   "uploaded_at": "2024-10-18T..."
# }
```

## Step 6: Check Processing (1 min)

```bash
# List documents
curl http://localhost:8000/api/documents?tenant_id=demo

# Get details (use ID from step 5)
curl http://localhost:8000/api/documents/{id}
```

## Step 7: Start Celery Worker (to actually process)

```bash
# In new terminal
cd app
celery -A workers.celery_app worker --loglevel=info
```

Now upload again and document will be auto-processed!

## With Azure Services (Production)

### Setup Azure Document Intelligence

```bash
# Create resource (FREE tier!)
az cognitiveservices account create \
  --name doc-intel-demo \
  --resource-group your-rg \
  --kind FormRecognizer \
  --sku F0 \
  --location westeurope

# Get credentials
az cognitiveservices account show \
  --name doc-intel-demo \
  --resource-group your-rg \
  --query "properties.endpoint"

az cognitiveservices account keys list \
  --name doc-intel-demo \
  --resource-group your-rg
```

Update `.env`:
```
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://doc-intel-demo.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-key
```

### Use Existing Azure OpenAI (from RAG project!)

Update `.env` with same credentials as RAG project:
```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT_CHAT=gpt-4o-mini
```

## Next Steps

1. Read [README.md](README.md) for full overview
2. See [DEVELOPMENT.md](DEVELOPMENT.md) for Week 1-6 plan
3. Customize for your use case!

## Troubleshooting

**"Connection refused" to PostgreSQL:**
```bash
docker ps | grep postgres
docker logs docintel-postgres
```

**"No module named 'app'":**
```bash
# Make sure you're in the app/ directory
cd app
python -m uvicorn main:app --reload
```

**Celery not processing:**
```bash
# Check Redis
docker logs docintel-redis

# Check Celery logs
celery -A workers.celery_app worker --loglevel=debug
```

## Success!

You now have:
- ✅ FastAPI running on :8000
- ✅ Document upload working
- ✅ Background processing (Celery)
- ✅ Mock AI services (or real Azure if configured)

**Ready to build Week 1 features!** 🚀
