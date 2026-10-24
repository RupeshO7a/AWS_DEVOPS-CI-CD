from contextlib import asynccontextmanager
from typing import List, Optional
 
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session
 
import models
from database import Base, SessionLocal, engine
 
APP_VERSION = "1.1.0"
 
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the app starts: create the tables if they do not exist.
    Base.metadata.create_all(bind=engine)
    yield
 
 
app = FastAPI(title="CI/CD Demo API", version=APP_VERSION, lifespan=lifespan)
 
 
def get_db():
    """Give each request a database session and close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
 
# ---------- Data shapes (what the API accepts and returns) ----------
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
 
 
class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
 
    id: int
    name: str
    description: Optional[str] = None
 
 
# ---------- Endpoints ----------
@app.get("/")
def root():
    return {
        "message": "Hello from FastAPI - deployed automatically by Jenkins!",
        "version": APP_VERSION,
    }
 
 
@app.get("/health")
def health(db: Session = Depends(get_db)):
    # Jenkins calls this after a deployment to check the app AND the database work.
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
 
 
@app.post("/items", response_model=ItemOut, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
 
 
@app.get("/items", response_model=List[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(models.Item).all()
 
 
@app.get("/items/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
 
 
@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"deleted": item_id}
