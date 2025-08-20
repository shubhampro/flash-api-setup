from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.admin.routers import users

# Create Admin FastAPI app
admin_app = FastAPI(
    title="Admin",
    description="Administrative interface for managing the system",
    version="1.0.0"
)

# Add CORS middleware
admin_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include admin routers
admin_app.include_router(users.router)

@admin_app.get("/")
async def admin_root():
    return {"message": "Admin Panel", "endpoints": ["/users"]}

@admin_app.get("/health")
async def admin_health():
    return {"status": "healthy", "service": "admin"}
