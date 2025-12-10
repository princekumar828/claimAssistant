import os
import sys

try:
    import google.generativeai as genai
except ImportError:
    print("Error: 'google-generativeai' package is not installed. Please run 'pip install google-generativeai'")
    sys.exit(1)

# The key provided by the user
API_KEY = os.getenv("GEMINI_API_KEY", "your-key-here")

def test_key():
    print(f"Testing Gemini API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
    
    genai.configure(api_key=API_KEY)
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello, are you working?")
        
        print("\nSUCCESS! Received response from Gemini:")
        print(response.text)
        return True
    except Exception as e:
        print("\nFAILURE! Could not connect to Gemini.")
        print(f"Error details: {e}")
        return False

if __name__ == "__main__":
    test_key()
