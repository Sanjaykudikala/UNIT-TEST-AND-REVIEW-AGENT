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
    
    # Chroma accepts batches, but we'll do it in one go assuming medium repo size
    # If the repo is large, we should batch this. For commons-text, ~1000 chunks is fine.
    
    # Check if we already have data
    existing = collection.get(ids=ids[:1])
    if existing and existing['ids']:
        # To simplify, we'll try to update or add.
        pass
        
    # Chroma upsert allows insert or update
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
    # Return matched documents as a single context string
    if results and results['documents']:
        return "\n\n".join(results['documents'][0])
    return ""
