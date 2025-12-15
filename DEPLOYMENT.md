# 🚀 Deployment Guide

## Railway Deployment (Backend)

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub

### Step 2: Deploy Backend
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `spazorlabs-rag-system`
4. Railway will auto-detect the Dockerfile

### Step 3: Add Environment Variables
In Railway dashboard:
```
OPENAI_API_KEY=your-openai-api-key-here
```

### Step 4: Get Backend URL
- Railway will provide a URL like: `https://your-app.railway.app`
- Copy this URL for frontend configuration

## Vercel Deployment (Frontend)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Deploy Frontend
```bash
cd frontend
vercel
```

### Step 3: Set Environment Variable
When prompted or in Vercel dashboard:
```
REACT_APP_API_URL=https://your-backend.railway.app
```

### Step 4: Production Deployment
```bash
vercel --prod
```

## Alternative: Render Deployment

### Backend on Render
1. Go to [render.com](https://render.com)
2. New Web Service → Connect GitHub repo
3. Settings:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Add `OPENAI_API_KEY`

### Frontend on Render
1. New Static Site → Connect GitHub repo
2. Settings:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/build`
   - **Environment**: Add `REACT_APP_API_URL`

## Docker Compose (Local Production)

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./chroma_db:/app/chroma_db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
```

Run with:
```bash
docker-compose up -d
```

## Environment Variables Summary

### Backend
- `OPENAI_API_KEY` (required): Your OpenAI API key

### Frontend
- `REACT_APP_API_URL` (required): Backend API URL

## Post-Deployment Checklist

- [ ] Backend health check: `GET /`
- [ ] Upload test document
- [ ] Query test
- [ ] Check stats endpoint
- [ ] Verify CORS settings
- [ ] Test from frontend UI
- [ ] Monitor logs for errors

## Troubleshooting

### CORS Errors
Update `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### OpenAI API Errors
- Verify API key is set correctly
- Check API key has credits
- Ensure key has access to required models

### ChromaDB Persistence
For production, mount volume:
```bash
docker run -v ./chroma_db:/app/chroma_db ...
```

## Monitoring

### Railway
- View logs in Railway dashboard
- Set up health checks
- Monitor resource usage

### Vercel
- Check deployment logs
- Monitor function execution
- Review analytics

## Scaling Considerations

### For High Traffic
1. Use managed vector DB (Pinecone/Weaviate)
2. Add Redis caching layer
3. Implement rate limiting
4. Use CDN for frontend
5. Add load balancer for backend

### Cost Optimization
- Cache embeddings to reduce OpenAI calls
- Implement request batching
- Use smaller embedding models for dev
- Monitor and set API usage limits