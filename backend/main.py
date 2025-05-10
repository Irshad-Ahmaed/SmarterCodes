from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
from weaviate import connect_to_local
from weaviate.classes.init import AdditionalConfig
from weaviate.classes.config import Property, DataType, Configure

# --- FastAPI setup ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# --- Model and Weaviate client ---
model = SentenceTransformer("all-MiniLM-L6-v2")
client = connect_to_local(
    additional_config=AdditionalConfig(grpc=False), skip_init_checks=True
)


# --- Input schema ---
class Input(BaseModel):
    url: str
    query: str


# --- Crawl internal pages ---
def crawl_internal_pages(base_url: str, max_pages: int = 10):
    visited = set()
    to_visit = [base_url]
    collected = []

    while to_visit and len(visited) < max_pages:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
        visited.add(current_url)

        try:
            response = requests.get(current_url, timeout=10)
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
        except:
            continue

        print(f"🧭 Crawled: {current_url}")

        # Collect content blocks from this page
        blocks = extract_content_blocks(soup, current_url)
        collected.extend(blocks)

        # Discover new internal links
        base_netloc = urlparse(base_url).netloc
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == base_netloc and full_url not in visited:
                to_visit.append(full_url)

    return collected


# --- Extract headings + paragraphs ---
def extract_content_blocks(soup, page_url):
    for tag in soup(["script", "style"]):
        tag.decompose()

    blocks = []
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

    for heading in headings:
        paragraph = heading.find_next("p")
        if not paragraph:
            continue

        html_block = f'<div class="et_pb_text_inner">\n  {str(heading)}\n  {str(paragraph)}\n</div>'
        text_block = f"{heading.get_text(strip=True)} {paragraph.get_text(strip=True)}"

        blocks.append({"text": text_block, "html": html_block, "url": page_url})

    return blocks


# --- Main endpoint ---
@app.post("/search")
def search(input: Input):
    print(f"🚀 Starting crawl for: {input.url}")
    blocks = crawl_internal_pages(input.url, max_pages=10)
    if not blocks:
        return {"results": [], "message": "No content found."}

    # Ensure schema exists
    if not client.collections.exists("Chunk"):
        client.collections.create(
            name="Chunk",
            properties=[
                Property(name="text", data_type=DataType.TEXT),
                Property(name="html", data_type=DataType.TEXT),
                Property(name="url", data_type=DataType.TEXT),
            ],
            vector_index_config=Configure.VectorIndex.hnsw(),
        )

    collection = client.collections.get("Chunk")

    # Clear old data
    for obj in collection.iterator():
        collection.data.delete_by_id(obj.uuid)

    # Insert blocks
    for block in blocks:
        embedding = model.encode(block["text"]).tolist()
        collection.data.insert(
            properties={
                "text": block["text"],
                "html": block["html"],
                "url": block["url"],
            },
            vector=embedding,
        )

    # Semantic search (now with distance)
    query_vector = model.encode(input.query).tolist()
    results = collection.query.near_vector(
        near_vector=query_vector, limit=10, return_metadata=["distance", "certainty"]
    )

    # print("✅ Type:", type(results.objects[0]))
    # print("✅ Distance:", results.objects[0].metadata)

    return {
        "results": [
            {
                "result": obj.properties["text"],
                "path": urlparse(obj.properties.get("url", input.url)).path or "/",
                "score": (
                    round(obj.metadata.certainty * 100, 2)
                    if obj.metadata.certainty is not None
                    else round((1 - obj.metadata.distance) * 100, 2)
                ),
                "html": obj.properties["html"],
            }
            for obj in results.objects
        ]
    }
