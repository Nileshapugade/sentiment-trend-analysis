from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import time
import tweepy
from transformers import pipeline
import re
import emoji
from nltk.corpus import stopwords

# FastAPI app setup
app = FastAPI()

# Database setup
DATABASE_URL = "postgresql://postgres:1111@localhost:5432/sentiment_db"  # Replace with your credentials
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Preprocessing function
def preprocess_text(text: str):
    # Remove URLs, mentions, hashtags, emojis, stopwords, etc.
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"(@\w+|#\w+)", "", text)
    text = emoji.demojize(text, delimiters=("", ""))
    stop_words = set(stopwords.words('english'))
    text = ' '.join([word for word in text.split() if word.lower() not in stop_words])
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Database model for sentiment analysis
class SentimentAnalysis(Base):
    __tablename__ = 'sentiment_analysis'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    sentiment = Column(String)
    confidence = Column(Float, nullable=False)
    created_at = Column(Integer, nullable=False)  # Unix timestamp as integer

# Pydantic models for request and response
class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    sentiment: str
    confidence: float
    created_at: int

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Load pre-trained sentiment-analysis pipeline from Hugging Face
sentiment_analyzer = pipeline("sentiment-analysis")

# Updated analyze_sentiment function using Hugging Face model
def analyze_sentiment(text: str):
    result = sentiment_analyzer(text)
    sentiment = result[0]['label']
    confidence = result[0]['score']
    return sentiment, confidence

# Function to fetch tweets and analyze sentiment
def fetch_and_analyze_tweets(query: str, db: Session):
    # Twitter API setup (replace with actual keys)
    auth = tweepy.OAuthHandler("d3HtA6llWoAg4u2eUxiaMzd6K", "voREiAe7Q0CwrmCFDe7aNZLyPGEFhaKt3vkaJ97av7QlqW922f")
    auth.set_access_token("1887660112514260992-EN5YOpKUlh0Bbu21eYfXGv6XZkfPe1", "Yjn3w9AYvzaigua0kkk5XkSKrVswb2r86SzbUNAoty0Iw")
    api = tweepy.API(auth)
    
    try:
        # Fetch tweets
        tweets = api.search_tweets(q=query, lang="en", count=10)  # Modify as needed
        for tweet in tweets:
            processed_text = preprocess_text(tweet.text)  # Preprocess tweet text
            sentiment, confidence = analyze_sentiment(processed_text)  # Analyze sentiment
            
            # Store in database
            sentiment_analysis = SentimentAnalysis(
                text=tweet.text,
                sentiment=sentiment,
                confidence=confidence,
                created_at=int(time.time())  # Store the current time as Unix timestamp
            )
            db.add(sentiment_analysis)
            db.commit()
            db.refresh(sentiment_analysis)
    except tweepy.TweepError as e:
        print(f"Error fetching tweets: {e}")

# FastAPI route for analyzing sentiment on specific tweets
@app.post("/analyze_twitter_data/")
async def analyze_twitter_data(request: SentimentRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Add the task to background
    background_tasks.add_task(fetch_and_analyze_tweets, request.text, db)
    return {"message": "Tweets are being analyzed in the background"}

# FastAPI route for sentiment analysis
@app.post("/analyze_sentiment/", response_model=SentimentResponse)
def analyze_sentiment_route(request: SentimentRequest, db: Session = Depends(get_db)):
    try:
        # Preprocess text and analyze sentiment
        sentiment, confidence = analyze_sentiment(request.text)

        sentiment_analysis = SentimentAnalysis(
            text=request.text,
            sentiment=sentiment,
            confidence=confidence,
            created_at=int(time.time())  # Store the current time as Unix timestamp
        )

        db.add(sentiment_analysis)
        db.commit()
        db.refresh(sentiment_analysis)

        return SentimentResponse(
            sentiment=sentiment,
            confidence=confidence,
            created_at=sentiment_analysis.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
