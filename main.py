from fastapi import FastAPI
from pydantic import BaseModel
# import supabase
from pydantic_ai.agent import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from dotenv import load_dotenv
import os
import asyncio
import supabase
from uuid import uuid4
# from sentence_transformers import SentenceTransformer
# import numpy as np
# import faiss
load_dotenv()


# embedding_model = SentenceTransformer("BAII/bge-large-en")

# dimensions = 1024
# faiss_index = faiss.IndexFlatL2(dimensions)





app = FastAPI() #uvicorn main:app --reload  

db_key = os.getenv("SUPABASE_KEY")
sp_url = os.getenv("SUPABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

model = GroqModel(model_name = "llama-3.3-70b-versatile",provider = GroqProvider(api_key = GROQ_API_KEY))

first_agent = Agent(model=model)

supabase_client = supabase.create_client(sp_url,db_key)

# Data Model
class Dream(BaseModel):
    user_id: str
    text: str


# '''locally storing data here for prototyping purpose'''
# dream_store = {} 
# dream_counter = 0


# Store a dream in Supabase
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
    
    structured_text = await first_agent.run(prompt)
    new_dream = {
        "id":str(uuid4()),
        "user_id":dream.user_id,
        "text":structured_text
    }
    
    response = supabase_client.table("dreams").insert(new_dream).execute()
    return {"status":"saved","dream_id":new_dream["id"]}


'''Continuing a specific dream'''
@app.get("/dream-response/{dream_id}")
async def generate_collective_response(user_id : str):
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

