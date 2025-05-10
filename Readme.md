# Website Semantic Search App

This is a full-stack semantic search application that allows users to input a website URL and a query. It fetches the HTML content from the website, extracts meaningful text sections (one heading + one paragraph), embeds them using a transformer model, stores them in a vector database (Weaviate), and returns the top 10 semantically relevant results.

---

## Features

- Fetch HTML content from any public webpage
- Extract first `<h1>`-`<h6>` and `<p>` as meaningful content
- Chunk content and create embeddings with `SentenceTransformer`
- Store and query chunks semantically via Weaviate
- Display results with match score and viewable raw HTML

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker + Docker Compose

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Irshad-Ahmaed/SmarterCodes.git
cd SmarterCodes
```

### 2. Backend Setup
### 2.1. Virtual Environment setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate 
```

### 2.2. Backend Run
```bash
pip install -r requirements.txt
docker-compose up
uvicorn main:app --reload --port 8000
```

### 3. Setup and Run Frontend
```bash
cd frontend
npm install
npm run dev
```

- App will be available at: http://localhost:3000

## Vector Database Configuration (Weaviate)
- Uses the weaviate Docker image.
- gRPC is disabled for simplicity (grpc: false in Python client).
- No authentication or persistence by default (can be added).
- Schema and collections are created dynamically at runtime.