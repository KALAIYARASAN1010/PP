import os
import sys
import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print(" IPMPRS: Intelligent Proposal Management & Precedent Retrieval")
    print(" Police Department Institutional Knowledge System")
    print("=" * 65)
    print("Starting server at http://127.0.0.1:8000 ...")
    print("Open http://127.0.0.1:8000 in your browser to access the application.")
    print("=" * 65)
    
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
