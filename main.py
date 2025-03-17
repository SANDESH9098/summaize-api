from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routers import transcript, summarize
from fastapi.responses import JSONResponse

app = FastAPI(
    title="YouTube Summarizer API",
    description="API for fetching and summarizing YouTube video transcripts",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transcript.router, tags=["Transcript"])
app.include_router(summarize.router, tags=["Summarize"])

@app.get("/")
async def root():
    return {"message": "YouTube Summarizer API is running"}

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": f"An unexpected error occurred: {str(exc)}"}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)