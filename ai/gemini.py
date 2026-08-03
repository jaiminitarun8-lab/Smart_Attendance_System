import os
from dotenv import load_dotenv
from google import genai

# Load .env file
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def ask_gemini(question):
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=question,
        )

        return response.text

    except Exception as e:
        return f"Gemini Error: {str(e)}"