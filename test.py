import requests
import io
from PIL import Image

API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": "Bearer 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"}

def query_huggingface(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    return response.content

# Test image generation
image_bytes = query_huggingface({"inputs": "A logo for an e-commerece website named shakani"})
if image_bytes:
    image = Image.open(io.BytesIO(image_bytes))
    image.show()  # Display the generated image
