from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import events, questionnaires, interviews, reports

app = FastAPI(
    title="Event Information Platform API",
    description="Local POC API for Event Questionnaire Generation and Interviews",
    version="0.1.0"
)

# Configure CORS for local Lovable frontend POC integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open to all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "environment": "local_poc"}


# Register Domain Routers
app.include_router(events.router, prefix="/api/v1/events", tags=["Events"])
app.include_router(questionnaires.router, prefix="/api/v1/questionnaires", tags=["Questionnaires"])
app.include_router(interviews.router, prefix="/api/v1/interviews", tags=["Interviews"])
app.include_router(reports.router, prefix="/api/v1")
