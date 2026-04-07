import chromadb
from chromadb.utils import embedding_functions
from core.config import settings

def get_chroma_client():
    return chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)

def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=settings.EMBEDDING_MODEL
    )

def get_collection():
    client = get_chroma_client()
    ef = get_embedding_function()
    collection = client.get_or_create_collection(
        name="java_codebase", 
        embedding_function=ef
    )
    return collection

def store_chunks(chunks):
    collection = get_collection()

    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    existing = collection.get(ids=ids[:1])
    if existing and existing['ids']:

        pass

    batch_size = 500
    for i in range(0, len(ids), batch_size):
        collection.upsert(
            ids=ids[i:i+batch_size],
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size]
        )
    return len(ids)

def query_context(query: str, n_results: int = 3):
    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    if results and results['documents']:
        context_list = []
        for i in range(len(results['documents'][0])):
            context_list.append({
                "text": results['documents'][0][i],
                "file": results['metadatas'][0][i].get("file", "unknown"),
                "score": results['distances'][0][i] if 'distances' in results else 1.0
            })
        return context_list
    return []
