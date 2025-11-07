from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .settings import settings
import os


class Base(DeclarativeBase):
    pass


os.makedirs(os.path.dirname(settings.sqlite_path), exist_ok=True)
DATABASE_URL = f"sqlite:///{settings.sqlite_path}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

