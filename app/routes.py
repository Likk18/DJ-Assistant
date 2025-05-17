from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from spotipy.oauth2 import SpotifyOAuth
from .track_selection import fetch_tracks
from .dj_set_generator import start_set, add_track, suggest_next_tracks
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if 'token_info' not in session:
        return redirect(url_for('main.auth'))
    return render_template('index.html')

@bp.route('/auth')
def auth():
    return render_template('auth.html')

@bp.route('/login')
def login():
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scope='user-library-read user-read-private user-read-email'
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@bp.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scope='user-library-read user-read-private user-read-email'
    )
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    import spotipy
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_info = sp.current_user()
    session['user_id'] = user_info['id']
    # Store user_id in sessionStorage via client-side script
    return '''
    <script>
        sessionStorage.setItem('user_id', '{}');
        window.location = '{}';
    </script>
    '''.format(user_info['id'], url_for('main.dj_page'))

@bp.route('/dj')
def dj_page():
    if 'token_info' not in session:
        return redirect(url_for('main.auth'))
    return render_template('dj_set.html')

@bp.route('/tracks')
def get_tracks():
    genre = request.args.get('genre', 'techno')
    country = request.args.get('country', 'Germany')
    if 'token_info' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    try:
        tracks = fetch_tracks(genre, country)
        return jsonify(tracks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/suggest-tracks')
def suggest_tracks():
    user_id = session.get('user_id', 'default_user')
    token_info = session.get('token_info')
    if not token_info:
        return jsonify({'error': 'Authentication required'}), 401
    try:
        suggestions = suggest_next_tracks(user_id, token_info=token_info)
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/start-set', methods=['POST'])
def start_set_endpoint():
    data = request.json or {}
    genre = data.get('genre')
    country = data.get('country')
    if not genre or not country:
        return jsonify({'error': 'Genre and country required'}), 400
    user_id = session.get('user_id', 'default_user')
    try:
        start_set(user_id, genre, country)
        return jsonify({'message': 'Set started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/add-track', methods=['POST'])
def add_track_endpoint():
    data = request.json or {}
    track_id = data.get('track_id')
    user_id = session.get('user_id', 'default_user')
    token_info = session.get('token_info')
    if not token_info:
        return jsonify({'error': 'Authentication required'}), 401
    if not track_id:
        return jsonify({'error': 'Track ID required'}), 400
    try:
        track = add_track(user_id, track_id, token_info=token_info)
        return jsonify(track)
    except Exception as e:
        return jsonify({'error': str(e)}), 400