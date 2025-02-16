from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from models import RawTweet  # Import the RawTweet model
from database import get_tweets_by_column  # Import the database function
from datetime import datetime
import tweepy
import re
import emoji
from nltk.corpus import stopwords
from transformers import pipeline

# FastAPI app setup
app = FastAPI()

# Database setup
DATABASE_URL = "postgresql://postgres:1111@localhost:5432/sentiment_db"  # Replace with your credentials
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Load sentiment-analysis model from Hugging Face
sentiment_analyzer = pipeline("sentiment-analysis")

# Twitter API authentication
auth = tweepy.OAuthHandler("d3HtA6llWoAg4u2eUxiaMzd6K", "voREiAe7Q0CwrmCFDe7aNZLyPGEFhaKt3vkaJ97av7QlqW922f")
auth.set_access_token("1887660112514260992-EN5YOpKUlh0Bbu21eYfXGv6XZkfPe1", "Yjn3w9AYvzaigua0kkk5XkSKrVswb2r86SzbUNAoty0Iw")
api = tweepy.API(auth, wait_on_rate_limit=True)

# Preprocessing function
def preprocess_text(text: str):
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)  # Remove URLs
    text = re.sub(r"(@\w+|#\w+)", "", text)  # Remove mentions & hashtags
    text = emoji.demojize(text, delimiters=("", ""))  # Convert emojis to text
    stop_words = set(stopwords.words('english'))
    text = ' '.join([word for word in text.split() if word.lower() not in stop_words])  # Remove stopwords
    return text.strip()

# Function to analyze tweets in the background
def fetch_and_analyze_tweets(query: str, db: Session):
    tweets = api.search_tweets(q=query, lang="en", count=10)
    for tweet in tweets:
        processed_text = preprocess_text(tweet.text)
        sentiment_result = sentiment_analyzer(processed_text)
        sentiment = sentiment_result[0]['label']
        confidence = sentiment_result[0]['score']

        # Store in DB
        tweet_entry = RawTweet(
            tweet_id=tweet.id_str,
            text=tweet.text,
            sentiment=sentiment,
            confidence=confidence,
            created_at=datetime.utcnow()
        )
        db.add(tweet_entry)
        db.commit()

# FastAPI route to trigger live sentiment analysis
@app.post("/analyze_twitter_data/")
async def analyze_twitter_data(query: str, background_tasks: BackgroundTasks, db: Session = Depends(SessionLocal)):
    background_tasks.add_task(fetch_and_analyze_tweets, query, db)
    return {"message": "Tweets are being analyzed in the background"}

# FastAPI route to fetch filtered tweets
@app.get("/filtered_tweets/")
async def get_filtered_tweets(column_name: str, value: str, db: Session = Depends(SessionLocal)):
    tweets = get_tweets_by_column(db, column_name, value)
    return {"tweets": [{"text": tweet.text, "sentiment": tweet.sentiment} for tweet in tweets]}
