"""
FastAPI App Entrypoint for Charlie Munger RAG Agent
Configures and initializes the complete FastAPI application
"""
# Load environment variables first, before any other imports
from dotenv import load_dotenv
load_dotenv()

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes import router
from backend.app.config.config import settings
from backend.app.dependencies import initialize_dependencies, shutdown_dependencies
from backend.app import routes

# Create FastAPI application
app = FastAPI(
    title="Charlie Munger RAG Agent",
    description="A sophisticated RAG system inspired by Charlie Munger's multidisciplinary thinking",
    version="0.1.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize all dependencies on startup"""
    print("Starting Charlie Munger RAG Agent...")
    # System will be initialized via routes module
    # Configure DSPy settings
    dspy_config = {
        'enable_dspy': True,
        'model_name': 'gpt-4-turbo-preview',
        'fallback_on_error': True,
        'auto_train': False
    }
    
    # Initialize all dependencies (vector store + DSPy)
    results = initialize_dependencies(dspy_config)
    
    if results['vector_store']:
        print("Vector store: Initialized")
        routes._system_initialized = True
    else:
        print("Vector store: Failed - limited functionality")
    
    if results['dspy']:
        print("DSPy system: Available")
    else:
        print("DSPy system: Fallback mode")
    
    print("Application startup complete!")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown all dependencies"""
    print("Shutting down Charlie Munger RAG Agent...")
    shutdown_dependencies()
    print("Application shutdown complete!")

# Include API routes
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0", 
        port=8000,
        reload=settings.debug
    )