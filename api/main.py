from fastapi import FastAPI
from routes import bigquery_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:8000"],
    allow_credentials=True,
)

app.include_router(bigquery_router.router, prefix="/api/v1")
# testing pipeline