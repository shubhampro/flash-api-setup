from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.api.app import api_app
from apps.admin.app import admin_app

# Create main FastAPI app
app = FastAPI(
    title="FastAPI Multi-App Project",
    description="A FastAPI project with multiple apps and shared components",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the API apps
app.mount("/api", api_app)
app.mount("/admin", admin_app)

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Multi-App Project"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
