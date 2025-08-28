from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class EmailId(Base):
    __tablename__ = 'email_verify'
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String, unique=True, nullable=False)
    otp = Column(Integer, nullable=True)
    otp_time = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)  
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  
    
 
