import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables once
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validate required environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")

# Initialize Supabase client
try:
    print("Attempting Supabase database connection...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    # Test the connection
    test_result = supabase.table("user_credentials").select("id").limit(1).execute()
    print("✅ Supabase database connection successful")
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")
    raise ConnectionError(f"Failed to connect to Supabase database: {e}")

def get_supabase_client():
    """Get Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

async def check_database_health():
    """Check if database connection is healthy"""
    try:
        if supabase:
            # Check if user_credentials table exists
            response = supabase.table("user_credentials").select("id").limit(1).execute()
            return {"status": "healthy", "database": "supabase"}
        else:
            return {"status": "unhealthy", "database": "none"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}