from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# IMPORTANTE: como rodaremos o backend dentro do Docker, use host = db (nome do serviço no compose)
DATABASE_URL = "postgresql+psycopg2://petgo:petgo@db:5432/petgo"

engine = create_engine(DATABASE_URL, future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()
