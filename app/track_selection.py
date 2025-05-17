import os
import time
import requests
from .oauth import get_spotify_user_client

# ----------------------------------------
# Get Access Token for Client Credentials
# ----------------------------------------
def get_access_token():
    try:
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_response = requests.post(auth_url, {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        })
        auth_response.raise_for_status()
        return auth_response.json()['access_token']
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

# ----------------------------------------
# Fetch Trending Tracks by Genre & Country (with cover image)
# ----------------------------------------
def fetch_trending_tracks(genre, country='United States'):
    country_to_market = {
        'united states': 'US',
        'germany': 'DE',
        'united kingdom': 'GB',
        'france': 'FR',
        'canada': 'CA',
        'australia': 'AU',
        'brazil': 'BR',
        'india': 'IN',
        'japan': 'JP',
        'mexico': 'MX',
    }
    market = country_to_market.get(country.lower(), 'US')
    print(f"Using market code: {market} for country: {country}")

    tracks = []
    try:
        access_token = get_access_token()
        if not access_token:
            print("Failed to obtain access token")
            return tracks

        search_url = 'https://api.spotify.com/v1/search'
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'q': f'genre:"{genre}"',
            'type': 'track',
            'market': market,
            'limit': 50,
        }
        for attempt in range(2):
            try:
                response = requests.get(search_url, headers=headers, params=params)
                response.raise_for_status()
                results = response.json()
                if 'tracks' in results and 'items' in results['tracks']:
                    track_list = [
                        {
                            'id': t['id'],
                            'title': t['name'],
                            'artist': t['artists'][0]['name'],
                            'image_url': t['album']['images'][0]['url'] if t.get('album') and t['album'].get('images') else None,
                            'source': 'trending'
                        }
                        for t in results['tracks']['items'] if t and t['id'] and t['name'] and t['artists']
                    ]
                    tracks.extend(track_list)
                    print(f"Fetched {len(track_list)} trending {genre} tracks in market {market}")
                else:
                    print(f"No trending tracks found for genre '{genre}' in market {market}")
                break
            except Exception as e:
                print(f"Error fetching tracks (attempt {attempt + 1}): {e}")
                if attempt == 0:
                    time.sleep(1)
                continue
    except Exception as e:
        print(f"Error in fetch_trending_tracks: {e}")

    return tracks

# ----------------------------------------
# Get User's Saved Tracks That Match Trending Tracks
# ----------------------------------------
def get_user_trending_matches(trending_tracks):
    sp = get_spotify_user_client()
    matched_user_tracks = []

    try:
        saved = sp.current_user_saved_tracks(limit=50)['items']
        saved_ids = {item['track']['id'] for item in saved}

        for t in trending_tracks:
            if t['id'] in saved_ids:
                matched_track = t.copy()
                matched_track['source'] = 'user_saved'
                matched_user_tracks.append(matched_track)

        print(f"Matched {len(matched_user_tracks)} of your saved tracks with trending ones.")

    except Exception as e:
        print(f"Error fetching user's saved tracks: {e}")

    return matched_user_tracks

# ----------------------------------------
# Combine and Return Tracks: User's Matches On Top
# ----------------------------------------
def fetch_tracks(genre, country='United States'):
    trending = fetch_trending_tracks(genre, country)
    user_trending = get_user_trending_matches(trending)

    user_ids = {t['id'] for t in user_trending}
    rest_trending = [t for t in trending if t['id'] not in user_ids]

    final = user_trending + rest_trending

    print(f"Returning {len(final)} tracks: {len(user_trending)} user + {len(rest_trending)} trending")
    return final
