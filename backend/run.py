import uvicorn
import os
import sys

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("=" * 60)
    print("  Starting AI Admission Counselling Agent Backend")
    print("  Access API Docs: https://admissionai-1.onrender.com/docs")
    print("  Access Frontend: https://admissionai-1.onrender.com/")
    print("=" * 60)
    uvicorn.run(
    "app.main:app",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8000))
)
