import os
import time
from dotenv import load_dotenv
from google import genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(MODULE_DIR)

load_dotenv(os.path.join(BASE_DIR, ".env"))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

vector_db = Chroma(
    collection_name="rca_memory",
    embedding_function=embeddings,
    persist_directory=os.path.join(BASE_DIR, "chroma_db") 
)

def analyze_with_ai(error_text, code_context):
    """Checks memory for the error. If not found, asks Gemini and saves it."""
    
    results = vector_db.similarity_search_with_score(error_text, k=1)
    
    if results and results[0][1] < 0.3:
        return True, results[0][0].metadata['root_cause'] # True = From Memory

    prompt = f"""
    You are an expert developer debugging a server crash.
    Here is the exact Error Traceback:
    {error_text}
    Here is the Python code where the crash occurred:
    {code_context}
    Please provide a brief Root Cause Analysis and suggest a fix. 
    Keep your response concise.
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    vector_db.add_texts(
        texts=[error_text],
        metadatas=[{"root_cause": response.text}],
        ids=[str(time.time())]
    )
    
    return False, response.text # False = From AI