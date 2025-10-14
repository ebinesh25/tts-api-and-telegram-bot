import os
from supabase import create_client, Client
from supabase.client import ClientOptions
from dotenv import load_dotenv

load_dotenv()

class SupabaseManager:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_ANON_KEY")
        supabase: Client = create_client(
            url,
            key,
            options=ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=10,
                schema="public",
            )
        )
        self.supabase = supabase
    
    def get_articles(self):
        return self.supabase.table("articles").select("*").execute()
    
    def insert_article(self, json_data: dict):
        return self.supabase.table("articles").insert(json_data).execute()
    
    def delete_article(self, id:str):
        return self.supabase.table("articles").delete().eq("id", id).execute()
    
    def get_article(self, id:str):
        return self.supabase.table("articles").select("*").eq("id", id).execute()
    


supabase = SupabaseManager().supabase
res = supabase.table("articles").select("*").limit(1).execute()
print(res)