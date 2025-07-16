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

# Use mock database when environment variables are not available
if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_AVAILABLE:
    if MOCK_AVAILABLE:
        print("Using mock database (hardcoded values) for assignment compliance")  #Enhanced message
        supabase = mock_supabase
    else:
        print("Neither Supabase nor mock database available")
        supabase = None
else:
    print("Using Supabase database")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client():
    """Get Supabase client - returns mock client if no environment variables or Supabase unavailable"""
    #Enhanced function with better error handling and availability checks
    if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_AVAILABLE:
        if MOCK_AVAILABLE:
            return mock_supabase
        else:
            raise ValueError("Neither Supabase nor mock database available")  #Better error message
    return create_client(SUPABASE_URL, SUPABASE_KEY)