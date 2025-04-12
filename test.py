from cerebras.cloud.sdk import Cerebras
import os
from dotenv import load_dotenv

load_dotenv()

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

model_name = 'llama-3.3-70b'

client = Cerebras(
    api_key=CEREBRAS_API_KEY
)

conv_history="""You are a guru who listens to everybody and gives advice which literally changes the person's perspective on life. You have a lot of experience in terms of living a life."""


while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit","quit"]:
        print("Conversation ended.")
        break

    conv_history += f"{user_input}"
    completion = client.completions.create(
        prompt=conv_history,
        model = model_name,
        max_tokens=200
    )

    response = completion.choices[0].text.strip()
    print(f"Bot: {response}")
    conv_history += f" {response}"