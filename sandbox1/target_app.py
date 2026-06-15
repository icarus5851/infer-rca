import hashlib
from importlib import reload
import os
import uuid
import uvicorn
import traceback
import requests
from fastapi import FastAPI, Request
from auth import verify_user
from starlette.middleware.base import BaseHTTPMiddleware

class InferTracerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = uuid.uuid4().hex[:8] 
        
        try:
            response = await call_next(request)
            success_payload = {
                "trace_id": trace_id,
                "status": "success",
                "endpoint": request.url.path,
                "event": "200 OK" 
            }
            try:
                requests.post("http://localhost:5050/ingest-success", json=success_payload, timeout=0.5)
            except Exception:
                pass
                
            return response
            
        except Exception as e:
            error_trace = traceback.format_exc()
            extracted_tb = traceback.extract_tb(e.__traceback__)

            file_inventory = {} 
            files_payload = []  
            processed_filepaths = set()

            for frame in extracted_tb:
                filepath = frame.filename
                
                if "site-packages" in filepath or "venv" in filepath or filepath.startswith("<"):
                    continue
                
                clean_filename = os.path.basename(filepath)
                
                if filepath in processed_filepaths:
                    continue
                processed_filepaths.add(filepath)

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                    
                    file_inventory[file_hash] = {
                        "filename": clean_filename,
                        "filepath": filepath,
                        "content": content,
                        "hash": file_hash
                    }
                    
                    files_payload.append({
                        "filename": clean_filename,
                        "filepath": filepath,
                        "hash": file_hash
                    })
                except Exception:
                    continue 

            primary_crashed_file = files_payload[-1]["filename"] if files_payload else "Unknown"

            log_payload = {
                "trace_id": trace_id,
                "endpoint": request.url.path,
                "error_type": type(e).__name__,
                "traceback": error_trace,
                "primary_crashed_file": primary_crashed_file,
                "files": files_payload 
            }
            
            print("\n" + "="*60)
            print(f"[INFER] Crash Intercepted | Trace-ID: {trace_id}")
            print(f"[INFER] Primary File: {primary_crashed_file}")
            print("="*60 + "\n")
            
            try:
                response = requests.post("http://localhost:5050/ingest", json=log_payload, timeout=5)
                
                if response.status_code == 200:
                    agent_data = response.json()
                    missing_hashes = agent_data.get("missing_hashes", [])
                    
                    if missing_hashes:
                        print(f"[INFER] Agent requested {len(missing_hashes)} missing files. Uploading...")
                        
                        code_payload = {
                            "trace_id": trace_id,
                            "missing_files": [
                                file_inventory[h] for h in missing_hashes if h in file_inventory
                            ]
                        }
                        requests.post("http://localhost:5050/upload-code", json=code_payload, timeout=5)
                        
            except requests.exceptions.RequestException as req_err:
                print(f"[INFER-WARNING] Connection failed: {req_err}")
            
            raise e

app = FastAPI()
app.add_middleware(InferTracerMiddleware)

@app.get("/checkout/{user_id}")
async def run_checkout(user_id: str, cart_total: float = 25.00):
    user = verify_user(user_id)

    current_balance = user.get("balance")
    if current_balance < cart_total:
        return {"error": "Insufficient funds"}

    return {"status": "Success"}

if __name__ == "__main__":
    print("Starting target app on port 10000...")
    uvicorn.run(app, host="127.0.0.1", port=10000, access_log=False)