import React, { useState } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import ReactMarkdown from 'react-markdown';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);

  // Fetch stats on mount
  React.useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const onDrop = async (acceptedFiles) => {
    setLoading(true);
    for (const file of acceptedFiles) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await axios.post(`${API_URL}/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        setUploadedFiles(prev => [...prev, {
          name: file.name,
          chunks: response.data.chunks_created,
          id: response.data.document_id
        }]);

        await fetchStats();
      } catch (error) {
        alert(`Error uploading ${file.name}: ${error.response?.data?.detail || error.message}`);
      }
    }
    setLoading(false);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt']
    }
  });

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setAnswer(null);

    try {
      const response = await axios.post(`${API_URL}/query`, {
        question: question,
        top_k: 5
      });

      setAnswer(response.data);
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    }

    setLoading(false);
  };

  const clearDatabase = async () => {
    if (!window.confirm('Clear all documents?')) return;
    
    try {
      await axios.delete(`${API_URL}/clear`);
      setUploadedFiles([]);
      setAnswer(null);
      await fetchStats();
      alert('Database cleared successfully');
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="App">
      <header className="header">
        <h1>🔍 RAG System</h1>
        <p>Retrieval-Augmented Generation with Citations</p>
      </header>

      <div className="container">
        {/* Upload Section */}
        <div className="section">
          <h2>📄 Upload Documents</h2>
          <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            {isDragActive ? (
              <p>Drop files here...</p>
            ) : (
              <p>Drag & drop PDF or TXT files, or click to select</p>
            )}
          </div>

          {uploadedFiles.length > 0 && (
            <div className="uploaded-files">
              <h3>Uploaded Files ({uploadedFiles.length})</h3>
              {uploadedFiles.map((file, idx) => (
                <div key={idx} className="file-item">
                  <span>📄 {file.name}</span>
                  <span className="chunks-badge">{file.chunks} chunks</span>
                </div>
              ))}
            </div>
          )}

          {stats && (
            <div className="stats">
              <strong>Total Chunks in DB:</strong> {stats.total_chunks}
              <button onClick={clearDatabase} className="clear-btn">Clear All</button>
            </div>
          )}
        </div>

        {/* Query Section */}
        <div className="section">
          <h2>💬 Ask Questions</h2>
          <form onSubmit={handleQuery}>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about your documents..."
              rows="3"
              className="question-input"
            />
            <button type="submit" disabled={loading || !question.trim()} className="query-btn">
              {loading ? 'Processing...' : 'Ask Question'}
            </button>
          </form>

          {answer && (
            <div className="answer-section">
              <div className="answer-header">
                <h3>Answer</h3>
                <span className="confidence">
                  Confidence: {(answer.confidence * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="answer-content">
                <ReactMarkdown>{answer.answer}</ReactMarkdown>
              </div>

              <div className="sources">
                <h4>📚 Sources ({answer.sources.length})</h4>
                {answer.sources.map((source, idx) => (
                  <div key={idx} className="source-item">
                    <div className="source-header">
                      <strong>{source.source}</strong>
                      <span className="relevance">
                        Relevance: {(source.relevance_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <p className="source-preview">{source.text_preview}</p>
                    <small>Chunk {source.chunk_index + 1}</small>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <footer className="footer">
        <p>Built for SPAZORLABS AI/ML Internship | Tathagata Bhattacherjee</p>
      </footer>
    </div>
  );
}

export default App;