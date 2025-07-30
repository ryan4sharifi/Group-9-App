from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field, constr
from enum import Enum
from passlib.hash import bcrypt 
from app.supabase_client import supabase

router = APIRouter()

class UserRole(str, Enum):
    volunteer = "volunteer"
    admin = "admin"

class UserRegister(BaseModel):
    email: EmailStr
    password: constr(min_length=6) = Field(..., description="password should have at least 6 characters")
    role: UserRole = UserRole.volunteer

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(user: UserRegister):
    try:
        existing = supabase.table("user_credentials").select("id").eq("email", user.email).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = bcrypt.hash(user.password) # Using bcrypt from passlib.hash directly

        result = supabase.table("user_credentials").insert({
            "email": user.email,
            "password": hashed_password,
            "role": user.role.value
        }).execute()

        if not result.data or "id" not in result.data[0]:
            raise HTTPException(status_code=500, detail="User could not be created")

        # After successful registration, automatically create a basic user_profile entry
        # This prevents 500 errors later if a profile isn't found for a new user trying to update
        # Ensure user_profiles.user_id is set to be unique or handle upsert logic
        user_id = result.data[0]["id"]
        try:
            # Insert with default values, especially an empty skills list as it's required
            supabase.table("user_profiles").insert({"user_id": user_id, "skills": []}).execute()
        except Exception as profile_e:
            print(f"Warning: Failed to create initial user profile for {user_id}: {profile_e}")
            # You might choose to delete the user_credentials here if profile creation is mandatory
            # For now, we'll just log and let registration proceed.

        return {
            "message": "User registered successfully",
            "id": user_id,
            "role": user.role.value
        }
    except Exception as e:
        # Check for unique constraint violation (e.g., email already exists)
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Email already registered.")
        print(f"Registration server error: {e}") # Added for better debugging
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login")
async def login(user: UserLogin):
    try:
        result = supabase.table("user_credentials").select("*").eq("email", user.email).execute()
        if not result.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        db_user = result.data[0]

        if not bcrypt.verify(user.password, db_user["password"]): # Using bcrypt from passlib.hash directly
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return {
            "message": "Login successful",
            "user_id": db_user["id"], # Renamed from 'id' to 'user_id' for consistency with frontend UserContext
            "role": db_user.get("role", "volunteer")
        }
    except Exception as e:
        print(f"Login server error: {e}") # Added for better debugging
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_by_id(user_id: str):
    try:
        result = supabase.table("user_credentials").select("email", "role").eq("id", user_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="User not found")

        return result.data[0]
    except Exception as e:
        print(f"Get user by ID server error: {e}") # Added for better debugging
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user: {str(e)}")

# --- NEW: Delete Account Endpoint ---
@router.delete("/delete_account/{user_id}")
async def delete_user_account(user_id: str):
    try:
        # Perform deletions in order of foreign key dependencies (children first)
        # Assuming ON DELETE NO ACTION or RESTRICT on your foreign keys

        # 1. Delete volunteer_history records associated with the user
        # (This is often a child table that references user_credentials or events)
        delete_history_res = supabase.table("volunteer_history").delete().eq("user_id", user_id).execute()
        print(f"Deleted {len(delete_history_res.data)} volunteer history entries for user {user_id}")

        # 2. Delete notifications associated with the user
        delete_notifications_res = supabase.table("notifications").delete().eq("user_id", user_id).execute()
        print(f"Deleted {len(delete_notifications_res.data)} notifications for user {user_id}")

        # 3. Delete user_profiles record (which references user_credentials)
        delete_profile_res = supabase.table("user_profiles").delete().eq("user_id", user_id).execute()
        if not delete_profile_res.data:
            print(f"No user profile found for {user_id} during deletion, proceeding with credentials.")
        else:
            print(f"Deleted user profile for user {user_id}")

        # 4. Finally, delete the main user_credentials record
        delete_credentials_res = supabase.table("user_credentials").delete().eq("id", user_id).execute()
        if not delete_credentials_res.data:
            # This indicates the user_credentials might not have existed (e.g., already deleted)
            raise HTTPException(status_code=404, detail="User account not found or already deleted.")
        print(f"Deleted user credentials for user {user_id}")

        return {"message": "Account and all associated data deleted successfully."}
    except HTTPException as he:
        # Re-raise HTTP exceptions (like 404)
        raise he
    except Exception as e:
        # Catch any other unexpected errors during the deletion process
        print(f"SERVER ERROR during account deletion for {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete account: {str(e)}")