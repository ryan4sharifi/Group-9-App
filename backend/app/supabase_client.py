from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

#changed this so we can run the tests without needing to set up a Supabase instance
def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing Supabase environment variables")
    return create_client(SUPABASE_URL, SUPABASE_KEY)