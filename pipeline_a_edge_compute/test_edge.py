import time
from openai import OpenAI

# vLLM acts as a drop-in replacement for OpenAI API
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"  # vLLM doesn't require an API key locally
)

def benchmark_speed():
    print("⚡ Connecting to Edge Node (TinyLlama-1.1B)...")
    
    start_time = time.time()
    
    # We ask a question that requires a bit of text generation
    stream = client.chat.completions.create(
        model="TheBloke/TinyLlama-1.1B-Chat-v1.0-AWQ",
        messages=[{"role": "user", "content": "List 10 distinct benefits of using edge computing for AI drones."}],
        stream=True
    )

    print("🤖 Receiving tokens...")
    token_count = 0
    for chunk in stream:
        if chunk.choices[0].delta.content:
            token_count += 1
            # Optional: Print generation in real-time
            # print(chunk.choices[0].delta.content, end="", flush=True)

    end_time = time.time()
    duration = end_time - start_time
    speed = token_count / duration

    print(f"\n\n✅ Request Complete.")
    print(f"📊 Stats: {token_count} tokens generated in {duration:.2f} seconds.")
    print(f"🚀 Speed: {speed:.2f} tokens/sec")

if __name__ == "__main__":
    benchmark_speed()