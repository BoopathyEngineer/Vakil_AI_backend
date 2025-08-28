from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,Integer,String

Base = declarative_base()

class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    roles = Column(String, nullable=False)