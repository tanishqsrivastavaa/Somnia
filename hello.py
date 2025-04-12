import supabase
import vecs
from dotenv import load_dotenv
import os
load_dotenv()

db_key = os.getenv("SUPABASE_KEY")
sp_url = os.getenv("SUPABASE_URL")

client = supabase.create_client(supabase_key=db_key,supabase_url=sp_url)

#client.table("dream").insert({"user_id":"20","text":"I could feel the soothing silk wipe off my hands"}).execute()
client.table("dream").insert({
    "user_id":"222",
    "text":"testing the embedding",
    "embedding":[0.5,0.25,-0.09]
    }
    ).execute()


data = client.table("dream").select("").execute()
print(data.data)
