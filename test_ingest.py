import cognee
import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def ingest():
    print("Reading payload...")
    with open("test_payloads/payload1_analyze.json", "r") as f:
        data = json.load(f)
    
    payload_text = data.get("payload", str(data))
    
    print("1. Adding payload to Cognee memory...")
    await cognee.add(payload_text, dataset_name="nq_live_trades")
    
    print("2. Cognifying (Extracting Knowledge Graph)...")
    await cognee.cognify()
    print("3. Cognify Complete!")

if __name__ == "__main__":
    asyncio.run(ingest())
