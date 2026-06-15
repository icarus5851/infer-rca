import os
import time
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from splunk_client import forward_to_splunk
from agent import analyze_crash
from graph_builder import analyze_directory
from splunk_mcp import get_historical_context

api_router = APIRouter()

latest_crashed_node = None
latest_trace_id = None
crash_vault = {}
live_log_trail = [] 

CACHE_DIR = os.path.join(os.path.dirname(__file__), "file_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def add_to_live_trail(log_entry):
    global live_log_trail
    live_log_trail.insert(0, log_entry)
    if len(live_log_trail) > 50:
        live_log_trail.pop()

@api_router.post("/ingest-success")
async def receive_success(request: Request, background_tasks: BackgroundTasks):
    """Clears the red node and logs a success heartbeat."""
    global latest_crashed_node, latest_trace_id
    payload = await request.json()

    latest_crashed_node = None 
    latest_trace_id = None
    
    log_entry = {"timestamp": time.time(), "status": "SUCCESS", "endpoint": payload.get("endpoint")}
    add_to_live_trail(log_entry)
    
    background_tasks.add_task(forward_to_splunk, payload)
    return {"status": "cleared"}

@api_router.post("/ingest")
async def receive_log(request: Request, background_tasks: BackgroundTasks):
    global latest_crashed_node, latest_trace_id
    payload = await request.json()
    
    trace_id = payload.get("trace_id", "UNKNOWN")
    files_list = payload.get("files", [])
    primary_file = payload.get("primary_crashed_file")
    
    print(f"\n📥 [INFER AGENT] Received Crash Report: {trace_id}")
    
    if primary_file:
        latest_crashed_node = primary_file
        latest_trace_id = trace_id
        
    crash_vault[trace_id] = payload
    
    log_entry = {"timestamp": time.time(), "status": "ERROR", "endpoint": payload.get("endpoint"), "file": primary_file}
    add_to_live_trail(log_entry)
    
    background_tasks.add_task(forward_to_splunk, payload)

    missing_hashes = set()
    for f in files_list:
        file_hash = f.get("hash")
        cache_path = os.path.join(CACHE_DIR, f"{file_hash}.txt")
        if not os.path.exists(cache_path):
            missing_hashes.add(file_hash)
            
    if missing_hashes:
        return {"status": "missing_files", "missing_hashes": list(missing_hashes), "trace_id": trace_id}
    else:
        return {"status": "received_and_ready", "trace_id": trace_id}

@api_router.post("/upload-code")
async def receive_missing_code(request: Request):
    payload = await request.json()
    trace_id = payload.get("trace_id")
    missing_files = payload.get("missing_files", [])
    
    for f in missing_files:
        file_hash = f.get("hash")
        content = f.get("content", "")
        if file_hash:
            cache_path = os.path.join(CACHE_DIR, f"{file_hash}.txt")
            with open(cache_path, "w", encoding="utf-8") as file:
                file.write(content)
                
    return {"status": "code_saved", "trace_id": trace_id}

@api_router.post("/diagnose/{trace_id}")
async def run_diagnostics(trace_id: str):
    if trace_id not in crash_vault:
        raise HTTPException(status_code=404, detail="Trace ID not found in vault.")
        
    payload = crash_vault[trace_id]
    primary_file = payload.get("primary_crashed_file")
    error_type = payload.get("error_type", "UnknownError")
    traceback_text = payload.get("traceback", "")
    
    crashed_code = "Code not found in cache."
    target_hash = next((f["hash"] for f in payload.get("files", []) if f["filename"] == primary_file), None)
    
    if target_hash:
        cache_path = os.path.join(CACHE_DIR, f"{target_hash}.txt")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                crashed_code = f.read()

    splunk_historical_context = get_historical_context(error_type, primary_file)

    print(f"\n🤖 [AI ENGINE] Running Diagnostics on Trace: {trace_id}...")
    enriched_traceback = f"Splunk Historical Context: {splunk_historical_context}\n\nTraceback:\n{traceback_text}"
    
    from_memory, analysis = analyze_crash(traceback_text=enriched_traceback, crashed_code=crashed_code)
    
    return {
        "trace_id": trace_id,
        "from_memory": from_memory,
        "analysis": analysis,
        "historical_context": splunk_historical_context
    }

@api_router.get("/graph-data")
async def get_architecture_graph():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_directory = os.path.join(current_dir, "..", "sandbox1")
    try:
        if not os.path.exists(target_directory):
            return {"error": f"Sandbox directory not found"}
        return analyze_directory(target_directory)
    except Exception as e:
        return {"error": str(e)}

@api_router.get("/latest-crash")
async def get_latest_crash():
    return {"crashed_node": latest_crashed_node, "trace_id": latest_trace_id}

@api_router.get("/live-logs")
async def get_live_logs():
    return {"logs": live_log_trail}