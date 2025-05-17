from .track_selection import fetch_trending_tracks
import math
import random

def get_key_compatibility(current_key, target_key):
    """
    Determine if two keys are harmonically compatible using a simplified Camelot wheel approach.
    Compatible keys include same key, relative minor/major, and adjacent keys.
    """
    key_map = {
        'C': ['C', 'Am', 'G', 'F', 'Em', 'Dm'],
        'Am': ['Am', 'C', 'F', 'G', 'Dm', 'Em'],
        'G': ['G', 'Em', 'C', 'D', 'Am', 'Bm'],
        'F': ['F', 'Dm', 'C', 'Bb', 'Am', 'Gm'],
        'D': ['D', 'Bm', 'G', 'A', 'F#m', 'Em'],
        'Bb': ['Bb', 'Gm', 'F', 'Eb', 'Dm', 'Cm'],
    }
    return target_key in key_map.get(current_key, [current_key])

def get_bpm_compatibility(current_bpm, target_bpm, tolerance=5):
    """
    Check if two tracks have compatible BPMs within a tolerance range.
    Includes double/half tempo compatibility.
    """
    return (
        abs(current_bpm - target_bpm) <= tolerance or
        abs(current_bpm * 2 - target_bpm) <= tolerance or
        abs(current_bpm / 2 - target_bpm) <= tolerance
    )

def fetch_non_trending_tracks(genre, country, trending_tracks, token_info=None):
    """
    Fetch tracks that are not in the trending tracks list or user's set.
    Uses Spotify API to fetch fresh tracks each time.
    
    Args:
        genre: Genre of tracks
        country: Country code
        trending_tracks: List of trending tracks to exclude
        token_info: Spotify OAuth token info
    
    Returns:
        List of non-trending tracks
    """
    try:
        import spotipy
        sp = spotipy.Spotify(auth=token_info['access_token'])
        query = f"genre:{genre}"
        # Randomize offset to get varied tracks each call
        offset = random.randint(0, 100)
        results = sp.search(q=query, type='track', market=country, limit=50, offset=offset)
        tracks = results['tracks']['items']
        trending_ids = {track['id'] for track in trending_tracks}
        non_trending = []
        for track in tracks:
            if track['id'] in trending_ids:
                continue
            # Placeholder key/BPM; replace with Audio Analysis for accuracy
            non_trending.append({
                'id': track['id'],
                'title': track['name'],
                'artist': track['artists'][0]['name'],
                'image_url': track['album']['images'][0]['url'] if track['album']['images'] else '',
                'key': 'C',  # Replace with actual key
                'bpm': 128   # Replace with actual BPM
            })
        return non_trending
    except Exception as e:
        print(f"Error fetching non-trending tracks: {e}")
        return []

def recommend_tracks(user_id, dj_sets, num_recommendations=5, token_info=None):
    """
    Recommend tracks based on the most recently added track in the user's DJ set.
    Excludes trending tracks and tracks in the set. Ranks all candidates and returns top 5.
    
    Args:
        user_id: ID of the user
        dj_sets: Dictionary containing user DJ sets
        num_recommendations: Number of tracks to recommend
        token_info: Spotify OAuth token info
    
    Returns:
        List of recommended tracks
    """
    user_set = dj_sets.get(user_id)
    if not user_set or not user_set['set_list']:
        return []

    # Use the most recently added track
    last_track = user_set['set_list'][-1]
    genre = user_set['genre']
    country = user_set['country']
    
    current_key = last_track.get('key', 'C')
    current_bpm = last_track.get('bpm', 128)

    # Get trending tracks to exclude
    trending_tracks = user_set.get('available_tracks', [])
    
    # Fetch fresh non-trending tracks
    candidate_tracks = fetch_non_trending_tracks(genre, country, trending_tracks, token_info)
    
    # Exclude tracks in the set
    used_ids = {track['id'] for track in user_set['set_list']}
    available_tracks = [t for t in candidate_tracks if t['id'] not in used_ids]

    # Score and rank tracks
    recommendations = []
    for track in available_tracks:
        track_key = track.get('key', 'C')
        track_bpm = track.get('bpm', 128)
        
        key_compatible = get_key_compatibility(current_key, track_key)
        bpm_compatible = get_bpm_compatibility(current_bpm, track_bpm)
        
        if key_compatible and bpm_compatible:
            bpm_diff = abs(current_bpm - track_bpm)
            key_score = 1.0 if current_key == track_key else 0.8
            score = key_score / (1 + bpm_diff)
            recommendations.append((track, score))

    # Sort by score and return top 5
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return [track for track, _ in recommendations[:num_recommendations]]

def update_recommendations(user_id, dj_sets, token_info=None):
    """
    Update available tracks with new recommendations based on the current set.
    
    Args:
        user_id: ID of the user
        dj_sets: Dictionary containing user DJ sets
        token_info: Spotify OAuth token info
    """
    recommendations = recommend_tracks(user_id, dj_sets, token_info=token_info)
    user_set = dj_sets.get(user_id)
    if user_set:
        user_set['available_tracks'] = recommendations