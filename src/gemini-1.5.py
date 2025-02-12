
"""
    This file is used to interact with the LLM API. We're using Gemini 1.5 flash model to generate content.
    The POST function sends a POST request to the LLM API and returns the text response.
    The API key is stored in a .env file.
    The POST function takes a prompt as an argument and returns the text response from the LLM API.
    The prompt must be a string.
    The response is a JSON object that contains the generated content.
    The generated content is extracted from the JSON object and returned as a string.
"""

from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
API_KEY = os.getenv("API_KEY")

def POST(prompt: str):
    """Send a POST request to the LLM API.
    Args:
        prompt (str): The prompt to send to the LLM API.
    Returns:
        content: Text response from the LLM API.
    """
    assert isinstance(prompt, str), "Prompt must be a string"
    headers = {'Content-Type: application/json'}
    print("Sending POST request to LLM API...")
    res = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}", json={
        "contents": [{
            "parts": [{
                "text": f"{prompt}"
            }]
        }]
    })
    content = json.loads(res.text)
    return content["candidates"][0]["content"]["parts"][0]["text"]