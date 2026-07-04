# FVP IB Strategy - AI Backend Testing Guide

This repository contains the Python FastAPI and Cognee backend for the FVP IB Strategy. It is responsible for ingesting live market profile data, constructing a knowledge graph, and providing AI-driven trade probability scores.

## Prerequisites
Before running the backend, ensure you have the following installed on your machine:
- **Python 3.10+**

## Initial Setup (First-Time Only)

1. **Open a Terminal** in this directory (`FVP_IB_Cognee_Backend`).
2. **Activate the Virtual Environment**:
   - Windows: `.\.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables**:
   Open the `.env` file and ensure your API keys (such as `OPENAI_API_KEY` or LiteLLM endpoints) are populated.

## Starting the Backend

To boot the system, you only need to run a single command. 

1. Double-click the **`START_COGNEE_BACKEND.bat`** file, OR run it via terminal:
   ```bash
   .\START_COGNEE_BACKEND.bat
   ```

> [!NOTE] 
> **What does this do?** 
> This batch script automatically starts both the **LiteLLM Proxy** (for LLM routing) and the **Cognee FastAPI Engine** in parallel.

## Verifying the Server is Running

1. Once the terminal shows the startup logs, open a web browser.
2. Navigate to: `http://127.0.0.1:8000/docs`
3. If you see the FastAPI Swagger UI displaying the `/analyze` and `/memory` endpoints, the AI brain is successfully online and ready to receive payloads from the Quantower C# Engine.
