from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Enum, Boolean
from datetime import datetime
import enum

from app.core.database import Base

class ModerationDecision(str, enum.Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MANUAL_REVIEW = "MANUAL_REVIEW"

class ContentFlagStatus(str, enum.Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    CLOSED = "CLOSED"

class ModerationEvent(Base):
    __tablename__ = "moderation_events"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_id = Column(BigInteger, ForeignKey("reports.id"), nullable=False)
    provider = Column(String(40))     # NudeNet, Vision, etc.
    score = Column(String(40))        # texto breve com scores
    decision = Column(Enum(ModerationDecision), nullable=False)
    reviewer_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class ContentFlag(Base):
    __tablename__ = "content_flags"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_id = Column(BigInteger, ForeignKey("reports.id"), nullable=False)
    reporter_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    reason = Column(String(120), nullable=False)
    status = Column(Enum(ContentFlagStatus), default=ContentFlagStatus.OPEN, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
