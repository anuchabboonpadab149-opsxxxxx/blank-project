from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import seed_packages
from .routers import router

seed_packages()

app = FastAPI(title="Payment Service", version="1.0.0")
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
    return {"message": "Payment service running"}