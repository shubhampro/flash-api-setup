from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.v1.routers import users, auth
from apps.api.v2.routers import users as users_v2

# Create API FastAPI app
api_app = FastAPI(
    title="API",
    description="Main API application with v1 and v2 endpoints",
    version="1.0.0"
)

# Add CORS middleware
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 routers
api_app.include_router(users.router, prefix="/v1")
api_app.include_router(auth.router, prefix="/v1")

# Include v2 routers
api_app.include_router(users_v2.router, prefix="/v2")

@api_app.get("/")
async def api_root():
    return {"message": "API Root", "versions": ["v1", "v2"]}

@api_app.get("/v1")
async def v1_root():
    return {"message": "API v1", "endpoints": ["/users", "/auth"]}

@api_app.get("/v2")
async def v2_root():
    return {"message": "API v2", "endpoints": ["/users"]}
