"""
Test script for RAG System API
Run: python test_api.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test API health"""
    print("🔍 Testing API health...")
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_upload(file_path):
    """Test document upload"""
    print(f"📤 Uploading document: {file_path}")
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print(f"✅ Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.json()

def test_query(question, top_k=5):
    """Test query"""
    print(f"❓ Querying: {question}")
    payload = {
        "question": question,
        "top_k": top_k
    }
    response = requests.post(f"{BASE_URL}/query", json=payload)
    
    print(f"✅ Status: {response.status_code}")
    result = response.json()
    
    print(f"\n📝 Answer:\n{result['answer']}\n")
    print(f"🎯 Confidence: {result['confidence']:.2%}\n")
    print(f"📚 Sources ({len(result['sources'])}):")
    for i, source in enumerate(result['sources'], 1):
        print(f"  {i}. {source['source']} (Chunk {source['chunk_index']}) - Relevance: {source['relevance_score']:.2%}")
    print()

def test_stats():
    """Test stats endpoint"""
    print("📊 Getting database stats...")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"✅ Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def create_sample_document():
    """Create a sample text document for testing"""
    content = """
    Artificial Intelligence and Machine Learning
    
    Artificial Intelligence (AI) is the simulation of human intelligence by machines.
    Machine Learning (ML) is a subset of AI that enables systems to learn from data.
    
    Key Concepts:
    1. Supervised Learning: Training with labeled data
    2. Unsupervised Learning: Finding patterns in unlabeled data
    3. Reinforcement Learning: Learning through trial and error
    
    Applications:
    - Natural Language Processing (NLP)
    - Computer Vision
    - Recommendation Systems
    - Autonomous Vehicles
    
    RAG (Retrieval-Augmented Generation) combines information retrieval with
    language generation to provide accurate, context-aware responses with citations.
    """
    
    with open('sample_doc.txt', 'w') as f:
        f.write(content)
    
    return 'sample_doc.txt'

def main():
    """Run all tests"""
    print("=" * 60)
    print("RAG SYSTEM API TESTS")
    print("=" * 60 + "\n")
    
    try:
        # Test 1: Health check
        test_health()
        time.sleep(1)
        
        # Test 2: Create and upload sample document
        sample_file = create_sample_document()
        test_upload(sample_file)
        time.sleep(2)
        
        # Test 3: Check stats
        test_stats()
        time.sleep(1)
        
        # Test 4: Query the document
        test_query("What is RAG?")
        time.sleep(2)
        
        test_query("What are the applications of AI?")
        time.sleep(2)
        
        test_query("Explain supervised learning")
        
        print("=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Make sure the server is running on", BASE_URL)
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()