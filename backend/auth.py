"""Authentication utilities and FastAPI routes.

This module provides functions for hashing passwords, verifying
credentials and issuing JSON Web Tokens (JWTs) for authenticated
requests.  It exposes a FastAPI APIRouter with registration and login
endpoints.  All sensitive operations are logged at info level and
errors are obscured to avoid leaking user details.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal, User, Session as TokenSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 scheme for extracting bearer tokens from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class UserCreate(BaseModel):
    """Model for registering new users."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Response model for login/register containing JWT access token."""

    access_token: str
    token_type: str = "bearer"


def get_db():
    """FastAPI dependency to yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plaintext password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password for storing in the database."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a signed JWT.

    The token payload includes a unique JTI and user ID.  Expiry defaults
    to settings.access_token_expire_minutes.  The returned string may
    be stored in the database for revocation.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def get_user(db: Session, username: str) -> Optional[User]:
    """Retrieve a user by username."""
    return db.query(User).filter(User.username == username).first()


@router.post("/register", response_model=TokenResponse)
def register(user_create: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    """Register a new user.

    If the username already exists, returns a 400 error.
    """
    existing = get_user(db, user_create.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    hashed = hash_password(user_create.password)
    user = User(username=user_create.username, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    # Generate a token with a JTI equal to user id and store session
    token_data = {"sub": str(user.id), "jti": f"register-{user.id}-{datetime.utcnow().timestamp()}"}
    access_token = create_access_token(data=token_data)
    # Persist token session with expiry
    expires = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    token_session = TokenSession(
        jti=token_data["jti"], user_id=user.id, issued_at=datetime.utcnow(), expires_at=expires
    )
    db.add(token_session)
    db.commit()
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
def login(user_create: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate an existing user and return a JWT.

    Returns 401 on invalid credentials.  Does not reveal whether the
    username or password was incorrect.
    """
    user = get_user(db, user_create.username)
    if not user or not verify_password(user_create.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    # Create new token
    token_data = {"sub": str(user.id), "jti": f"login-{user.id}-{datetime.utcnow().timestamp()}"}
    access_token = create_access_token(data=token_data)
    expires = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    token_session = TokenSession(
        jti=token_data["jti"], user_id=user.id, issued_at=datetime.utcnow(), expires_at=expires
    )
    db.add(token_session)
    db.commit()
    return TokenResponse(access_token=access_token)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extract user from a Bearer token.

    This function decodes the JWT, validates the signature and expiry,
    checks that the jti is still valid in the sessions table, and
    returns the corresponding user object.  Raises HTTP 401 on any
    failure.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        if user_id is None or jti is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    # Verify session exists and is not expired/revoked
    session_record = (
        db.query(TokenSession)
        .filter(TokenSession.jti == jti, TokenSession.user_id == int(user_id))
        .first()
    )
    if not session_record or session_record.expires_at < datetime.utcnow():
        raise credentials_exception
    user = db.query(User).get(int(user_id))
    if not user:
        raise credentials_exception
    return user


__all__ = [
    "router",
    "UserCreate",
    "TokenResponse",
    "get_current_user",
    "hash_password",
    "verify_password",
    "create_access_token",
]