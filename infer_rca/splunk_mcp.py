import requests
import urllib.parse

SPLUNK_HOST = "https://localhost:8089" 
SPLUNK_USER = "your-username"
SPLUNK_PASS = "your-password" 

def get_historical_context(error_type: str, primary_file: str) -> str:
    print(f"🔍 [MCP] Querying Splunk history for: {error_type} in {primary_file}...")
    
    search_query = f'search index=main "{error_type}" "{primary_file}" earliest=-7d | stats count'
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"search": search_query, "output_mode": "json", "exec_mode": "oneshot"}
    
    try:
        response = requests.post(
            f"{SPLUNK_HOST}/services/search/jobs",
            headers=headers,
            data=urllib.parse.urlencode(data),
            auth=(SPLUNK_USER, SPLUNK_PASS),
            verify=False,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            count = 0
            if "results" in result and len(result["results"]) > 0:
                count = result["results"][0].get("count", 0)
            
            history_str = f"This '{error_type}' in '{primary_file}' has occurred {count} times in the last 7 days."
            print(f"   -> [MCP] {history_str}")
            return history_str
        else:
            return "Historical context unavailable. Assume this is a new error."
            
    except Exception as e:
        return "Historical context unavailable due to connection timeout."