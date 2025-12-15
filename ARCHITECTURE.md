# 🏗️ System Architecture

## Overview

The RAG system follows a modern microservices architecture with clear separation between frontend, backend, and data layers.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              React Frontend (Port 3000)                 │ │
│  │  • Drag & Drop Upload  • Query Interface               │ │
│  │  • Results Display     • Source Citations              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           FastAPI Backend (Port 8000)                   │ │
│  │                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │   Upload     │  │    Query     │  │    Stats     │ │ │
│  │  │   Handler    │  │   Handler    │  │   Handler    │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │
│  │                                                          │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │         Document Processing Pipeline             │  │ │
│  │  │  1. Text Extraction (PyPDF2)                     │  │ │
│  │  │  2. Chunking (LangChain)                         │  │ │
│  │  │  3. Embedding Generation (OpenAI)                │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│      DATA LAYER          │  │    EXTERNAL SERVICES     │
│                          │  │                          │
│  ┌────────────────────┐  │  │  ┌────────────────────┐  │
│  │    ChromaDB        │  │  │  │   OpenAI API       │  │
│  │  Vector Database   │  │  │  │                    │  │
│  │                    │  │  │  │  • Embeddings      │  │
│  │  • Embeddings      │  │  │  │  • GPT-4o-mini     │  │
│  │  • Metadata        │  │  │  │                    │  │
│  │  • Cosine Search   │  │  │  └────────────────────┘  │
│  └────────────────────┘  │  │                          │
└──────────────────────────┘  └──────────────────────────┘
```

## Component Details

### 1. Frontend (React)

**Responsibilities:**
- User interface for document upload
- Query input and submission
- Results visualization with citations
- Real-time feedback and loading states

**Key Technologies:**
- React 18 with Hooks
- Axios for HTTP requests
- React Dropzone for file uploads
- React Markdown for answer rendering

**Files:**
- `frontend/src/App.js` - Main application component
- `frontend/src/App.css` - Styling
- `frontend/public/index.html` - HTML template

### 2. Backend (FastAPI)

**Responsibilities:**
- RESTful API endpoints
- Document processing pipeline
- Vector database management
- LLM orchestration

**Key Technologies:**
- FastAPI for async API
- PyPDF2 for PDF parsing
- LangChain for text splitting
- ChromaDB client for vector operations

**Files:**
- `backend/main.py` - Main application with all endpoints
- `backend/requirements.txt` - Python dependencies
- `backend/Dockerfile` - Container configuration

### 3. Vector Database (ChromaDB)

**Responsibilities:**
- Store document embeddings
- Perform similarity search
- Manage metadata

**Configuration:**
- Distance metric: Cosine similarity
- Storage: DuckDB + Parquet (persistent)
- Collection: "documents"

### 4. External Services

**OpenAI API:**
- **Embeddings**: text-embedding-3-small (1536 dimensions)
- **LLM**: gpt-4o-mini for answer generation
- **Usage**: ~100ms per embedding, ~2-3s per completion

## Data Flow

### Upload Flow

```
1. User uploads PDF/TXT
   ↓
2. Frontend sends file to /upload
   ↓
3. Backend extracts text (PyPDF2)
   ↓
4. Text split into chunks (LangChain)
   ↓
5. Generate embeddings (OpenAI)
   ↓
6. Store in ChromaDB with metadata
   ↓
7. Return success + chunk count
```

### Query Flow

```
1. User submits question
   ↓
2. Frontend sends to /query
   ↓
3. Generate question embedding (OpenAI)
   ↓
4. Search ChromaDB (cosine similarity)
   ↓
5. Retrieve top-k chunks + metadata
   ↓
6. Build context from chunks
   ↓
7. Generate answer with GPT (OpenAI)
   ↓
8. Return answer + sources + confidence
   ↓
9. Frontend displays with citations
```

## Scalability Considerations

### Current Architecture (Demo/MVP)
- Single-instance deployment
- In-memory ChromaDB
- Synchronous processing
- **Suitable for**: Demos, small teams, low traffic

### Production Architecture

```
┌──────────────┐
│ Load Balancer│
└──────┬───────┘
       │
   ┌───┴────┬────────┬────────┐
   ▼        ▼        ▼        ▼
┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐
│API-1│  │API-2│  │API-3│  │API-N│
└──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘
   │        │        │        │
   └────────┴────────┴────────┘
            │
      ┌─────┴─────┐
      │   Redis   │ (Cache)
      └─────┬─────┘
            │
   ┌────────┴────────┐
   │  Managed Vector │
   │  DB (Pinecone)  │
   └─────────────────┘
```

**Improvements:**
- Horizontal scaling with load balancer
- Redis caching for embeddings
- Managed vector DB (Pinecone/Weaviate)
- Async task queue (Celery)
- CDN for frontend

## Performance Optimization

### Latency Breakdown
- **Text Extraction**: 50-200ms (PDF size dependent)
- **Chunking**: 10-50ms
- **Embedding Generation**: 100ms per chunk
- **Vector Search**: <50ms
- **LLM Generation**: 2-3s
- **Total**: ~3-4s per query

### Optimization Strategies

1. **Caching**
   - Cache embeddings for repeated chunks
   - Cache common queries
   - Use Redis for distributed cache

2. **Batching**
   - Batch embedding requests
   - Process multiple chunks in parallel

3. **Indexing**
   - Use HNSW index in ChromaDB
   - Optimize chunk size for retrieval

4. **Model Selection**
   - Use smaller embedding models for dev
   - Consider local models for privacy

## Security Architecture

### Current Implementation
- Environment-based API key management
- CORS configuration
- Input validation

### Production Recommendations
- API rate limiting
- Authentication/Authorization (JWT)
- Request signing
- Encryption at rest
- HTTPS only
- API key rotation
- Audit logging

## Monitoring & Observability

### Metrics to Track
- Request latency (p50, p95, p99)
- Error rates
- OpenAI API usage
- Vector DB query performance
- Document processing time
- Storage usage

### Recommended Tools
- **Logging**: Structured logging with JSON
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry
- **Alerts**: PagerDuty/Slack integration

## Deployment Architecture

### Development
```
Local Machine
├── Backend (localhost:8000)
├── Frontend (localhost:3000)
└── ChromaDB (local file)
```

### Production
```
Cloud Infrastructure
├── Frontend (Vercel/Netlify)
├── Backend (Railway/Render)
│   ├── Auto-scaling
│   └── Health checks
└── Vector DB (Managed service)
```

## Future Enhancements

1. **Multi-modal Support**
   - Image document processing
   - Audio transcription

2. **Advanced Features**
   - Conversation memory
   - Multi-document comparison
   - Automatic summarization

3. **Enterprise Features**
   - Multi-tenancy
   - Role-based access
   - Custom model fine-tuning
   - Analytics dashboard

## Technology Choices Rationale

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Backend Framework | FastAPI | Async support, auto docs, type safety |
| Vector DB | ChromaDB | Easy setup, good for demos, Python-native |
| Embeddings | OpenAI | High quality, fast, well-supported |
| LLM | GPT-4o-mini | Cost-effective, fast, accurate |
| Frontend | React | Component-based, large ecosystem |
| Deployment | Railway/Vercel | Easy setup, free tier, good DX |