from sqlalchemy import Column, BigInteger, String, Boolean, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base

class Role(str, enum.Enum):
    USER = "USER"
    ONG = "ONG"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.USER)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    reports = relationship("Report", back_populates="author")

class NGO(Base):
    __tablename__ = "ngos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    name = Column(String(160), nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    radius_km = Column(String(10), default="3.0")  # simples; pode ser NUMERIC se preferir
    phone = Column(String(40))
    description = Column(String)

    user = relationship("User")
