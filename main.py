from fastapi import FastAPI
from app.api.v1.endpoints import router as v1_router
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="Fare Calculation API",
    description="API for calculating fares based on routes",
    version="1.0.0",
)

# Allow CORS for frontend running on port 8080
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Allow frontend's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routes
app.include_router(v1_router, prefix="/api/v1")

# Entry point for running the app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)