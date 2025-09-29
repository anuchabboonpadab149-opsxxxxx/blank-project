from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db, User, Base, engine
from ..schemas import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse
from ..utils import hash_password, verify_password, create_access_token

Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(email=str(payload.email), password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token, _ = create_access_token(user.id)
    return RegisterResponse(user_id=user.id, token=token)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == str(payload.email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token, expires_in = create_access_token(user.id)
    return LoginResponse(user_id=user.id, token=token, expires_in=expires_in)


@router.post("/logout")
def logout():
    return {"message": "success"}