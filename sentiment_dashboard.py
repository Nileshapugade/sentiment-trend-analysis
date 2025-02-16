import os
import asyncio
import websockets
import json
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

try:
    import streamlit as st
    USE_STREAMLIT = True
except ModuleNotFoundError:
    print("Warning: Streamlit module not found. Running in console mode.")
    USE_STREAMLIT = False

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1111@localhost:5432/sentiment_db")
engine = create_engine(DATABASE_URL)

WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "ws://localhost:8000/ws")

def fetch_historical_data():
    try:
        query = "SELECT * FROM raw_tweets ORDER BY created_at DESC LIMIT 100"
        return pd.read_sql(query, engine)
    except SQLAlchemyError as e:
        error_message = f"Database error: {e}"
    except Exception as e:
        error_message = f"Error fetching data: {e}"
    else:
        return pd.DataFrame()
    
    if USE_STREAMLIT:
        st.error(error_message)
    else:
        print(error_message)
    return pd.DataFrame()

async def receive_updates():
    retries = 3
    while retries > 0:
        try:
            async with websockets.connect(WEBSOCKET_URL) as websocket:
                success_message = "Connected to WebSocket!"
                if USE_STREAMLIT:
                    st.write(success_message)
                else:
                    print(success_message)
                
                async for data in websocket:
                    try:
                        tweet_data = json.loads(data)
                        message = f"Tweet: {tweet_data.get('tweet', 'N/A')}\nSentiment: {tweet_data.get('sentiment', 'N/A')} (Confidence: {tweet_data.get('confidence', 0.0):.2f})\n---"
                        if USE_STREAMLIT:
                            st.write(message)
                        else:
                            print(message)
                    except json.JSONDecodeError:
                        error_message = "Received malformed JSON data. Skipping."
                        if USE_STREAMLIT:
                            st.error(error_message)
                        else:
                            print(error_message)
        except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.InvalidURI, OSError) as e:
            retries -= 1
            error_message = f"WebSocket error: {e}. Retrying in {4 - retries} seconds ({retries} attempts left)..."
            if USE_STREAMLIT:
                st.error(error_message)
            else:
                print(error_message)
            await asyncio.sleep(4 - retries)
        except Exception as e:
            error_message = f"Unexpected error: {e}"
            if USE_STREAMLIT:
                st.error(error_message)
            else:
                print(error_message)
            break
    
if USE_STREAMLIT:
    st.title("Real-Time Sentiment Analysis Dashboard")
    st.header("Historical Data")
    historical_data = fetch_historical_data()
    st.write(historical_data)

    if st.button("Start Real-Time Updates"):
        asyncio.run(receive_updates())
else:
    print("Historical Data:")
    print(fetch_historical_data())
    print("Starting real-time updates...")
    asyncio.run(receive_updates())

