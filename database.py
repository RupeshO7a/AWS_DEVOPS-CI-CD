import os
 
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
 
# The address of the PostgreSQL database.
# In Docker we pass it in with an environment variable called DATABASE_URL.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://appuser:localpassword@localhost:5432/appdb",
)
 
# The "engine" is the connection to the database.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
 
# Every request to the API gets its own short "session" with the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
# All our table classes inherit from this Base.
Base = declarative_base()
