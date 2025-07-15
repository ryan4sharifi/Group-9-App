# Authentication Routes using Supabase as backend
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field, constr
from enum import Enum
from passlib.hash import bcrypt
from app.supabase_client import supabase

router = APIRouter()

# Enum to define user roles
class UserRole(str, Enum):
    volunteer = "volunteer"
    admin = "admin"

# Model for user registration input validation
class UserRegister(BaseModel):
    email: EmailStr
    password: constr(min_length=6) = Field(..., description="password should have at least 6 characters")
    role: UserRole = UserRole.volunteer

# Model for user login input
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Register route - handles user signup
@router.post("/register")
async def register(user: UserRegister):
    try:
        # Check if user already exists in Supabase
        existing = supabase.table("user_credentials").select("id").eq("email", user.email).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash the password using bcrypt
        hashed_password = bcrypt.hash(user.password)

        # Insert new user into Supabase
        result = supabase.table("user_credentials").insert({
            "email": user.email,
            "password": hashed_password,
            "role": user.role.value
        }).execute()

        # Handle Supabase insert failure
        if not result.data or "id" not in result.data[0]:
            raise HTTPException(status_code=500, detail="User could not be created")

        return {
            "message": "User registered successfully",
            "id": result.data[0]["id"],
            "role": user.role.value
        }
    except Exception as e:
        # Generic error handling
        raise HTTPException(status_code=500, detail=str(e))

# Login route - verifies credentials and returns user ID and role
@router.post("/login")
async def login(user: UserLogin):
    # Get user by email from Supabase
    result = supabase.table("user_credentials").select("*").eq("email", user.email).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    db_user = result.data[0]

    # Verify hashed password
    if not bcrypt.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user_id": db_user["id"],
        "role": db_user.get("role", "volunteer")
    }

# Fetch user by ID for frontend session persistence
@router.get("/user/{user_id}")
async def get_user_by_id(user_id: str):
    result = supabase.table("user_credentials").select("email", "role").eq("id", user_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")

    return result.data[0]