from dotenv import load_dotenv
import os
from together import Together
import requests

load_dotenv()  # Load environment variables from .env

# TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

client = Together()

image = client.images.generate(
    prompt="Cats eating popcorn",
    model="black-forest-labs/FLUX.1-schnell-Free",
    steps=2,
    n=1,
    format = "jpeg"
)



url = image.data[0].url
response = requests.get(url)

with open("output.jpg", "wb") as f:
    f.write(response.content)
#