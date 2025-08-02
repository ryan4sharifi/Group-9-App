import os
from dotenv import load_dotenv

# Load environment variables once
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Import mock database for assignment compliance when no real database available
try:
    from app.mock_database import mock_supabase
    MOCK_AVAILABLE = True
except ImportError:
    MOCK_AVAILABLE = False

# Try to import Supabase client
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Try to use Supabase database first, fall back to mock if needed
if SUPABASE_URL and SUPABASE_KEY and SUPABASE_AVAILABLE:
    try:
        print("Attempting Supabase database connection...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Test the connection
        test_result = supabase.table("user_credentials").select("id").limit(1).execute()
        print("✅ Supabase database connection successful")
    except Exception as e:
        print(f"⚠️ Supabase connection failed: {e}")
        if MOCK_AVAILABLE:
            print("Falling back to mock database")
            supabase = mock_supabase
        else:
            print("No fallback available")
            supabase = None
elif MOCK_AVAILABLE:
    print("Using mock database (hardcoded values) for assignment compliance")  #Enhanced message
    supabase = mock_supabase
else:
    print("Neither Supabase nor mock database available")
    supabase = None

def get_supabase_client():
    """Get Supabase client - returns mock client if no environment variables or Supabase unavailable"""
    #Enhanced function with better error handling and availability checks
    if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_AVAILABLE:
        if MOCK_AVAILABLE:
            return mock_supabase
        else:
            raise ValueError("Neither Supabase nor mock database available") 
    return create_client(SUPABASE_URL, SUPABASE_KEY)

async def check_database_health():
    """Check if database connection is healthy"""
    try:
        if supabase:
            # If using mock database, always return healthy
            if MOCK_AVAILABLE and not SUPABASE_URL:
                return {"status": "healthy", "database": "mock"}
            # Check if user_credentials table exists (our actual table name)
            response = supabase.table("user_credentials").select("id").limit(1).execute()
            return {"status": "healthy", "database": "supabase"}
        else:
            return {"status": "unhealthy", "database": "none"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}