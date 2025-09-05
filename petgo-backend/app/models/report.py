from sqlalchemy import Column, BigInteger, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from geoalchemy2 import Geography, Geometry
from app.core.database import Base

class ReportStatus(str, enum.Enum):
    REPORTADO = "REPORTADO"
    EM_ATENDIMENTO = "EM_ATENDIMENTO"
    RESOLVIDO = "RESOLVIDO"
    UNDER_REVIEW = "UNDER_REVIEW"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"

class Visibility(str, enum.Enum):
    PUBLIC = "PUBLIC"     # exibe approx_geom
    FOGGED = "FOGGED"     # deslocamento/ruído adicional
    ONG_ONLY = "ONG_ONLY" # exato só para ONG verificada

class Report(Base):
    __tablename__ = "reports"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.UNDER_REVIEW)
    visibility_level = Column(Enum(Visibility), nullable=False, default=Visibility.PUBLIC)

    # coordenada exata (geography para consultas por raio precisas)
    geom = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)
    # coordenada aproximada (geometry para visual)
    approx_geom = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)

    address_text = Column(String(200))
    description = Column(String(500))
    animal_type = Column(String(20), default="DESCONHECIDO")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    author = relationship("User", back_populates="reports")
    photos = relationship("ReportPhoto", back_populates="report", cascade="all, delete-orphan")

class ReportPhoto(Base):
    __tablename__ = "report_photos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_id = Column(BigInteger, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    report = relationship("Report", back_populates="photos")
