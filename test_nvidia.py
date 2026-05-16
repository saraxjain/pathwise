from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("NVIDIA_API_KEY")
print(f"Key loaded: {key[:10]}..." if key else "ERROR: No API key found!")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=key
)

response = client.chat.completions.create(
    model="nvidia/llama-3.3-nemotron-super-49b-v1",
    messages=[{"role": "user", "content": "Say hello and tell me you are Nemotron."}],
    max_tokens=100
)

print("Full response:", response)
print("Message:", response.choices[0].message.content)