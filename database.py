from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import RawTweet  # Import the RawTweet model

# Database URL (replace with your actual database URL)
DATABASE_URL = "postgresql://postgres:1111@db:5432/sentiment_db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_tweets_by_column(db: Session, column_name: str, value: str):
    """
    Fetch tweets from the database filtered by a specific column and value.
    
    Args:
        db (Session): SQLAlchemy database session.
        column_name (str): Name of the column to filter by.
        value (str): Value to filter the column by.
    
    Returns:
        List[RawTweet]: List of RawTweet objects matching the filter.
    """
    # Dynamically access the column using getattr
    column = getattr(RawTweet, column_name, None)
    if column is None:
        raise ValueError(f"Column '{column_name}' does not exist in RawTweet model.")
    
    # Perform the query
    return db.query(RawTweet).filter(column == value).all()
