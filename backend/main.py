from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends, Query, Path, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import os
from datetime import datetime, date
from app.db import database
from app.db.database import Base
from app import models # Assuming models.py is in backend/app/

from app.routes import (
    auth,
    other_routes,
    outfit_routes,
    search_router,
    wardrobe,
    user_profile
)
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
Base.metadata.create_all(bind=database.engine) # This creates tables if they don't exist
app = FastAPI()
security = HTTPBearer()

# Mount static files directory
# This should be done before including routers if routers depend on static paths at startup,
# though for serving files, order might not strictly matter unless complex path overlaps.
os.makedirs("static", exist_ok=True) # Ensure the base static directory exists
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.utcnow()
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Register routers
app.include_router(auth.router, prefix="/api")
app.include_router(user_profile.router, prefix="/api") 
app.include_router(outfit_routes.router, prefix="/api")
app.include_router(wardrobe.router, prefix="/api")
app.include_router(search_router.router, prefix="/api")
app.include_router(other_routes.router, prefix="/api")
# Added new user_profile router
   # Added new community router


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Run Uvicorn when executing: python main.py
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Remove in production
        workers=1,  # Adjust as needed
        log_level="info",
    )