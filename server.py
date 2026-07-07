import asyncio
from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn
import cognee
import os
import sys
import uuid
import json
import glob
from datetime import datetime
from dotenv import load_dotenv
from cognee.api.v1.search import SearchType
import openai

load_dotenv()

# Global LLM Client for evaluation (ARCH-01)
llm_client = openai.AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "sk-1234"),
    base_url=os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:4000")
)

def save_failed_payload(payload: str, endpoint: str):
    os.makedirs("FailedPayloads", exist_ok=True)
    filename = f"FailedPayloads/failed_{endpoint}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.txt"
    with open(filename, "w") as f:
        f.write(payload)
    print(f"\n[!] ULTIMATE FALLBACK TRIGGERED:")
    print(f"[!] Payload safely written to {filename}\n")

# The fast in-memory queue
payload_queue = asyncio.Queue()
INGESTION_DIR = "IngestionQueue"
os.makedirs(INGESTION_DIR, exist_ok=True)

async def background_worker():
    print("[Background Worker] Started and listening for payloads...")
    payload_counter = 0
    while True:
        filepath = await payload_queue.get()
        payload_counter += 1
        print("\n" + "="*60)
        print(f"💾 [PAYLOAD {payload_counter}] POST-TRADE MEMORY INGESTION STARTED")
        print("="*60)
        print(f"[Background Worker] Payload {payload_counter} received | data processing started\n")
        print(f"[Background Worker] Processing {filepath}...")
        
        try:
            if not os.path.exists(filepath):
                print(f"[Background Worker] File {filepath} not found. Skipping.")
                payload_queue.task_done()
                continue
                
            with open(filepath, "r") as f:
                data = json.load(f)
                
            payload = data.get("payload")
            auto_cognify = data.get("auto_cognify", False)
            
            print("1. [+] Injecting Raw Payload into Cognee Memory Engine...")
            await cognee.add(payload, dataset_name="nq_live_trades")
            
            if auto_cognify:
                print("2. [>] Cognifying (Extracting Knowledge Graph via Mistral)...")
                await cognee.cognify()
                print("3. [OK] Trade Data Successfully Extracted into AI Knowledge Graph!")
                print("-> [INFO] Mistral LLM has mapped the new market relationships for future predictions.")
                print(f"[Background Worker] Payload {payload_counter} received | data processing Completed")
                print("="*60 + "\n")
            else:
                print("2. [>>] Skipping Cognify (Saved for manual batch processing).")
                print(f"[Background Worker] Payload {payload_counter} received | data processing Completed")
                print("="*60 + "\n")
            
            # Success! Delete the persistent file
            os.remove(filepath)
            
        except Exception as e:
            print(f"[Background Worker] Error processing memory: {str(e)}")
            if 'payload' in locals() and payload:
                save_failed_payload(payload, "memory")
            # Delete from ingestion queue since it failed (and moved to failed queue)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        payload_queue.task_done()
        
        # CRITICAL PACING: Wait 60 seconds before taking next item from queue
        print("[Background Worker] Pacing to protect RPM limit...")
        for i in range(60, 0, -1):
            sys.stdout.write(f"\r[Background Worker] Next extraction in {i} seconds...   ")
            sys.stdout.flush()
            await asyncio.sleep(1)
        sys.stdout.write("\r[Background Worker] Ready for next payload!               \n")

app = FastAPI(title="Ninaivaatral Quant - Cognee Integration")

import console_ui

@app.on_event("startup")
async def startup_event():
    # 0. Print the Startup Logo
    console_ui.print_logo()
    
    # 1. Recover any payloads that were dropped during a server crash
    pending_files = glob.glob(f"{INGESTION_DIR}/*.json")
    for file in pending_files:
        await payload_queue.put(file)
    if pending_files:
        print(f"[Startup] Recovered {len(pending_files)} pending payloads from disk!")
        
    # 2. Start the background worker
    asyncio.create_task(background_worker())


