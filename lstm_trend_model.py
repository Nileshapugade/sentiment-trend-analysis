import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from models import RawTweet, TrendPrediction
from datetime import datetime

# Database setup
DATABASE_URL = "postgresql://postgres:1111@localhost:5432/sentiment_db"  # Replace with your credentials
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to train LSTM on-the-fly
def train_lstm_model():
    db = SessionLocal()
    
    # Fetch data from DB
    tweets = db.query(RawTweet).order_by(RawTweet.created_at).all()
    
    # Convert to DataFrame
    data = pd.DataFrame([{"created_at": t.created_at, "sentiment": 1 if t.sentiment == "POSITIVE" else 0} for t in tweets])

    if len(data) < 20:
        print("Not enough data to train LSTM.")
        return

    # Prepare data
    data["time"] = np.arange(len(data))
    X = np.array(data["time"]).reshape(-1, 1, 1)
    y = np.array(data["sentiment"]).reshape(-1, 1)

    # Define LSTM model
    model = Sequential([
        LSTM(50, activation='relu', input_shape=(1, 1)),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Train model
    model.fit(X, y, epochs=5, verbose=1)

    # Make a prediction for next time step
    future_trend = model.predict(np.array([[len(data)]]).reshape(1, 1, 1))[0][0]
    prediction_label = "Rising" if future_trend > 0.5 else "Falling"

    # Store in DB
    trend_entry = TrendPrediction(
        keyword="Twitter",
        predicted_trend=prediction_label,
        confidence=float(future_trend),
        created_at=datetime.utcnow()
    )
    db.add(trend_entry)
    db.commit()
    db.refresh(trend_entry)

    print(f"Predicted trend: {prediction_label} (Confidence: {future_trend:.2f})")
