import os
import time
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

def analyze_crash(traceback_text, crashed_code):
    
    print("   -> [AI ENGINE] Searching ChromaDB memory...")
    
    # Search Memory for similar errors
    results = vector_db.similarity_search_with_score(traceback_text, k=1)
    
    if results and results[0][1] < 0.3:
        print("   -> [AI ENGINE] Exact match found in local memory!")
        return True, results[0][0].metadata['root_cause']

    print("   -> [AI ENGINE] Unseen error. Querying Groq (Llama-3-70B)...")
    
    # Feed both the error and the actual code
    prompt = f"""
    You are an expert backend developer debugging a server crash.
    
    Here is the exact Error Traceback:
    {traceback_text}
    
    Here is the ENTIRE source code for the file where the crash occurred:
    {crashed_code}
    
    Analyze the full file for interrelated issues (bad logic, wrong types, missing keys). 
    Provide a brief Root Cause Analysis and exactly one code block to fix it. Keep it concise.
    """
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
    analysis = response.choices[0].message.content

    # Save the new solution into ChromaDB
    vector_db.add_texts(
        texts=[traceback_text],
        metadatas=[{"root_cause": analysis}],
        ids=[str(time.time())]
    )
    
    return False, analysis