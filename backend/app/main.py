from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.routes import (
    auth, profile, events, history, match, notifications, report, contact
)
from app.supabase_client import supabase, check_database_health
from app.routes.auth import verify_token
import json
import asyncio
from typing import Dict, List

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                print(f"Error sending message to {user_id}: {e}")
                self.disconnect(user_id)
    
    async def broadcast(self, message: str):
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting to {user_id}: {e}")
                self.disconnect(user_id)

manager = ConnectionManager()

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Volunteer Management System...")
    
    # Check database health
    health = await check_database_health()
    print(f"📊 Database status: {health}")
    
    # Setup real-time subscriptions if available
    if hasattr(supabase, 'subscribe_to_table'):
        def notification_handler(payload):
            # Handle real-time notification updates
            asyncio.create_task(handle_notification_update(payload))
        
        supabase.subscribe_to_table("notifications", notification_handler, "INSERT")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Volunteer Management System...")
    if hasattr(supabase, 'close_all_subscriptions'):
        supabase.close_all_subscriptions()

async def handle_notification_update(payload):
    """Handle real-time notification updates"""
    try:
        new_record = payload.get("new", {})
        user_id = new_record.get("user_id")
        
        if user_id:
            message = json.dumps({
                "type": "notification",
                "data": new_record
            })
            await manager.send_personal_message(message, user_id)
    except Exception as e:
        print(f"Error handling notification update: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="Volunteer Management System",
    description="A comprehensive volunteer management system with real-time notifications",
    version="2.0.0",
    lifespan=lifespan
)

# Security middleware - temporarily disabled for testing
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["localhost", "127.0.0.1", "*.volunteerapp.com"]
# )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
<<<<<<< HEAD
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-frontend-domain.com"
    ],
=======
    allow_origins=["http://localhost:3000"],  
>>>>>>> c7755f350084cea77c4aa9a597b23aaaaf0a615a
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Volunteer Management System API v2.0",
        "status": "operational",
        "features": [
            "JWT Authentication",
            "Real-time Notifications",
            "Advanced Matching Algorithm",
            "Email Integration",
            "Comprehensive Reports"
        ]
    }

<<<<<<< HEAD
# Health check endpoint
@app.get("/health")
async def health_check():
    db_health = await check_database_health()
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "database": db_health,
        "websocket_connections": len(manager.active_connections)
    }

# WebSocket endpoint for real-time notifications
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
            message = json.loads(data)
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)

# API route registration
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/api", tags=["Profile"])
app.include_router(events.router, prefix="/api", tags=["Events"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(match.router, prefix="/api", tags=["Matching"])
app.include_router(notifications.router, prefix="/api", tags=["Notifications"])
app.include_router(report.router, prefix="/api", tags=["Reports"])
app.include_router(contact.router, prefix="/api", tags=["Contact"])

# Real-time notification endpoint
@app.post("/api/notify-realtime")
async def notify_realtime(user_id: str, message: str, current_user: dict = Depends(verify_token)):
    """Send real-time notification via WebSocket"""
    if current_user["role"] != "admin":
        return {"error": "Admin access required"}
    
    notification_data = {
        "type": "notification",
        "message": message,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    await manager.send_personal_message(json.dumps(notification_data), user_id)
    return {"message": "Real-time notification sent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
=======
# 🔌 Register API route modules with appropriate prefixes
app.include_router(auth.router, prefix="/auth")
app.include_router(profile.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(match.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(report.router, prefix="/api")
>>>>>>> c7755f350084cea77c4aa9a597b23aaaaf0a615a
