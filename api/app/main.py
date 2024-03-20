from fastapi import FastAPI
from routers import database_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:8000"],
    allow_credentials=True,
)

app.include_router(database_router.router, prefix="/api/v1")