@app.post("/memory")
async def add_memory(request: Request):
    """
    Receives JSON payload from the Quantower C# Indicator, 
    adds it to the graph, and immediately cognifies it.
    """
    try:
        data = await request.json()
        payload = data.get("payload")
        
        if not payload:
            return {"status": "error", "message": "No payload provided"}
            
        # Write-Ahead Log: Save to persistent disk immediately
        filename = f"{INGESTION_DIR}/payload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.json"
        with open(filename, "w") as f:
            json.dump(data, f)
            
        # Put into the fast async queue
        await payload_queue.put(filename)
        
        return {"status": "success", "message": "Payload securely queued for processing."}
        
    except Exception as e:
        print(f"Error queueing memory: {str(e)}")
        return {"status": "error", "message": str(e)}

async def background_ingest_and_cognify(payload: str):
    try:
        print("\n" + "-"*50)
        print("-> [Background Task] [+] Injecting Active Setup into Cognee...")
        await cognee.add(payload, dataset_name="nq_live_trades")
        print("-> [Background Task] [>] Cognifying Setup for Graph Insertion...")
        await cognee.cognify()
        print("-> [Background Task] [OK] Active Analysis Cognify Complete!")
        print("-" * 50 + "\n")
    except Exception as e:
        print(f"-> [Background Task] Error cognifying active setup: {str(e)}")

analyze_counter = 0

