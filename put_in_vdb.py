from chromadb import PersistentClient
from chromadb.utils import embedding_functions
import json

ef = embedding_functions.DefaultEmbeddingFunction()

client = PersistentClient(path="./chroma_db")  # Use PersistentClient
collection = client.get_or_create_collection(name="rag_db", embedding_function=ef)

# Load data
with open('final_data.json') as f:
    data = json.load(f)

documents = []
metadatas = []
ids = []

for idx, item in enumerate(data):
    documents.append(item['text'])
    metadatas.append({
        'url': item.get('url', ''),
        'images': " ".join(item.get('images', []))
    })
    ids.append(str(idx))

collection.add(documents=documents, metadatas=metadatas, ids=ids)

print(f"Inserted {len(documents)} documents.")
