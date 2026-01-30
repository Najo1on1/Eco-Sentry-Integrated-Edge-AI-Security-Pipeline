import chromadb
from sentence_transformers import SentenceTransformer

class SentryGuard:
    def __init__(self, db_path="./chroma_db_storage"):
        print("🛡️  Sentry Agent Initializing...")
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_collection("normal_patterns")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.THRESHOLD = 0.12  # Strictness level (Lower = More paranoid)
        print("✅ Sentry Online. Monitoring for anomalies.")

    def check_log(self, log_line):
        """
        Returns a dict: {'is_threat': bool, 'score': float, 'log': str}
        """
        # 1. Convert log to vector
        query_vec = self.model.encode([log_line]).tolist()

        # 2. Query the DB for the closest "Normal" match
        results = self.collection.query(
            query_embeddings=query_vec,
            n_results=1  # We only need the single closest match
        )

        # 3. Analyze the distance
        # ChromaDB returns 'distances' (Euclidean or Cosine). 
        # For this model, smaller distance = more similar.
        # Approx: 0.0 is exact match, > 0.5 is starting to look weird.
        score = results['distances'][0][0]
        
        is_threat = score > self.THRESHOLD

        return {
            "is_threat": is_threat,
            "anomaly_score": round(score, 4),
            "log": log_line
        }

# ---------------------------------------------------------
# FAST TEST (Runs only if you execute this file directly)
# ---------------------------------------------------------
if __name__ == "__main__":
    agent = SentryGuard()
    
    # Test 1: A Normal Log
    print("\n--- TEST 1: Normal Traffic ---")
    log1 = '192.168.1.10 - - [30/Jan/2026:08:00:00 +0000] "GET /index.html HTTP/1.1" 200 1024'
    result1 = agent.check_log(log1)
    print(f"Log: {log1}")
    print(f"Result: {result1}")

    # Test 2: An Attack (SQL Injection)
    print("\n--- TEST 2: SQL Injection Attack ---")
    log2 = '192.168.66.6 - - [30/Jan/2026:08:05:00 +0000] "GET /login?user=\' OR \'1\'=\'1 HTTP/1.1" 403 0'
    result2 = agent.check_log(log2)
    print(f"Log: {log2}")
    print(f"Result: {result2}")