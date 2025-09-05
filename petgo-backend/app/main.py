from fastapi import FastAPI
from loguru import logger

app = FastAPI(title="PetGo API", version="0.1.0")

@app.get("/health")
def health():
    logger.info("Health check ok")
    return {"status": "ok"}
