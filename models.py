from sqlalchemy import Column, Integer, String
 
from database import Base
 
 
class Item(Base):
    """This class becomes a table called 'items' in PostgreSQL."""
 
    __tablename__ = "items"
 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
