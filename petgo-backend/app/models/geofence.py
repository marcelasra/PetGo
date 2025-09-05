from sqlalchemy import Column, BigInteger, String
from geoalchemy2 import Geometry
from app.core.database import Base

class GeofenceZone(Base):
    __tablename__ = "geofence_zones"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    rule = Column(String(40), nullable=False, default="ONG_ONLY")  # ex.: ONG_ONLY / FOGGED
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326), nullable=False)
