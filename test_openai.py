import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print("Error: 'openai' package is not installed. Please run 'pip install openai'")
    sys.exit(1)

# The key provided by the user
API_KEY = os.getenv("OPENAI_API_KEY", "your-key-here")

def test_key():
    print(f"Testing OpenAI API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
    
    client = OpenAI(api_key=API_KEY)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, are you working?"}
            ],
            max_tokens=10
        )
        print("\nSUCCESS! Received response from OpenAI:")
        print(response.choices[0].message.content)
        return True
    except Exception as e:
        print("\nFAILURE! Could not connect to OpenAI.")
        print(f"Error details: {e}")
        return False

if __name__ == "__main__":
    test_key()
