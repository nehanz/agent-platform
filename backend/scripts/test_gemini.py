import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
load_dotenv()

from google import genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY is not set in .env")
    sys.exit(1)

client = genai.Client(api_key=api_key)

print("Listing supported models for generateContent:")
for model in client.models.list():
    name = model.name
    # Strip 'models/' if present
    base_name = name.replace("models/", "")
    supported_actions = getattr(model, "supported_generation_methods", []) or getattr(model, "supported_actions", [])
    print(f"- {base_name} (full: {name}) | actions: {supported_actions}")

# Test simple generation with gemini-3.8-flash / gemini-3.7-flash
for test_model in ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash", "gemini-flash-latest"]:
    try:
        res = client.models.generate_content(
            model=test_model,
            contents="Hi"
        )
        print(f"\n SUCCESS with model: {test_model} -> Response: {res.text}")
        break
    except Exception as e:
        print(f"\n Failed with model: {test_model} -> Error: {e}")
