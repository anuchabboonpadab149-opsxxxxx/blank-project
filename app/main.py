from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine, seed_initial_data
from .routers import auth as auth_router
from .routers import user as user_router
from .routers import payment as payment_router
from .routers import fortune as fortune_router
from .routers import internal as internal_router

Base.metadata.create_all(bind=engine)
seed_initial_data()

app = FastAPI(title="Fortune API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(user_router.router, prefix="/user", tags=["User"])
app.include_router(payment_router.router, tags=["Payment"])
app.include_router(fortune_router.router, prefix="/fortune", tags=["Fortune"])
app.include_router(internal_router.router, prefix="/internal", tags=["Internal"])


@app.get("/")
def root():
    return {"message": "Fortune API is running"}