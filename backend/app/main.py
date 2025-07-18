import logging
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import the scheduler and API routers
from app.core.scheduler import start_scheduler
from app.api.v1 import deputados, proposicoes, partidos, orgaos, eventos, votacoes
from app.infra.db.session import SessionLocal
from app.infra.camara_api import camara_api_client
from app.infra.llm_client import llm_client
from app.domain.entidades import HealthCheckResponse # Import the new model

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to be executed on startup
    logging.info("--- Application starting ---")
    start_scheduler()
    yield
    # Code to be executed on shutdown
    logging.info("--- Application shutting down ---")


app = FastAPI(
    title="Câmara Insights API",
    description="An API to collect, process, and analyze data from the Chamber of Deputies of Brazil.",
    version="0.1.0",
    lifespan=lifespan # Add the lifecycle manager
)

origins = [
    "http://localhost:3000", # The address of your React frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# Include the routers
app.include_router(deputados.router, prefix="/api/v1", tags=["Deputados"])
app.include_router(proposicoes.router, prefix="/api/v1", tags=["Proposições"])
app.include_router(partidos.router, prefix="/api/v1", tags=["Partidos"])
app.include_router(orgaos.router, prefix="/api/v1", tags=["Órgãos"])
app.include_router(eventos.router, prefix="/api/v1", tags=["Eventos"])
app.include_router(votacoes.router, prefix="/api/v1", tags=["Votações"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Câmara Insights API!"}

@app.get("/health-check", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    db_status = "ok"
    camara_api_status = "ok"
    openrouter_api_status = "ok"

    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logging.error(f"Database health check failed: {e}")
        db_status = "error"

    # Check Câmara API connectivity
    try:
        # A simple request to a lightweight endpoint
        response = await camara_api_client.get("/referencias/proposicoes/codTema")
        if not response:
            camara_api_status = "error"
    except Exception as e:
        logging.error(f"Câmara API health check failed: {e}")
        camara_api_status = "error"

    # Check OpenRouter API connectivity
    try:
        # This will try to make a request to OpenRouter, we can just check if the client is configured
        if not llm_client.api_key:
            openrouter_api_status = "not configured"
    except Exception as e:
        logging.error(f"OpenRouter API health check failed: {e}")
        openrouter_api_status = "error"


    return {
        "api_status": "ok",
        "db_status": db_status,
        "camara_api_status": camara_api_status,
        "openrouter_api_status": openrouter_api_status
    }