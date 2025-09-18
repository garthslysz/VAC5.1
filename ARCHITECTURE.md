# Simplified gwsGPT Architecture

## Project Structure (Optimized for Local → Personal Azure → Enterprise)

```
gwsGPT/
├─ app/                           # Single FastAPI application
│  ├─ main.py                    # Main API with all endpoints
│  ├─ chat/                      # Chat functionality
│  │  ├─ __init__.py
│  │  ├─ conversation.py         # Conversation management
│  │  └─ routes.py              # Chat endpoints
│  ├─ rating/                    # Rating engines
│  │  ├─ __init__.py
│  │  ├─ vac_canada.py          # VAC Canada rating logic
│  │  ├─ aus_garp.py            # Australia GARP logic
│  │  ├─ uk_afcs.py             # UK AFCS/WPS logic
│  │  └─ us_38cfr.py            # US 38 CFR logic
│  ├─ documents/                 # Document processing
│  │  ├─ __init__.py
│  │  ├─ processor.py           # File upload & processing
│  │  └─ search.py              # Document search
│  ├─ core/                      # Core utilities
│  │  ├─ __init__.py
│  │  ├─ config.py              # Configuration
│  │  ├─ auth.py                # Authentication
│  │  └─ prompts.py             # System prompts
│  ├─ data/                      # Static data & rules
│  │  ├─ rules/
│  │  │  ├─ master2019ToD.json
│  │  │  ├─ US_Title38_rules.json
│  │  │  └─ mapping.yaml
│  │  ├─ documents/              # Pre-processed documents
│  │  │  ├─ canada/
│  │  │  │  └─ VAC_ToD_2019_indexed.json
│  │  │  ├─ australia/
│  │  │  ├─ uk/
│  │  │  └─ usa/
│  │  └─ embeddings/             # Local vector store
│  │     └─ document_vectors.pkl
│  └─ schemas/                   # Pydantic models
│     ├─ __init__.py
│     ├─ intake.py              # Input schemas
│     └─ results.py             # Output schemas
│
├─ ui/                           # Next.js UI (unchanged)
│  ├─ app/
│  ├─ lib/
│  └─ public/
│
├─ prompts/                      # System prompts
│  ├─ system_prompt.md
│  ├─ flows/
│  │  └─ assessment.md
│  └─ styles/
│     └─ adjudicator_tone.md
│
├─ deploy/                       # Deployment configs
│  ├─ docker-compose.yml         # Local development
│  ├─ Dockerfile                # Single container
│  ├─ azure-container-instance.bicep  # Personal Azure
│  └─ azure-container-apps.bicep      # Enterprise Azure
│
├─ tests/                        # Testing
│  ├─ unit/
│  └─ integration/
│
├─ .env.example                  # Environment template
├─ requirements.txt              # Python dependencies
└─ README.md                     # Setup instructions
```

## Key Simplifications

### 1. Single FastAPI App
- Combines all services into one application
- Built-in file processing (no separate functions)
- Embedded vector search (no AI Search initially)
- Direct conversation management

### 2. Pre-processed Documents
- Documents pre-indexed and chunked
- Stored as JSON for fast lookup
- Embedded vectors for semantic search
- No complex ingestion pipeline needed

### 3. Container-First Development
- Single Dockerfile for all components
- docker-compose for local development
- Same container for all deployment targets

### 4. Simplified Data Flow
```
File Upload → Process Immediately → Store & Index → Available for Search
```

Instead of:
```
File Upload → Queue → Functions → Process → Index → Available
```

## Development Workflow

### Local Development
```bash
# Start everything locally
docker-compose up --build

# Access:
# UI: http://localhost:3000
# API: http://localhost:8000/docs
```

### Personal Azure Deploy
```bash
# Build and push
az acr build --registry your-acr --image gwsgpt .

# Deploy to Container Instance
az deployment group create \
  --resource-group rg-gwsgpt-test \
  --template-file deploy/azure-container-instance.bicep
```

### Enterprise Azure Deploy
```bash
# Same container, different infrastructure
az deployment group create \
  --resource-group rg-gwsgpt-prod \
  --template-file deploy/azure-container-apps.bicep
```

## Migration Benefits

✅ **Same codebase** across all environments
✅ **Container portability** - build once, deploy anywhere  
✅ **Incremental scaling** - add services as needed
✅ **Cost optimization** - start small, scale up
✅ **Risk mitigation** - test before enterprise investment