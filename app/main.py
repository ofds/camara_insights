# app/main.py
from fastapi import FastAPI

app = FastAPI(
    title="Câmara Insights API",
    description="An API to collect, process, and analyze data from the Brazilian Chamber of Deputies.",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Câmara Insights!"}

@app.get("/health-check")
def health_check():
    return {"status": "ok"}