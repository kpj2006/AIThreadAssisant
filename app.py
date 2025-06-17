# app.py

import os
import re
import time
import tweepy
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Core Tweepy Logic (Modified for Web App) ---

def get_twitter_client():
    """Authenticates with Twitter API v2 and returns a client object."""
    try:
        client = tweepy.Client(
            consumer_key=os.environ.get("TWITTER_API_KEY"),
            consumer_secret=os.environ.get("TWITTER_API_SECRET"),
            access_token=os.environ.get("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
        )
        me = client.get_me()
        return client, me.data.username, None
    except Exception as e:
        error_message = f"❌ Authentication Error: {e}. Check your API keys and permissions in your environment variables."
        return None, None, error_message

def parse_thread_input(thread_text):
    """Parses the numbered input string into a clean list of tweets."""
    lines = [line.strip() for line in thread_text.strip().split('\n') if line.strip()]
    tweets = [re.sub(r'^\d+/\s*', '', line) for line in lines]
    return tweets

def post_thread(client, username, tweets):
    """
    Posts a list of tweets as a nested thread.
    Returns a list of log messages and a boolean for success.
    """
    previous_tweet_id = None
    log_messages = []
    
    for i, tweet_text in enumerate(tweets):
        log_messages.append(f"Posting tweet {i+1}/{len(tweets)}: \"{tweet_text[:40]}...\"")
        
        try:
            if previous_tweet_id is None:
                response = client.create_tweet(text=tweet_text)
            else:
                response = client.create_tweet(
                    text=tweet_text, 
                    in_reply_to_tweet_id=previous_tweet_id
                )
            
            new_tweet_id = response.data['id']
            tweet_url = f"https://twitter.com/{username}/status/{new_tweet_id}"
            
            log_messages.append(f"✅ Success! URL: {tweet_url}")
            previous_tweet_id = new_tweet_id
            time.sleep(1) # Small delay is good practice

        except tweepy.errors.TweepyException as e:
            error_detail = f"❌ Error on tweet {i+1}: {e}"
            log_messages.append(error_detail)
            log_messages.append("🛑 Halting thread due to error.")
            return log_messages, False
            
    log_messages.append("\n🎉 Full thread posted successfully!")
    return log_messages, True

# --- Flask API Endpoints ---

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/post-thread', methods=['POST'])
def handle_post_thread():
    """Receives thread text and posts it."""
    data = request.get_json()
    thread_text = data.get('thread_text')

    if not thread_text:
        return jsonify({"success": False, "log": ["Error: No thread text provided."]})

    client, username, auth_error = get_twitter_client()
    if auth_error:
        return jsonify({"success": False, "log": [auth_error]})

    tweets_to_post = parse_thread_input(thread_text)
    if not tweets_to_post:
        return jsonify({"success": False, "log": ["Error: Input is empty or invalid."]})

    log, success = post_thread(client, username, tweets_to_post)
    
    return jsonify({"success": success, "log": log})

# --- Main execution ---
if __name__ == '__main__':
    # For development, you can run this script directly.
    # For production, use a proper WSGI server like Gunicorn.
    app.run(debug=True, port=5001)