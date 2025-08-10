from backend.api.v1.endpoints import router as api_v1_router
from backend.api.v2.endpoints import router as api_v2_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="AbSequenceAlign API",
    description="Antibody Sequence Alignment and Analysis Tool",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register v1 API router
app.include_router(api_v1_router, prefix="/api/v1")

# Register v2 API router
app.include_router(api_v2_router, prefix="/api/v2")


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
