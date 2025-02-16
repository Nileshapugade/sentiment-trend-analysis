from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RawTweet(Base):
    __tablename__ = "raw_tweets"

    id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(String, unique=True, nullable=False)
    text = Column(Text, nullable=False)
    sentiment = Column(String, nullable=False)  # "POSITIVE", "NEGATIVE", "NEUTRAL"
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TrendPrediction(Base):
    __tablename__ = "trend_predictions"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, nullable=False)
    predicted_trend = Column(String, nullable=False)  # "Rising", "Falling"
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
