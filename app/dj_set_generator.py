from .track_selection import fetch_trending_tracks
from .recommendations import recommend_tracks

# Global dict to store sets: user_id -> dict with keys 'genre', 'country', 'set_list', 'available_tracks'
dj_sets = {}

def start_set(user_id, genre, country):
    trending = fetch_trending_tracks(genre, country)
    dj_sets[user_id] = {
        'genre': genre,
        'country': country,
        'set_list': [],
        'available_tracks': trending
    }

def add_track(user_id, track_id, token_info=None):
    user_set = dj_sets.get(user_id)
    if not user_set:
        raise Exception("No active DJ set found for user")

    track = {'id': track_id}
    user_set['set_list'].append(track)
    user_set['available_tracks'] = recommend_tracks(user_id, dj_sets, token_info=token_info)

    try:
        import spotipy
        sp = spotipy.Spotify(auth=token_info['access_token'])
        track_data = sp.track(track_id)
        features = sp.audio_features(track_id)[0]
        key_map = {0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'}
        key = key_map.get(features['key'], 'C') + ('m' if features['mode'] == 0 else '')
        track = {
            'id': track_id,
            'title': track_data['name'],
            'artist': track_data['artists'][0]['name'],
            'image_url': track_data['album']['images'][0]['url'] if track_data['album']['images'] else '',
            'key': key,
            'bpm': round(features['tempo'])
        }
        # Update set with full track details
        user_set['set_list'][-1] = track
    except Exception as e:
        print(f"Error fetching track details: {e}")

    return track

def get_set(user_id):
    user_set = dj_sets.get(user_id)
    if not user_set:
        return []
    return user_set['set_list']

def suggest_next_tracks(user_id, token_info=None):
    return recommend_tracks(user_id, dj_sets, token_info=token_info)