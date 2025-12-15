from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings
import openai
import os
from typing import List, Optional
import PyPDF2
import io
from langchain.text_splitter import RecursiveCharacterTextSplitter
import hashlib

app = FastAPI(title="RAG System API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Chroma client
chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_db"
))

# Get or create collection
collection = chroma_client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: float

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Split text into chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_embedding(text: str) -> List[float]:
    """Get OpenAI embedding for text"""
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

@app.get("/")
async def root():
    return {
        "message": "RAG System API",
        "endpoints": {
            "upload": "/upload",
            "query": "/query",
            "stats": "/stats"
        }
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process document"""
    try:
        # Read file content
        content = await file.read()
        
        # Extract text based on file type
        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(content)
        elif file.filename.endswith('.txt'):
            text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF or TXT")
        
        # Chunk the text
        chunks = chunk_text(text)
        
        # Generate embeddings and store in Chroma
        doc_id = hashlib.md5(file.filename.encode()).hexdigest()
        
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            chunk_id = f"{doc_id}_chunk_{i}"
            
            collection.add(
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "source": file.filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }],
                ids=[chunk_id]
            )
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_created": len(chunks),
            "document_id": doc_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents using RAG"""
    try:
        # Get embedding for question
        question_embedding = get_embedding(request.question)
        
        # Search in Chroma
        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=request.top_k
        )
        
        if not results['documents'][0]:
            raise HTTPException(status_code=404, detail="No documents found")
        
        # Prepare context from retrieved chunks
        context_chunks = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]
        
        context = "\n\n".join([
            f"[Source: {meta['source']}, Chunk {meta['chunk_index']+1}/{meta['total_chunks']}]\n{chunk}"
            for chunk, meta in zip(context_chunks, metadatas)
        ])
        
        # Generate answer using GPT
        prompt = f"""Answer the question based on the context below. Include citations to sources.

Context:
{context}

Question: {request.question}

Answer with citations (mention source documents):"""
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context. Always cite your sources."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        answer = response.choices[0].message.content
        
        # Prepare sources
        sources = [
            {
                "source": meta['source'],
                "chunk_index": meta['chunk_index'],
                "relevance_score": 1 - dist,
                "text_preview": chunk[:200] + "..."
            }
            for chunk, meta, dist in zip(context_chunks, metadatas, distances)
        ]
        
        # Calculate confidence (average relevance)
        confidence = sum(1 - d for d in distances) / len(distances)
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            confidence=round(confidence, 3)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        count = collection.count()
        return {
            "total_chunks": count,
            "collection_name": collection.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear")
async def clear_database():
    """Clear all documents"""
    try:
        chroma_client.delete_collection("documents")
        global collection
        collection = chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        return {"status": "success", "message": "Database cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)