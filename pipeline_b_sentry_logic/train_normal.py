import chromadb
import chromadb.errors
from sentence_transformers import SentenceTransformer
import os

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
DATA_PATH = "../data/normal_train.txt"
DB_PATH = "./chroma_db_storage"
COLLECTION_NAME = "normal_patterns"
MODEL_NAME = "all-MiniLM-L6-v2"  # Fast, lightweight embedding model

def main():
    print(f"🚀 Initializing Sentry Training Core...")
    
    # 1. Initialize the Embedding Model
    # We use a small model optimized for sentence similarity
    model = SentenceTransformer(MODEL_NAME)
    
    # 2. Initialize Vector Database (Persistent)
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # Reset collection if it exists (for fresh training)
    try:
        client.delete_collection(COLLECTION_NAME)
    except chromadb.errors.NotFoundError: 
        pass  # Collection didn't exist, which is fine
        
    collection = client.create_collection(name=COLLECTION_NAME)

    # 3. Load Training Data
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: Data file not found at {DATA_PATH}")
        return

    with open(DATA_PATH, "r") as f:
        logs = [line.strip() for line in f.readlines() if line.strip()]

    print(f"📥 Loaded {len(logs)} normal log lines.")

    # 4. Vectorization & Storage
    # We embed the logs into vector space and store them
    print("🧠 Vectorizing and Indexing (this may take a moment)...")
    
    ids = [f"id_{i}" for i in range(len(logs))]
    embeddings = model.encode(logs).tolist()
    
    collection.add(
        documents=logs,
        embeddings=embeddings,
        ids=ids
    )

    print(f"✅ Training Complete. stored {collection.count()} patterns in {DB_PATH}")
    print("🛡️  The Sentry now knows what 'Normal' looks like.")

if __name__ == "__main__":
    main()