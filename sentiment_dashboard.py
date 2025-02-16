# sentiment_dashboard.py

import streamlit as st
import asyncio
import websockets
import json
import pandas as pd
from sqlalchemy import create_engine

# Database setup
DATABASE_URL = "postgresql://postgres:1111@localhost:5432/sentiment_db"  # Replace with your credentials
engine = create_engine(DATABASE_URL)

# Streamlit app title
st.title("Real-Time Sentiment Analysis Dashboard")

# WebSocket URL (replace with your backend URL)
WEBSOCKET_URL = "ws://localhost:8000/ws"

# Function to fetch historical data
def fetch_historical_data():
    query = "SELECT * FROM raw_tweets ORDER BY created_at DESC LIMIT 100"
    return pd.read_sql(query, engine)

# Function to connect to WebSocket and receive updates
async def receive_updates():
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        st.write("Connected to WebSocket for real-time updates!")
        while True:
            try:
                # Receive data from WebSocket
                data = await websocket.recv()
                tweet_data = json.loads(data)

                # Display the tweet and sentiment
                st.write(f"**Tweet:** {tweet_data['tweet']}")
                st.write(f"**Sentiment:** {tweet_data['sentiment']} (Confidence: {tweet_data['confidence']:.2f})")
                st.write("---")
            except Exception as e:
                st.error(f"Error receiving data: {e}")
                break

# Display historical data
st.header("Historical Data")
historical_data = fetch_historical_data()
st.write(historical_data)

# Start the WebSocket connection
if st.button("Start Real-Time Updates"):
    asyncio.run(receive_updates())
