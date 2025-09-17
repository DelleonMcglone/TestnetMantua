"""Database configuration and models for Mantua.AI.

This module sets up a SQLAlchemy engine and session for PostgreSQL and
defines ORM models for users, sessions and transactions.  It
encapsulates database access so that the rest of the application can
import a session factory without worrying about engine creation.

The database URL is read from the environment via settings.database_url.
If you change the database backend or credentials, update your
DATABASE_URL environment variable accordingly (e.g.
postgresql://username:password@localhost:5432/mantua).
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine

from .config import settings

# Base class for ORM models
Base = declarative_base()

# Create engine and session factory
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class User(Base):
    """User model representing registered accounts."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sessions = relationship("Session", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class Session(Base):
    """Session model storing issued JWT tokens (JTI) with expiry times.

    Session records allow us to revoke or blacklist specific tokens by JTI.
    """

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(128), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    user = relationship("User", back_populates="sessions")


class Transaction(Base):
    """On‑chain transaction requested by a user.

    Stores a JSON‑encoded representation of the original intent along with
    the resulting transaction hash and status.  Amounts are stored as
    numeric to facilitate per‑user daily limits.
    """

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tx_hash = Column(String(66), nullable=True)
    status = Column(String(32), default="pending")
    intent_json = Column(String, nullable=False)
    amount_usd = Column(Numeric(38, 18), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")


def init_db() -> None:
    """Create all tables.

    Should be called at application startup once.  It is a no‑op if the
    tables already exist.
    """
    import logging

    Base.metadata.create_all(bind=engine)
    logging.getLogger(__name__).info("Database tables created")


__all__ = [
    "SessionLocal",
    "Base",
    "User",
    "Session",
    "Transaction",
    "init_db",
]