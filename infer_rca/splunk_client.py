import requests

SPLUNK_HEC_TOKEN = "your-token" 
SPLUNK_HEC_URL = "https://localhost:8088/services/collector/event"

def forward_to_splunk(log_data):
    """Sends the intercepted log to the local Splunk database."""
    headers = {
        "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
        "Content-Type": "application/json"
    }
    splunk_payload = {"event": log_data}
    
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
    except requests.exceptions.RequestException:
        print(f"❌ [SPLUNK CONNECTION ERROR] Could not reach {SPLUNK_HEC_URL}")