from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup
import requests

from weaviate import connect_to_local
from weaviate.classes.init import AdditionalConfig
from weaviate.classes.config import Property, DataType, Configure

# Initialize FastAPI app
app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load sentence transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to Weaviate (REST-only)
client = connect_to_local(
    additional_config=AdditionalConfig(grpc=False),
    skip_init_checks=True
)

# Input schema
class Input(BaseModel):
    url: str
    query: str

# Clean HTML text
def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)

# Chunk into ~500-token blocks
def chunk_text(text: str, max_tokens: int = 500):
    words = text.split()
    return [' '.join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]

@app.post("/search")
def search(input: Input):
    try:
        html_raw = requests.get(input.url, timeout=10).text
    except Exception as e:
        return {"error": f"Failed to fetch URL: {str(e)}"}

    soup = BeautifulSoup(html_raw, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Create a list of clean HTML blocks with 1 heading + 1 paragraph
    blocks = []
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    for heading in headings:
        # Try to find the first paragraph after this heading
        paragraph = heading.find_next('p')
        if not paragraph:
            continue

        # Build combined HTML block
        combined_html = f'<div class="et_pb_text_inner">\n  {str(heading)}\n  {str(paragraph)}\n</div>'
        combined_text = f"{heading.get_text(strip=True)} {paragraph.get_text(strip=True)}"

        blocks.append({
            "text": combined_text,
            "html": combined_html
        })

    # Ensure Weaviate schema exists
    if not client.collections.exists("Chunk"):
        client.collections.create(
            name="Chunk",
            properties=[
                Property(name="text", data_type=DataType.TEXT),
                Property(name="html", data_type=DataType.TEXT)
            ],
            vector_index_config=Configure.VectorIndex.hnsw()
        )

    collection = client.collections.get("Chunk")

    # Optional: Clear old data
    for obj in collection.iterator():
        collection.data.delete_by_id(obj.uuid)

    # Insert blocks into Weaviate
    for block in blocks:
        embedding = model.encode(block["text"]).tolist()
        collection.data.insert(
            properties={
                "text": block["text"],
                "html": block["html"]
            },
            vector=embedding
        )

    # Semantic search
    query_vector = model.encode(input.query).tolist()
    results = collection.query.near_vector(
        near_vector=query_vector,
        limit=10
    )

    # Final structured response
    return {
        "results": [
            {
                "result": obj.properties["text"],
                "path": "/unknown",
                "score": obj.distance if hasattr(obj, 'distance') else 0.85,
                "html": obj.properties["html"]
            }
            for obj in results.objects
        ]
    }