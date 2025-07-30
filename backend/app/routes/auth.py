# Authentication Routes using Supabase as backend
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, constr
from enum import Enum
<<<<<<< HEAD
from passlib.hash import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
=======
from passlib.hash import bcrypt 
>>>>>>> c7755f350084cea77c4aa9a597b23aaaaf0a615a
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

<<<<<<< HEAD
        # Hash the password using bcrypt
        hashed_password = bcrypt.hash(user.password)
=======
        hashed_password = bcrypt.hash(user.password) # Using bcrypt from passlib.hash directly
>>>>>>> c7755f350084cea77c4aa9a597b23aaaaf0a615a

        # Insert new user into Supabase
        result = supabase.table("user_credentials").insert({
            "email": user.email,
            "password": hashed_password,
            "role": user.role.value
        }).execute()

        # Handle Supabase insert failure - check both data and structure
        if not result.data or not isinstance(result.data, list) or len(result.data) == 0:
            raise HTTPException(status_code=500, detail="User could not be created")
        
        # Get the new user record
        new_user = result.data[0]
        if "id" not in new_user:
            raise HTTPException(status_code=500, detail="User ID not returned")

        user_id = new_user["id"]
        
        # Create JWT token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id, "role": user.role.value},
            expires_delta=access_token_expires
        )

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
<<<<<<< HEAD
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
=======
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
>>>>>>> c7755f350084cea77c4aa9a597b23aaaaf0a615a
