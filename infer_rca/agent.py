import uvicorn
import requests
from fastapi import FastAPI, Request
from engine import analyze_crash

app = FastAPI(title="Infer RCA Agent")

SPLUNK_HEC_TOKEN = "your-token-here" 

SPLUNK_HEC_URL = "https://localhost:8088/services/collector/event"

def forward_to_splunk(log_data):
    """Sends the intercepted log to the local Splunk database."""
    headers = {
        "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
        "Content-Type": "application/json"
    }
    
    splunk_payload = {
        "event": log_data
    }
    
    try:
        response = requests.post(
            SPLUNK_HEC_URL, 
            headers=headers, 
            json=splunk_payload, 
            verify=False,
            timeout=3
        )
        
        if response.status_code == 200:
            print("✅ [SPLUNK] Log successfully vaulted!")
        else:
            print(f"❌ [SPLUNK REJECTED] Code: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ [SPLUNK CONNECTION ERROR] Could not reach {SPLUNK_HEC_URL}")
        print("   Did you enable HEC globally in Splunk settings?")

@app.post("/ingest")
async def receive_log(request: Request):
    payload = await request.json()
    
    trace_id = payload.get("trace_id", "UNKNOWN")
    error_type = payload.get("error_type", "UNKNOWN")
    
    print(f"\n📥 [INFER AGENT] Received Crash Report: {trace_id}")
    print(f"   -> Error: {error_type}")
    print("   -> Forwarding to Splunk vault...")

    forward_to_splunk(payload)
    traceback_text = payload.get("traceback", "")
    crashed_code = payload.get("crashed_code", "") 
    
    if traceback_text:
        from_memory, analysis = analyze_crash(traceback_text, crashed_code)
        print("\n================== AI SOLUTION ==================")
        print(analysis)
        print("=================================================\n")
    
    return {"status": "received", "trace_id": trace_id}

def start_agent():
    print(" Starting Infer Local Agent on http://localhost:5050")
    uvicorn.run(app, host="0.0.0.0", port=5050)

if __name__ == "__main__":
    start_agent()