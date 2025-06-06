import os
import requests
from chromadb import PersistentClient
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse


GROQ_API_KEY = "key"

# Setup Chroma client
ef = embedding_functions.DefaultEmbeddingFunction()
client = PersistentClient(path="../chroma_db")
collection = client.get_collection(name="rag_db", embedding_function=ef)

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

@app.post("/api")
async def ask_question(req: QuestionRequest):
    question = req.question

    # Query Chroma
    results = collection.query(query_texts=[question], n_results=15)
    contexts = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    filtered = [(c, m) for c, m, d in zip(contexts, metas, distances)]
    if not filtered:
        return JSONResponse({"answer": None, "related_links": [], "images": [], "message": "No relevant data found."}, status_code=404)

    # Compose context
    context_text = "\n\n".join([ctx for ctx, _ in filtered])

    # Prompt for Groq
    prompt = f"""You are a helpful virtual TA for the 'Tools in Data Science' course at IIT Madras.
Answer the question based only on the context below.

Context:
{context_text}

Question: {question}
Answer:"""

    # Call Groq API
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        return JSONResponse({"answer": None, "related_links": [], "images": [], "message": "Error from Groq: " + response.text}, status_code=500)

    answer = response.json()['choices'][0]['message']['content']

    # Related links and images
    related_links = []
    images = []

    for _, meta in filtered:
        if meta.get("url"):
            url = meta["url"]
            print(" ".join(url.split("/")[2].split("-")))
            related_links.append({
                "url": f'https://discourse.onlinedegree.iitm.ac.in/{url}' if 'https' not in url else url,
                "text": " ".join(url.split("/")[2].split("-"))
            })
        if meta.get("images"):
            img_list = meta["images"].split()
            images.extend(img_list)

    return {
        "answer": answer,
        "links": related_links,
    }
