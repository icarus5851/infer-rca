import os
import time
import json
from dotenv import load_dotenv
from google import genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from groq import Groq

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(MODULE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

vector_db = Chroma(
    collection_name="rca_memory",
    embedding_function=embeddings,
    persist_directory=os.path.join(BASE_DIR, "chroma_db") 
)

def extract_error_location_with_ai(log_text):
    """AGENT 1: Fast Router. Forces JSON output to find the file and line."""
    prompt = """You are a routing agent. Read these log lines and find the most recent fatal error. 
    Return ONLY a valid JSON object containing the primary 'file' name and the 'line' number. 
    Example: {"file": "app.py", "line": 42}"""
    
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": log_text}
        ],
        response_format={"type": "json_object"}
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except:
        return None

def analyze_with_groq(error_text, full_code):
    """AGENT 2: Heavy Debugger. Checks Memory first, then asks Groq 70B."""
    
    results = vector_db.similarity_search_with_score(error_text, k=1)
    if results and results[0][1] < 0.3:
        return True, results[0][0].metadata['root_cause'] 

    prompt = f"""
    You are an expert developer debugging a server crash.
    Here is the exact Error Traceback:
    {error_text}
    
    Here is the ENTIRE source code for the file where the crash occurred:
    {full_code}
    
    Analyze the full file for interrelated issues (bad imports, logic flaws, etc.). 
    Provide a brief Root Cause Analysis and exactly one code block to fix it. Keep it concise.
    """
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
    final_answer = response.choices[0].message.content

    vector_db.add_texts(
        texts=[error_text],
        metadatas=[{"root_cause": final_answer}],
        ids=[str(time.time())]
    )
    
    return False, final_answer