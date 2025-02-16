from sqlalchemy.orm import Session
from models import RawTweet  # Import the RawTweet model

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
