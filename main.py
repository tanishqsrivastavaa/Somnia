from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
import supabase
from pydantic_ai.agent import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
import asyncio
from uuid import uuid4
from together import Together
import requests
load_dotenv()



app = FastAPI() #uvicorn main:app --reload  

db_key = os.getenv("SUPABASE_KEY")
sp_url = os.getenv("SUPABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")
supabase_client = supabase.create_client(sp_url,db_key)


'''-------AGENTS---------'''

#GroqAPI
model1 = GroqModel(model_name = "llama-3.3-70b-versatile",provider = GroqProvider(api_key = GROQ_API_KEY))
first_agent = Agent(model=model1)

# HuggingFace for image generation
model2=InferenceClient(
    provider="fal-ai",
    api_key=HF_API_KEY,
    model="HiDream-ai/HiDream-I1-Full"
)

image_client = Together()


# Data Model
class Dream(BaseModel):
    user_id: str
    text: str


# '''locally storing data here for prototyping purpose'''
# dream_store = {} 
# dream_counter = 0


# Store a dream in Supabase
#GET http://127.0.0.1:8000/dream
@app.post("/dream")
async def save_dream(dream: Dream):
    # global dream_counter
    # dream_store[dream_counter] = {
    #     "user_id" : dream.user_id,
    #     "text" : dream.text
    # }
    # response_id = dream_counter
    # dream_counter += 1
    # return {"status":"saved","dream_id" : response_id}
    prompt = f"""You are supposed to format the following text into a structured, vivid dream narrative in first person:
            {dream.text}
            Make it immersive, flow like a dream, and avoid any analysis or explanations. Just narrate as if you're recounting the dream."""
    
    structured_result = await first_agent.run(prompt)
    structured_text = structured_result.data
    new_dream = {
        "id":str(uuid4()),
        "user_id":dream.user_id,
        "text":dream.text,
        "structured_text":structured_text
    }
    
    response = supabase_client.table("dreams").insert(new_dream).execute()
    return {"status":"saved","dream_id":new_dream["id"]}


'''Continuing a specific dream'''
#POST http://127.0.0.1:8000/dream-response/user?user_id=
@app.get("/dream-response/user")
async def generate_collective_response(user_id : str = Query(...)):
    # dream = dream_store.get(dream_id)
    # if not dream:
    #     return {"error": "Dream not found"}
    response = supabase_client.table("dreams").select("*").eq("user_id",user_id).execute()
    dreams = response.data

    if not dreams:
        return {"error":"No dreams for this user."}
    
    all_dreams_text = "\n\n".join(d["text"] for d in dreams)
    
    prompt = f"""
    You are an AI dream weaver. These are a collection of dreams experienced by one person: 
    {all_dreams_text}
    Now, evolve these dreams into one surreal, cohesive, vivid dream experience.
    - The format should be in **first person**.
    - Make it immersive and continuous, as if it was one long night of dreaming.
    - Do not explain. Just narrate the dream directly.
    - Make sure it is about 100-200 words."""

    ai_response = await first_agent.run(prompt)
    # supabase_client.table("dreams").select("response").
    return {"response": ai_response}

# '''Testing agent's response'''
# async def test_agent():
#     response = await first_agent.run("Describe a surreal dream about a floating city.")
#     print(response)


# if __name__ == "__main__":
    # import asyncio
    # asyncio.run(test_agent())

#Second agent which turns the collective dreams into an image.
@app.get("/dream-generate/user")
async def generate_collective_image(user_id : str = Query(...)):
    response = supabase_client.table("dreams").select('*').eq("user_id",user_id).execute()
    dreams = response.data

    if not dreams:
        return {"error":"No dreams found for this user."}

    combined_dreams = "\n\n".join(d['text'] for d in dreams)
    
    prompt = f"""
    You are a surreal storyteller. Here's a set of dreams:
    {combined_dreams}
    Turn it into a visual, animative description in 1-2 sentences for an artist to paint.
    Be abstract and expressive.
    """

    summarized = await first_agent.run(prompt)
    dream_description = summarized.data.strip()

    # image = model2.text_to_image(dream_description)
    # file_path = f"{uuid4().hex}.png"
    # image.save(file_path)
    # return FileResponse(file_path,media_type="image/png")
    image = image_client.images.generate(
        prompt=dream_description,
        model="black-forest-labs/FLUX.1-schnell-Free",
        steps=2,
        n=1,
        height=1024,
        width=1024,
        format="jpeg"
)

    url = image.data[0].url
    response = requests.get(url)

    response2 = supabase_client.table("dreams").insert(url).execute()

    files = os.listdir()
    dream_images = [f for f in files if f.startswith("dream_image_") and f.endswith(".png")]
    numbers = []
    for name in dream_images:
        try:
            num = int(name.split("_")[-1].split(".")[0])
            numbers.append(num)
        except ValueError:
            continue

    next_num = max(numbers) + 1 if numbers else 1
    file_path = f"dream_images_{next_num}.png"

    with open("dream_image.png", "wb") as f:
        f.write(response.content)


    return FileResponse(file_path,media_type="image/png")


# '''TODO
# 1. Should append the image url into supabase
# 2. Re-format the code for better code quality
# 3. Make the front-end (use deepseek)'''
