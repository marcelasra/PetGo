from sqlalchemy import Column, BigInteger, Integer, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base

class TrustSignal(Base):
    __tablename__ = "trust_signals"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
