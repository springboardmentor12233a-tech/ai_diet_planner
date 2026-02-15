"""
Quick test to verify .env file is loading correctly
"""
from dotenv import load_dotenv
import os

print("Loading .env file...")
load_dotenv()

print("\nEnvironment Variables Status:")
print("=" * 50)

# Check Groq API Key
groq_key = os.getenv("GROQ_API_KEY")
if groq_key:
    print(f"✓ GROQ_API_KEY: {groq_key[:20]}... (loaded)")
else:
    print("✗ GROQ_API_KEY: Not found")

# Check USDA API Key
usda_key = os.getenv("USDA_API_KEY")
if usda_key:
    print(f"✓ USDA_API_KEY: {usda_key[:20]}... (loaded)")
else:
    print("✗ USDA_API_KEY: Not found")

# Check Encryption Key
encryption_key = os.getenv("NUTRICARE_ENCRYPTION_KEY")
if encryption_key:
    print(f"✓ NUTRICARE_ENCRYPTION_KEY: {encryption_key[:20]}... (loaded)")
else:
    print("✗ NUTRICARE_ENCRYPTION_KEY: Not found")

# Check NLP Model
nlp_model = os.getenv("NUTRICARE_NLP_MODEL", "bert")
print(f"✓ NUTRICARE_NLP_MODEL: {nlp_model}")

print("=" * 50)
print("\nIf all keys show as loaded, your .env file is working correctly!")
