from fastapi import FastAPI
from app.api.v1.endpoints import router as v1_router

# Initialize FastAPI app
app = FastAPI(
    title="Fare Calculation API",
    description="API for calculating fares based on routes",
    version="1.0.0",
)

# Include routes
app.include_router(v1_router, prefix="/api/v1")

# Entry point for running the app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)