# States Management Routes for US State Codes and Names
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.supabase_client import supabase

router = APIRouter()

class State(BaseModel):
    code: str  # 2-letter state code (e.g., "TX")
    name: str  # Full state name (e.g., "Texas")

# Get all US states
@router.get("/states", response_model=List[State])
async def get_all_states():
    """Get all US states with codes and names"""
    try:
        response = supabase.table("states").select("*").order("name").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve states: {str(e)}")

# Get state by code
@router.get("/states/{state_code}")
async def get_state_by_code(state_code: str):
    """Get state details by 2-letter code"""
    try:
        response = supabase.table("states").select("*").eq("code", state_code.upper()).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="State not found")
        return response.data
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="State not found")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve state: {str(e)}")

# Initialize states table with US states data (Admin function)
@router.post("/states/initialize")
async def initialize_states():
    """Initialize states table with all US states - run once during setup"""
    try:
        us_states = [
            {"code": "AL", "name": "Alabama"}, {"code": "AK", "name": "Alaska"},
            {"code": "AZ", "name": "Arizona"}, {"code": "AR", "name": "Arkansas"},
            {"code": "CA", "name": "California"}, {"code": "CO", "name": "Colorado"},
            {"code": "CT", "name": "Connecticut"}, {"code": "DE", "name": "Delaware"},
            {"code": "FL", "name": "Florida"}, {"code": "GA", "name": "Georgia"},
            {"code": "HI", "name": "Hawaii"}, {"code": "ID", "name": "Idaho"},
            {"code": "IL", "name": "Illinois"}, {"code": "IN", "name": "Indiana"},
            {"code": "IA", "name": "Iowa"}, {"code": "KS", "name": "Kansas"},
            {"code": "KY", "name": "Kentucky"}, {"code": "LA", "name": "Louisiana"},
            {"code": "ME", "name": "Maine"}, {"code": "MD", "name": "Maryland"},
            {"code": "MA", "name": "Massachusetts"}, {"code": "MI", "name": "Michigan"},
            {"code": "MN", "name": "Minnesota"}, {"code": "MS", "name": "Mississippi"},
            {"code": "MO", "name": "Missouri"}, {"code": "MT", "name": "Montana"},
            {"code": "NE", "name": "Nebraska"}, {"code": "NV", "name": "Nevada"},
            {"code": "NH", "name": "New Hampshire"}, {"code": "NJ", "name": "New Jersey"},
            {"code": "NM", "name": "New Mexico"}, {"code": "NY", "name": "New York"},
            {"code": "NC", "name": "North Carolina"}, {"code": "ND", "name": "North Dakota"},
            {"code": "OH", "name": "Ohio"}, {"code": "OK", "name": "Oklahoma"},
            {"code": "OR", "name": "Oregon"}, {"code": "PA", "name": "Pennsylvania"},
            {"code": "RI", "name": "Rhode Island"}, {"code": "SC", "name": "South Carolina"},
            {"code": "SD", "name": "South Dakota"}, {"code": "TN", "name": "Tennessee"},
            {"code": "TX", "name": "Texas"}, {"code": "UT", "name": "Utah"},
            {"code": "VT", "name": "Vermont"}, {"code": "VA", "name": "Virginia"},
            {"code": "WA", "name": "Washington"}, {"code": "WV", "name": "West Virginia"},
            {"code": "WI", "name": "Wisconsin"}, {"code": "WY", "name": "Wyoming"}
        ]
        
        # Insert all states
        response = supabase.table("states").insert(us_states).execute()
        return {"message": f"Successfully initialized {len(us_states)} states", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize states: {str(e)}")
