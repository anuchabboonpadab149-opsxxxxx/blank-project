from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import seed_sources_and_content
from .routers import router

seed_sources_and_content()

app = FastAPI(title="Fortune Service", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Fortune service running"}