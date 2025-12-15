# 🔍 RAG System - Retrieval-Augmented Generation

**SPAZORLABS AI/ML Internship - Task 1**

A production-ready RAG (Retrieval-Augmented Generation) system with document ingestion, vector search, and LLM-based Q&A with citations.

## 🎯 Features

### Core Capabilities
- **Document Ingestion**: Upload PDF and TXT files
- **Smart Chunking**: Recursive text splitting with overlap for context preservation
- **Vector Embeddings**: OpenAI text-embedding-3-small for semantic search
- **Vector Database**: ChromaDB with cosine similarity search
- **LLM Generation**: GPT-4o-mini for accurate, context-aware answers
- **Citation System**: Automatic source attribution with relevance scores
- **Confidence Scoring**: Answer confidence based on retrieval quality

### Technical Highlights
- ✅ **Scalable Architecture**: FastAPI backend with async operations
- ✅ **Low Latency**: Optimized chunking and retrieval pipeline
- ✅ **High Accuracy**: Context-aware generation with source verification
- ✅ **Production Ready**: Docker containerization, CORS support
- ✅ **Modern UI**: React frontend with drag-and-drop upload
- ✅ **Real-time Stats**: Live database statistics and monitoring

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   FastAPI    │─────▶│  ChromaDB   │
│   (React)   │      │   Backend    │      │  (Vectors)  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  OpenAI API  │
                     │  (Embeddings │
                     │   & LLM)     │
                     └──────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API Key

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Set environment variable
export OPENAI_API_KEY="your-api-key-here"

# Run server
uvicorn main:app --reload
```

Backend runs on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install

# Set API URL (optional, defaults to localhost:8000)
export REACT_APP_API_URL="http://localhost:8000"

# Run development server
npm start
```

Frontend runs on `http://localhost:3000`

## 📡 API Endpoints

### `POST /upload`
Upload and process documents
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "status": "success",
  "filename": "document.pdf",
  "chunks_created": 15,
  "document_id": "abc123..."
}
```

### `POST /query`
Query documents with RAG
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic?",
    "top_k": 5
  }'
```

**Response:**
```json
{
  "answer": "Based on the documents...",
  "sources": [
    {
      "source": "document.pdf",
      "chunk_index": 3,
      "relevance_score": 0.92,
      "text_preview": "..."
    }
  ],
  "confidence": 0.89
}
```

### `GET /stats`
Get database statistics
```bash
curl "http://localhost:8000/stats"
```

### `DELETE /clear`
Clear all documents
```bash
curl -X DELETE "http://localhost:8000/clear"
```

## 🐳 Docker Deployment

### Build and Run Backend
```bash
cd backend
docker build -t rag-backend .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  rag-backend
```

### Build Frontend
```bash
cd frontend
npm run build
# Deploy build/ folder to Vercel/Netlify
```

## 🔧 Configuration

### Environment Variables

**Backend:**
- `OPENAI_API_KEY`: Your OpenAI API key (required)

**Frontend:**
- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8000)

### Chunking Parameters
Adjust in `backend/main.py`:
```python
chunk_size = 1000        # Characters per chunk
chunk_overlap = 200      # Overlap between chunks
```

### Retrieval Parameters
Adjust in query request:
```python
top_k = 5               # Number of chunks to retrieve
```

## 📊 Performance Metrics

- **Embedding Speed**: ~100ms per chunk (OpenAI API)
- **Search Latency**: <50ms (ChromaDB cosine search)
- **Answer Generation**: ~2-3s (GPT-4o-mini)
- **Total Query Time**: ~3-4s end-to-end

## 🎨 Frontend Features

- **Drag & Drop Upload**: Easy document upload interface
- **Real-time Processing**: Live upload progress and feedback
- **Interactive Q&A**: Clean question-answer interface
- **Source Citations**: Expandable source references with relevance scores
- **Confidence Indicators**: Visual confidence scoring
- **Responsive Design**: Mobile-friendly UI

## 🔐 Security Considerations

- API key stored in environment variables
- CORS configured for production domains
- Input validation on file uploads
- Rate limiting recommended for production
- Secure HTTPS deployment recommended

## 📈 Scalability

### Current Limitations
- In-memory ChromaDB (suitable for demos)
- Single-instance deployment

### Production Recommendations
- Use ChromaDB with persistent storage
- Deploy ChromaDB as separate service
- Implement caching layer (Redis)
- Add load balancing for API
- Use managed vector DB (Pinecone/Weaviate) for scale

## 🧪 Testing

### Test Document Upload
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@test.pdf"
```

### Test Query
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question?", "top_k": 3}'
```

## 📝 Technical Stack

**Backend:**
- FastAPI - Modern Python web framework
- ChromaDB - Vector database
- OpenAI API - Embeddings & LLM
- LangChain - Text splitting utilities
- PyPDF2 - PDF processing

**Frontend:**
- React 18 - UI framework
- Axios - HTTP client
- React Dropzone - File upload
- React Markdown - Answer rendering

## 🎓 Learning Outcomes

This project demonstrates:
- End-to-end RAG pipeline implementation
- Vector database integration and search
- LLM prompt engineering for Q&A
- Document processing and chunking strategies
- Full-stack application development
- Production deployment practices

## 👨‍💻 Author

**Tathagata Bhattacherjee**
- Email: tathab3110@gmail.com
- GitHub: [@Tathagt](https://github.com/Tathagt)

## 📄 License

MIT License - Built for SPAZORLABS AI/ML Internship

## 🙏 Acknowledgments

- SPAZORLABS for the internship opportunity
- OpenAI for embeddings and LLM APIs
- ChromaDB team for the vector database

---

**Submission Date**: December 2025  
**Task**: Retrieval-Augmented Generation (RAG) System  
**Status**: ✅ Complete with Deployment