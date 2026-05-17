import os
import sys

def check_environment():
    errors = []
    
    if sys.version_info < (3, 11):
        errors.append("Python version must be 3.11 or higher.")
        
    if not os.path.exists(".env"):
        errors.append("Missing .env file. Copy from .env.example.")
    else:
        with open(".env", "r") as f:
            content = f.read()
            if "OPENAI_API_KEY" not in content or "sk-" not in content:
                errors.append("OPENAI_API_KEY seems invalid or missing.")
            if "PINECONE_API_KEY" not in content:
                errors.append("PINECONE_API_KEY missing.")
                
    if errors:
        print("[FAIL] Environment validation failed:")
        for e in errors:
            print(f" - {e}")
        sys.exit(1)
        
    print("[SUCCESS] Environment is ready for production deployment.")

if __name__ == "__main__":
    check_environment()
