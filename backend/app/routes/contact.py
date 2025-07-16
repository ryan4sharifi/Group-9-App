#(no DB implementation yet)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, constr

router = APIRouter()

# Pydantic schema for contact form validation
class ContactMessage(BaseModel):
    name: constr(min_length=1, max_length=100)
    email: EmailStr
    message: constr(min_length=1, max_length=1000)

# Simulate contact form submission (mock)
@router.post("/contact")
async def submit_contact_form(contact: ContactMessage):
    try:
        # Here you would typically save the contact message to a database or send an email
        print(f"New contact message received: {contact.dict()}")

        # Normally you'd send an email or save to DB — skip for now
        return {"message": "Your message has been received. Thank you for reaching out!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
