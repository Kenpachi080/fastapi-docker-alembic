from database.base import Base
from sqlalchemy import Column, String, Integer


class Todo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(128), unique=True)
