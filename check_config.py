"""
Quick test script to verify environment configuration
Run this to check if your deployment is properly configured
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("ENVIRONMENT CONFIGURATION CHECK")
print("=" * 60)

# Check mistral_api_key
mistral_key = os.getenv("mistral_api_key")
if mistral_key and mistral_key.strip():
    print("✓ mistral_api_key: CONFIGURED")
    print(f"  Length: {len(mistral_key)} characters")
else:
    print("✗ mistral_api_key: MISSING OR EMPTY")
    print("  ⚠️  This will cause API failures!")
    print("  ➜ Set it in Railway: Variables → mistral_api_key")

print()

# Check PORT
port = os.getenv("PORT", "8000")
print(f"✓ PORT: {port}")

print()

# Test free APIs (these don't need keys)
print("Testing free APIs...")

try:
    import requests
    
    # Test Open-Meteo (weather)
    response = requests.get("https://api.open-meteo.com/v1/forecast?latitude=12.97&longitude=77.59&current=temperature_2m", timeout=5)
    if response.status_code == 200:
        print("✓ Open-Meteo API (weather): WORKING")
    else:
        print("✗ Open-Meteo API (weather): FAILED")
    
    # Test Nominatim (geocoding)
    headers = {"User-Agent": "TourismAIAgent/1.0"}
    response = requests.get("https://nominatim.openstreetmap.org/search?q=Bangalore&format=json&limit=1", headers=headers, timeout=5)
    if response.status_code == 200:
        print("✓ Nominatim API (geocoding): WORKING")
    else:
        print("✗ Nominatim API (geocoding): FAILED")
    
    # Test Overpass (places)
    response = requests.get("https://overpass-api.de/api/status", timeout=5)
    if response.status_code == 200:
        print("✓ Overpass API (places): WORKING")
    else:
        print("✗ Overpass API (places): FAILED")
        
except Exception as e:
    print(f"✗ API test failed: {e}")

print()
print("=" * 60)

if mistral_key and mistral_key.strip():
    print("STATUS: Ready to deploy ✓")
else:
    print("STATUS: Configuration incomplete ✗")
    print("Action required: Set mistral_api_key in Railway")
    
print("=" * 60)
