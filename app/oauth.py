# app/oauth.py

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import session

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scope='user-library-read'
    )

def get_spotify_user_client():
    sp_oauth = get_spotify_oauth()

    token_info = session.get('token_info', None)

    if not token_info:
        raise Exception("User not logged in or token info missing")

    # Check if token is expired, refresh if needed
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    access_token = token_info['access_token']

    return spotipy.Spotify(auth=access_token)
