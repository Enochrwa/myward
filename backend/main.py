from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, outfits, recommendations, wardrobe, upload

app = FastAPI(
    title="Digital Wardrobe API",
    description="The backend for the Digital Wardrobe application.",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(outfits.router, prefix="/outfits", tags=["outfits"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
app.include_router(wardrobe.router, prefix="/wardrobe", tags=["wardrobe"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Digital Wardrobe API"}