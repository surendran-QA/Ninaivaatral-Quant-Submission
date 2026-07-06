import requests
import json
import time
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ANALYZE_URL = "http://localhost:8000/analyze"
MEMORY_URL = "http://localhost:8000/memory"

def run_test():
    print("========================================")
    print("  NINAIVAATRAL DATA LIFECYCLE TEST      ")
    print("========================================")
    
    # 1. Test /analyze endpoint
    print("\n[STEP 1] Testing /analyze (Pre-Trade Active Analysis)...")
    with open(os.path.join(SCRIPT_DIR, "payload1_analyze.json"), "r") as f:
        analyze_payload = json.load(f)
        
    try:
        start_time = time.time()
        res = requests.post(ANALYZE_URL, json=analyze_payload, timeout=30.0)
        elapsed = time.time() - start_time
        print(f"Status Code: {res.status_code} (in {elapsed:.2f}s)")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"Error testing /analyze: {str(e)}")
        
    # 2. Test /memory endpoint
    print("\n[STEP 2] Testing /memory (Post-Trade Memory Recap)...")
    with open(os.path.join(SCRIPT_DIR, "payload2_memory.json"), "r") as f:
        memory_payload = json.load(f)
        
    # Adding auto_cognify flag to force immediate background extraction in test
    memory_payload["auto_cognify"] = True
        
    try:
        start_time = time.time()
        res = requests.post(MEMORY_URL, json=memory_payload, timeout=30.0)
        elapsed = time.time() - start_time
        print(f"Status Code: {res.status_code} (in {elapsed:.2f}s)")
        print(f"Response: {res.json()}")
    except Exception as e:
        print(f"Error testing /memory: {str(e)}")
        
    print("\n[TEST COMPLETE] Check your backend server terminal to verify the Background Worker processes the queues successfully.")

if __name__ == "__main__":
    run_test()
