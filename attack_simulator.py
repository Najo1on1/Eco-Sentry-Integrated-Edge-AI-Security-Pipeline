import time
import pandas as pd
import sys
import os
from openai import OpenAI

# Import the Sentry Class from Pipeline B
sys.path.append(os.path.join(os.getcwd(), "pipeline_b_sentry_logic"))
from sentry_agent import SentryGuard

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
INPUT_FILE = "data/live_fire_log.txt"
OUTPUT_FILE = "monitor_stream.csv"
DELAY = 0.5  # Standard speed
EDGE_API_URL = "http://localhost:8000/v1"
EDGE_MODEL = "TheBloke/TinyLlama-1.1B-Chat-v1.0-AWQ"

def consult_edge_node(log_line):
    """
    Sends the suspicious log to the Local Edge LLM for analysis.
    """
    try:
        client = OpenAI(base_url=EDGE_API_URL, api_key="EMPTY")
        
        prompt = f"Analyze this server log and identify the attack type in 1 short sentence: '{log_line}'"
        
        response = client.chat.completions.create(
            model=EDGE_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60, # Keep it short for speed
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Edge Node Offline: {e}"

def main():
    print("🚀 Initializing Live Fire Exercise (With Cognitive Edge Support)...")
    
    # 1. Initialize Sentry
    sentry = SentryGuard(db_path="pipeline_b_sentry_logic/chroma_db_storage")
    
    # 2. Load Traffic
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Input file {INPUT_FILE} not found.")
        return
    
    with open(INPUT_FILE, "r") as f:
        traffic_logs = [line.strip() for line in f.readlines()]
    
    # 3. Reset Monitor Stream
    pd.DataFrame(columns=["timestamp", "score", "is_threat", "log", "analysis"]).to_csv(OUTPUT_FILE, index=False)

    print(f"📥 Loaded {len(traffic_logs)} requests. Starting replay...")

    # 4. The Loop
    try:
        for i, log_line in enumerate(traffic_logs):
            # A. Sentry Check
            analysis = sentry.check_log(log_line)
            
            ai_explanation = ""
            
            # B. If Threat -> Consult Edge Node
            if analysis['is_threat']:
                print(f"🔴 [{i}] THREAT DETECTED! Consulting Edge Node...")
                ai_explanation = consult_edge_node(log_line)
                print(f"   🤖 Edge AI says: {ai_explanation}")
                status_icon = "🔴"
            else:
                status_icon = "🟢"
                print(f"{status_icon} [{i}] Score: {analysis['anomaly_score']:.4f}")
            
            # C. Append to CSV (Now with AI Analysis)
            # Note: We added an 'analysis' column
            new_row = pd.DataFrame([{
                "timestamp": time.strftime("%H:%M:%S"),
                "score": analysis['anomaly_score'],
                "is_threat": analysis['is_threat'],
                "log": log_line,
                "analysis": ai_explanation
            }])
            
            # Append carefully to match header
            new_row.to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
            
            time.sleep(DELAY)

    except KeyboardInterrupt:
        print("\n🛑 Simulation Stopped.")

if __name__ == "__main__":
    main()