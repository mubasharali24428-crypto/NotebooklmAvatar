from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import avatar

app = FastAPI(title="AvatarLM API", description="Backend for the Avatar-Based NotebookLM", version="1.0.0")

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Explicitly allow frontend origin to work with credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(avatar.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the AvatarLM API"}
