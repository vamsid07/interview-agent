from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

key = os.getenv("GROQ_API_KEY")
mock = os.getenv("USE_MOCK_API")

print("-" * 30)
print(f"Current Working Directory: {os.getcwd()}")
print(f"USE_MOCK_API: {mock}")
if key:
    print(f"GROQ_API_KEY found: {key[:5]}... (Hidden for safety)")
else:
    print("❌ GROQ_API_KEY is Missing or None")
print("-" * 30)