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

        hashed_password = bcrypt.hash(user.password)

        result = supabase.table("user_credentials").insert({
            "email": user.email,
            "password": hashed_password,
            "role": user.role.value
        }).execute()

        if not result.data or "id" not in result.data[0]:
            raise HTTPException(status_code=500, detail="User could not be created")

        return {
            "message": "User registered successfully",
            "id": result.data[0]["id"],
            "role": user.role.value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(user: UserLogin):
    result = supabase.table("user_credentials").select("*").eq("email", user.email).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    db_user = result.data[0]

    if not bcrypt.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user_id": db_user["id"],
        "role": db_user.get("role", "volunteer")
    }

@router.get("/user/{user_id}")
async def get_user_by_id(user_id: str):
    result = supabase.table("user_credentials").select("email", "role").eq("id", user_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")

    return result.data[0]