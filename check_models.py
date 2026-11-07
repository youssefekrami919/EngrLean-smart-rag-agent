"""Utility to list all supported Gemini models for your API key."""
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import google.generativeai as genai
from src.core.secrets import get_gemini_api_key

def main():
    key = get_gemini_api_key()
    genai.configure(api_key=key)
    print("=" * 60)
    print("Listing available models for your Gemini API Key...")
    print("=" * 60)
    
    embed_models = []
    chat_models = []
    
    try:
        for m in genai.list_models():
            methods = m.supported_generation_methods
            if "embedContent" in methods:
                embed_models.append(m.name)
            if "generateContent" in methods:
                chat_models.append(m.name)
                
        print("\n🔹 Embedding Models (for RAG / Vector search):")
        for em in embed_models:
            print(f"  • {em}")
            
        print("\n🔹 Chat & Generation Models (for conversation):")
        for cm in chat_models:
            print(f"  • {cm}")
            
        print("\n" + "=" * 60)
        print("✔ Check completed successfully!")
    except Exception as e:
        print(f"❌ Error querying models: {e}")

if __name__ == "__main__":
    main()

