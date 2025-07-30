from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr, Field 
from typing import Optional, List
from datetime import date
from app.supabase_client import supabase

router = APIRouter()

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

@router.post("/profile/{user_id}")
async def create_or_update_profile(user_id: str, profile: UserProfileWithoutID):
    try:
       
        data = profile.dict(exclude_none=True)
        data["user_id"] = str(user_id) 
        print("DATA RECEIVED:", data)

      
        if "availability" in data and isinstance(data["availability"], date):
            data["availability"] = data["availability"].isoformat()
        

        response = supabase.table("user_profiles").upsert(data, on_conflict=["user_id"]).execute()
        return {"message": "Profile saved", "data": response.data}
    except Exception as e:
        print("SERVER ERROR:", e)
        
        raise HTTPException(status_code=500, detail=f"Failed to save profile: {str(e)}")

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    try:
        
        profile_res = supabase.table("user_profiles").select("*").eq("user_id", user_id).maybe_single().execute()
        profile_data = profile_res.data if profile_res and profile_res.data else {}

       
        creds_res = supabase.table("user_credentials").select("email", "role").eq("id", user_id).maybe_single().execute()
        creds_data = creds_res.data if creds_res and creds_res.data else {}

        
        return {**profile_data, **creds_data}
    except Exception as e:
        print("SERVER ERROR:", e) 
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profile: {str(e)}")

@router.delete("/profile/{user_id}")
async def delete_profile(user_id: str):
    try:
        response = supabase.table("user_profiles").delete().eq("user_id", user_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found or already deleted")
        return {"message": "Profile deleted", "data": response.data}
    except Exception as e:
        print("SERVER ERROR:", e) 
        raise HTTPException(status_code=500, detail=f"Failed to delete profile: {str(e)}")