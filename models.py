from database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, func, UniqueConstraint, ARRAY


class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, index=True)
    url = Column(String, index=True)
    title = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    summary = Column(Text)
    links = Column(ARRAY(String))


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, index=True)
    status = Column(String)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=None,
                        onupdate=func.now(), nullable=True)
