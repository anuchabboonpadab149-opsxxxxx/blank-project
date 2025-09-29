import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth as auth_router
from .routers import user as user_router
from .routers import packages as packages_router
from .routers import payment as payment_router
from .routers import fortune as fortune_router
from .routers import admin as admin_router

app = FastAPI(title="Fortune Gateway", version="1.0.0")

allow_origins = os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(user_router.router, prefix="/user", tags=["User"])
app.include_router(packages_router.router, tags=["Packages"])
app.include_router(payment_router.router, tags=["Payment"])
app.include_router(fortune_router.router, prefix="/fortune", tags=["Fortune"])
app.include_router(admin_router.router, prefix="/admin", tags=["Admin"])


@app.get("/")
def root():
    return {"message": "Gateway running"}