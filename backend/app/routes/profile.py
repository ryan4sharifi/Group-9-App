# Routes for managing user profiles (create, read, update, delete)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr, Field 
from typing import Optional, List
from datetime import date
from app.supabase_client import supabase

router = APIRouter()

# Pydantic model for user profile excluding the ID
class UserProfileWithoutID(BaseModel):
    full_name: Optional[constr(max_length=50)] = None
    address1: Optional[constr(max_length=100)] = None
    address2: Optional[constr(max_length=100)] = None
    city: Optional[constr(max_length=100)] = None
    state: Optional[constr(min_length=2, max_length=2)] = None
    zip_code: Optional[constr(min_length=5, max_length=9)] = None
    skills: List[str] 
    preferences: Optional[str] = None
    availability: Optional[date] = None
    role: Optional[constr(max_length=20)] = "volunteer"

# Create or update a profile for a given user
@router.post("/profile/{user_id}")
async def create_or_update_profile(user_id: str, profile: UserProfileWithoutID):
    try:
       
        data = profile.dict(exclude_none=True)
        data["user_id"] = str(user_id) 
        print("DATA RECEIVED:", data)

      
        if "availability" in data and isinstance(data["availability"], date):
            data["availability"] = data["availability"].isoformat()
        

        # Upsert into Supabase user_profiles table
        response = supabase.table("user_profiles").upsert(data, on_conflict=["user_id"]).execute()
        return {"message": "Profile saved", "data": response.data}
    except Exception as e:
        print("SERVER ERROR:", e)
        
        raise HTTPException(status_code=500, detail=f"Failed to save profile: {str(e)}")

# Retrieve a user's profile + email and role from credentials table
@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    try:
        # Get profile data - handle both real Supabase and mock database
        try:
            profile_res = supabase.table("user_profiles").select("*").eq("user_id", user_id).maybe_single().execute()
            profile_data = profile_res.data if profile_res and profile_res.data else {}
        except AttributeError:
            # Fallback for mock database that doesn't have maybe_single
            profile_res = supabase.table("user_profiles").select("*").eq("user_id", user_id).execute()
            profile_data = profile_res.data[0] if profile_res and profile_res.data else {}

        # Get credentials data - handle both real Supabase and mock database  
        try:
            creds_res = supabase.table("user_credentials").select("email, role").eq("id", user_id).maybe_single().execute()
            creds_data = creds_res.data if creds_res and creds_res.data else {}
        except AttributeError:
            # Fallback for mock database that doesn't have maybe_single
            creds_res = supabase.table("user_credentials").select("email, role").eq("id", user_id).execute()
            creds_data = creds_res.data[0] if creds_res and creds_res.data else {}

        # Ensure we have at least some data to return
        if not profile_data and not creds_data:
            raise HTTPException(status_code=404, detail="Profile not found")
            
        # Safely merge the data
        merged_data = {}
        if profile_data:
            merged_data.update(profile_data)
        if creds_data:
            merged_data.update(creds_data)
            
        return merged_data
    except HTTPException:
        raise
    except Exception as e:
        print("SERVER ERROR:", e) 
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profile: {str(e)}")

# Delete a profile from the system
@router.delete("/profile/{user_id}")
async def delete_profile(user_id: str):
    try:
        response = supabase.table("user_profiles").delete().eq("user_id", user_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found or already deleted")
        return {"message": "Profile deleted", "data": response.data}
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print("SERVER ERROR:", e)
        raise HTTPException(status_code=500, detail=f"Failed to delete profile: {str(e)}")
        print("SERVER ERROR:", e) 
        raise HTTPException(status_code=500, detail=f"Failed to delete profile: {str(e)}")
