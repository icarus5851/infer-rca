import os
import time
import re
from dotenv import load_dotenv
from groq import Groq
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

vector_db = Chroma(
    collection_name="infer_memory",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

def sanitize_traceback(text):
    """
    Removes volatile memory addresses (e.g., 0x0001FA) from the traceback.
    This ensures ChromaDB can match the exact same error across different runs.
    """
    return re.sub(r'0x[0-9a-fA-F]+', '0x...', text)

def analyze_crash(traceback_text, crashed_code):
    print("   -> [AI ENGINE] Searching ChromaDB memory...")
    
    clean_traceback = sanitize_traceback(traceback_text)
    
    results = vector_db.similarity_search_with_score(clean_traceback, k=1)
    
    if results and results[0][1] < 0.3:
        print("   -> [AI ENGINE] Exact match found in local memory!")
        return True, results[0][0].metadata['root_cause']

    print("   -> [AI ENGINE] Unseen error. Querying Groq (Llama-3-70B)...")
    
    prompt = f"""
    You are an expert backend systems engineer diagnosing a server crash.
    
    Here is the telemetry data intercepted from the application:
    {traceback_text}
    
    Here is the ENTIRE source code for the primary file where the crash occurred:
    {crashed_code}
    
    INSTRUCTIONS:
    1. Read the "Splunk Historical Context" to understand if this is a recurring systemic issue or a one-off anomaly.
    2. Analyze the traceback and source code to identify the exact line of failure.
    3. Provide a brief Root Cause Analysis.
    4. Provide exactly one Markdown code block with the corrected code. Keep it concise.
    """
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
    analysis = response.choices[0].message.content

    vector_db.add_texts(
        texts=[clean_traceback],
        metadatas=[{"root_cause": analysis}],
        ids=[str(time.time())]
    )
    
    return False, analysis