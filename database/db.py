from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import SYNC_DATABASE_URI

SQLALCHEMY_DATABASE_URL = SYNC_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
