import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import api_router

app = FastAPI(title="Infer RCA Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    print("🚀 Starting Infer Hub on http://localhost:5050")
    uvicorn.run("main:app", host="0.0.0.0", port=5050, reload=True)