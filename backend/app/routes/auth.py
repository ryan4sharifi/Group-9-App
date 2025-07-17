# Authentication Routes using Supabase as backend
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, constr
from enum import Enum
from passlib.hash import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.supabase_client import supabase
import os

router = APIRouter()
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

# Model for token response
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    role: str

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"user_id": user_id, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Enhanced validation function
def validate_user_data(user_data: dict) -> dict:
    """Validate user registration data"""
    errors = {}
    
    # Email validation
    if not user_data.get("email"):
        errors["email"] = "Email is required"
    elif len(user_data["email"]) > 100:
        errors["email"] = "Email cannot exceed 100 characters"
    
    # Password validation
    if not user_data.get("password"):
        errors["password"] = "Password is required"
    elif len(user_data["password"]) < 6:
        errors["password"] = "Password must be at least 6 characters"
    
    # Role validation
    if user_data.get("role") not in ["volunteer", "admin"]:
        errors["role"] = "Role must be 'volunteer' or 'admin'"
    
    return errors

# Register route - handles user signup
@router.post("/register", response_model=Token)
async def register(user: UserRegister):
    try:
        # Validate user data
        validation_errors = validate_user_data(user.dict())
        if validation_errors:
            raise HTTPException(status_code=400, detail=validation_errors)
        
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

        user_id = result.data[0]["id"]
        
        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id, "role": user.role.value},
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id,
            "role": user.role.value
        }
    except Exception as e:
        # Generic error handling
        raise HTTPException(status_code=500, detail=str(e))

# Login route - verifies credentials and returns user ID and role
@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    try:
        # Get user by email from Supabase
        result = supabase.table("user_credentials").select("*").eq("email", user.email).execute()
        if not result.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        db_user = result.data[0]

        # Verify hashed password
        if not bcrypt.verify(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user["id"], "role": db_user.get("role", "volunteer")},
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": db_user["id"],
            "role": db_user.get("role", "volunteer")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fetch user by ID for frontend session persistence
@router.get("/user/{user_id}")
async def get_user_by_id(user_id: str, current_user: dict = Depends(verify_token)):
    """Get user by ID - protected route"""
    if current_user["user_id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this user")
    
    result = supabase.table("user_credentials").select("email", "role").eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return result.data[0]

@router.post("/verify-token")
async def verify_token_endpoint(current_user: dict = Depends(verify_token)):
    """Verify token validity"""
    return {"valid": True, "user_id": current_user["user_id"], "role": current_user["role"]}