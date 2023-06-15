import gsd
import sqlite3
import redis
import json
import os
from Support.load_file import get_API_keys

twitter = gsd.make_token()
dict = get_API_keys()
client_id = dict['ClientID']
client_secret = dict['ClientSecret']
token_url = "https://api.twitter.com/2/oauth2/token"

twitter_database = "TwitterAPI.db"

t = gsd.r.get("token")
print(t)
bb_t = t.decode("utf8").replace("'", '"')
data = json.loads(t)

refreshed_token = twitter.refresh_token(
    client_id=client_id,
    client_secret=client_secret,
    token_url=token_url,
    refresh_token=data["refresh_token"],
)


st_refreshed_token = '"{}"'.format(refreshed_token)
j_refreshed_token = json.loads(st_refreshed_token)
gsd.r.set("token", j_refreshed_token)

payload = gsd.upload_media()
gsd.post_tweet(payload, refreshed_token)