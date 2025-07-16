from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    auth, profile, events, history, match, notifications, report, contact
)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Volunteer Management Backend is running."}

# Register API route modules with appropriate prefixes
app.include_router(auth.router, prefix="/auth")
app.include_router(profile.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(match.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(report.router, prefix="/api")
app.include_router(contact.router, prefix="/api/contact")