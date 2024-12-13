from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///reviews.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, nullable=False)  
    customer_id = Column(Integer, nullable=False) 
    rating = Column(Integer, nullable=False) 
    review = Column(Text, nullable=True) 

Base.metadata.create_all(bind=engine)
