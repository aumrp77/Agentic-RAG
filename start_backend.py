#!/usr/bin/env python3
"""
Startup script for The Munger Talks backend
Initializes the Charlie Munger RAG system with all dependencies
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault("PYTHONPATH", str(project_root))

def main():
    """Main startup function"""
    print("🚀 Starting The Munger Talks Backend...")
    print("=" * 60)
    
    # Import and run the FastAPI app
    try:
        import uvicorn
        from backend.main import app
        
        print("📚 Charlie Munger RAG Agent initializing...")
        print("   - Vector store will initialize on first request")
        print("   - DSPy modules loading...")
        print("   - Memory system ready")
        print()
        print("🌐 Server starting on http://localhost:8000")
        print("📖 API docs available at http://localhost:8000/docs")
        print("💬 Chat endpoints ready at /chat/*")
        print()
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=[str(project_root / "backend")],
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Charlie Munger RAG Agent...")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
