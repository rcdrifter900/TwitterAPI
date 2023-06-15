import base64
import hashlib
import os
import re
import json
import requests
import tweepy
import sqlite3
import redis
from requests.auth import AuthBase, HTTPBasicAuth
from requests_oauthlib import OAuth2Session, TokenUpdated
from flask import Flask, request, redirect, session, url_for, render_template
from Support.load_file import get_API_keys

app = Flask(__name__)
app.secret_key = os.urandom(50)


dict = get_API_keys()
client_id = dict['ClientID']
client_secret = dict['ClientSecret']
api_key = dict['APIKey']
api_secret = dict['APISecret']
auth_url = "https://twitter.com/i/oauth2/authorize"
token_url = "https://api.twitter.com/2/oauth2/token"
redirect_uri = 'http://127.0.0.1:5000/oauth/callback'
redis_url = 'rediss://red-ci53frenqqlc6v0m12og:6di3l9h2c1DTCbS5tEZUtGfvt1ySJIs0@oregon-redis.render.com:6379'

r = redis.from_url(redis_url)

# Set the scopes
scopes = ["tweet.read", "users.read", "tweet.write", "offline.access"]

# Create a code verifier
code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

# Create a code challenge
code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")


def make_token():
    return OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)


def upload_media():
    tweepy_auth = tweepy.OAuth1UserHandler(
        consumer_key = api_key,
        consumer_secret = api_secret,
        access_token = client_id,
        access_token_secret = client_secret
    )
    tweepy_api = tweepy.API(tweepy_auth)
    url = "https://api.thecatapi.com/v1/images/search"
    cats = requests.request("GET", url).json()
    cat_pic = cats[0]["url"]
    img_data = requests.get(cat_pic).content
    with open("catpic.jpg", "wb") as handler:
        handler.write(img_data)
    post = tweepy_api.simple_upload("catpic.jpg")
    text = str(post)
    media_id = re.search("media_id=(.+?),", text).group(1)
    payload = {"media": {"media_ids": ["{}".format(media_id)]}}
    os.remove("catpic.jpg")
    return payload


def post_tweet(payload, token):
    print("Tweeting!")
    return requests.request(
        "POST",
        "https://api.twitter.com/2/tweets",
        json=payload,
        headers={
            "Authorization": "Bearer {}".format(token["access_token"]),
            "Content-Type": "application/json",
        },
    )


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/start")
def demo():
    global twitter
    twitter = make_token()
    authorization_url, state = twitter.authorization_url(
        auth_url, code_challenge=code_challenge, code_challenge_method="S256"
    )
    session["oauth_state"] = state
    return redirect(authorization_url)


@app.route("/oauth/callback", methods=["GET"])
def callback():
    code = request.args.get("code")
    token = twitter.fetch_token(
        token_url=token_url,
        client_secret=client_secret,
        code_verifier=code_verifier,
        code=code,
    )
    st_token = '"{}"'.format(token)
    j_token = json.loads(st_token)
    r.set("token", j_token)
    payload = upload_media()
    # The first Tweet after auth
    response = post_tweet(payload, token)
    return render_template("thank-you.html")


if __name__ == "__main__":
    app.run()