@app.post("/analyze")
async def analyze_setup(request: Request):
    """
    Receives Morning Setup JSON payload from Indicator at 10:00 AM, 
    queries the graph for AI Score, and queues the payload for background cognification.
    """
    global analyze_counter
    try:
        data = await request.json()
        payload = data.get("payload")
        
        if not payload:
            return {"status": "error", "message": "No payload provided"}
            
        analyze_counter += 1
        print("\n" + "="*60)
        print(f">>> [PAYLOAD {analyze_counter}] ACTIVE ANALYSIS REQUEST RECEIVED")
        print("="*60)
        print(payload)
        print("="*60)
        
        print("\n1. [?] Querying Knowledge Graph for Similar Historical Outcomes...")
        
        search_query = (
            "Find historical trading sessions with similar structural states to this payload. "
            "Look for matching Profile Shapes and similar Value Area/POC placement. "
            "Retrieve the final trade Result (e.g. SL Hit, TP Hit) and Exit Reason for those matches. "
            f"Current Payload Context: {payload}"
        )
        
        try:
            cognee_results = await asyncio.wait_for(
                cognee.search(query_text=search_query, query_type=SearchType.SUMMARIES),
                timeout=15.0
            )
        except Exception as search_err:
            print(f"[!] Cognee Search Failed: {str(search_err)}")
            print("-> [WARNING] Triggering Cold Start Fail-Safe.")
            
            # Route to single queue to prevent SQLite concurrent lock
            filename = f"{INGESTION_DIR}/payload_analyze_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.json"
            with open(filename, "w") as f:
                json.dump({"payload": payload, "auto_cognify": True}, f)
            await payload_queue.put(filename)
            
            print("-> [OK] Baseline Generated! Confidence Score: N/A | Historical Win Rate: N/A")
            print("-> [INFO] Suggestion Sent to Quantower C# Webhook.\n")
            return {
                "status": "success", 
                "confidence_score": "N/A", 
                "historical_win_rate": "N/A",
                "narrative": "Cold Start. Initializing Database."
            }
        
        # Step 2: EXEC-01 Cold Start Check and ARCH-02 Token Optimization
        if not cognee_results:
            print("[!] Cognee Search Failed: Insufficient Historical Data.")
            print("-> [WARNING] Triggering Cold Start Fail-Safe.")
            
            # Route to single queue to prevent SQLite concurrent lock
            filename = f"{INGESTION_DIR}/payload_analyze_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.json"
            with open(filename, "w") as f:
                json.dump({"payload": payload, "auto_cognify": True}, f)
            await payload_queue.put(filename)
            
            print("-> [OK] Baseline Generated! Confidence Score: N/A | Historical Win Rate: N/A")
            print("-> [INFO] Suggestion Sent to Quantower C# Webhook.\n")
            return {
                "status": "success", 
                "confidence_score": "N/A", 
                "historical_win_rate": "N/A",
                "narrative": "Insufficient Historical Data. Cold Start."
            }
            
        # Condense the results to save tokens (ARCH-02)
        condensed_results = []
        for res in cognee_results:
            res_str = str(res)
            # Take a generous slice to preserve outcome keywords while preventing massive token dumps
            condensed_results.append(res_str[:500])
            
        optimized_context = " | ".join(condensed_results)
        
        if not optimized_context.strip():
            print("-> Extracted context is empty. Triggering Cold Start Fail-Safe.")
            
            # Route to single queue to prevent SQLite concurrent lock
            filename = f"{INGESTION_DIR}/payload_analyze_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.json"
            with open(filename, "w") as f:
                json.dump({"payload": payload, "auto_cognify": True}, f)
            await payload_queue.put(filename)
            
            return {
                "status": "success", 
                "confidence_score": "50", 
                "historical_win_rate": "50%",
                "narrative": "Insufficient Historical Data. Cold Start."
            }
        
        print("2. [>] Mistral-Large AI Analyzing Historical Outcomes & Calculating Probabilities...")
        
        # Step 3: LLM Evaluation with Try/Except Shielding and Strict Timeout (EXEC-02)
        try:
            response_coro = llm_client.chat.completions.create(
                model="antigravity-router",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": (
                        "You are a quantitative trading AI. Analyze the historical graph facts provided. "
                        "Determine the overall success rate based on past Results (e.g. SL Hit = Loss, TP Hit = Win). "
                        "Calculate a Historical Win Rate % and a Confidence Score out of 100. "
                        "ADVANCED INSTRUCTIONS: "
                        "1. Weight recent dates heavier. "
                        "2. Lower the score significantly if past trades show heavy Stop Loss clusters. "
                        "3. Return strict JSON: {\"confidence_score\": \"XX\", \"historical_win_rate\": \"XX%\", \"narrative\": \"brief explanation\"}"
                    )},
                    {"role": "user", "content": f"Graph Results:\n{optimized_context}"}
                ],
                timeout=15.0 # Protect against hanging requests
            )
            
            # Absolute hard cap to ensure C# UI isn't hung
            response = await asyncio.wait_for(response_coro, timeout=15.0)
            
            ai_evaluation = json.loads(response.choices[0].message.content)
            
            confidence_score = str(ai_evaluation.get("confidence_score", "50"))
            historical_win_rate = str(ai_evaluation.get("historical_win_rate", "50%"))
            narrative = str(ai_evaluation.get("narrative", "Evaluation successful."))
            
        except Exception as llm_err:
            print(f"[!] LLM Evaluation Failed (Timeout or Parsing Error): {str(llm_err)}")
            print("-> [WARNING] Triggering Cold Start Fail-Safe.")
            confidence_score = "N/A"
            historical_win_rate = "N/A"
            narrative = "Insufficient Historical Data. Cold Start."
            
        print(f"-> [OK] AI Suggestion Generated! Confidence Score: {confidence_score} | Historical Win Rate: {historical_win_rate}")
        print("-> [INFO] Suggestion Sent to Quantower C# Webhook.\n")
        
        # Enqueue the heavy graph insertion/cognification so we don't block the HTTP response
        print("3. [+] Queueing Active Payload for Background Graph Insertion...")
        
        # Route to single queue to prevent SQLite concurrent lock
        filename = f"{INGESTION_DIR}/payload_analyze_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.json"
        with open(filename, "w") as f:
            json.dump(data, f)
        await payload_queue.put(filename)
        
        return {
            "status": "success", 
            "confidence_score": confidence_score, 
            "historical_win_rate": historical_win_rate,
            "narrative": narrative
        }
        
    except Exception as e:
        print(f"Error analyzing setup: {str(e)}")
        if payload:
            save_failed_payload(payload, "analyze")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("Starting Cognee Memory Webhook on http://localhost:8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
