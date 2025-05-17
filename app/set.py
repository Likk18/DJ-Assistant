import sqlite3
import os
from typing import List, Dict, Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import uuid

# Load environment variables from .env file in project root
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Check for required environment variables
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
if not client_id or not client_secret:
    raise EnvironmentError(
        f"Missing Spotify credentials. Ensure SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET are set in {env_path}."
    )

# Initialize Spotify client
try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    ))
except spotipy.exceptions.SpotifyOauthError as e:
    raise EnvironmentError(f"Failed to initialize Spotify client: {str(e)}")

# Database setup
DB_PATH = os.getenv("DJ_DB_PATH", "dj_assistant.db")

def init_db():
    """Initialize the database with required tables."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dj_sets (
                set_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                genre TEXT,
                country TEXT,
                set_name TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                set_id TEXT,
                track_id TEXT,
                track_name TEXT,
                artist TEXT,
                FOREIGN KEY (set_id) REFERENCES dj_sets (set_id)
            )
        """)
        conn.commit()

# Initialize database on module load
init_db()

def start_set(user_id: str, genre: str, country: str, set_name: str) -> str:
    """Create a new DJ set in the database and return set_id."""
    if not all([user_id, set_name]):
        raise ValueError("Missing user_id or set_name")
    set_id = str(uuid.uuid4())
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO dj_sets (set_id, user_id, genre, country, set_name)
                VALUES (?, ?, ?, ?, ?)
                """,
                (set_id, user_id, genre, country, set_name)
            )
            conn.commit()
            return set_id
    except sqlite3.Error as e:
        raise Exception(f"Database error: {str(e)}")

def add_track_to_set(user_id: str, set_id: str, track: Dict) -> None:
    """Add a track to an existing DJ set in the database."""
    if not all([user_id, set_id, track]):
        raise ValueError("Missing user_id, set_id, or track")
    track_id = track.get('id')
    track_name = track.get('name')
    artist = track.get('artists', [{}])[0].get('name')
    if not all([track_id, track_name, artist]):
        raise ValueError("Invalid track data")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Check if set exists and belongs to user
            cursor.execute(
                """
                SELECT 1 FROM dj_sets WHERE set_id = ? AND user_id = ?
                """,
                (set_id, user_id)
            )
            if not cursor.fetchone():
                raise ValueError("Set not found or unauthorized")
            cursor.execute(
                """
                INSERT INTO tracks (set_id, track_id, track_name, artist)
                VALUES (?, ?, ?, ?)
                """,
                (set_id, track_id, track_name, artist)
            )
            conn.commit()
    except sqlite3.Error as e:
        raise Exception(f"Database error: {str(e)}")

def remove_track_from_set(user_id: str, set_id: str, track_id: str) -> None:
    """Remove a specific track from a DJ set in the database."""
    if not all([user_id, set_id, track_id]):
        raise ValueError("Missing user_id, set_id, or track_id")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Check if set exists and belongs to user
            cursor.execute(
                """
                SELECT 1 FROM dj_sets WHERE set_id = ? AND user_id = ?
                """,
                (set_id, user_id)
            )
            if not cursor.fetchone():
                raise ValueError("Set not found or unauthorized")
            cursor.execute(
                """
                DELETE FROM tracks WHERE set_id = ? AND track_id = ?
                """,
                (set_id, track_id)
            )
            conn.commit()
            if cursor.rowcount == 0:
                raise ValueError("Track not found in set")
    except sqlite3.Error as e:
        raise Exception(f"Database error: {str(e)}")

def get_set_tracks(set_id: str) -> List[Dict]:
    """Retrieve the tracks in a DJ set from the database."""
    if not set_id:
        raise ValueError("Missing set_id")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT track_id AS id, track_name AS name, artist
                FROM tracks WHERE set_id = ?
                """,
                (set_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise Exception(f"Database error: {str(e)}")

def update_set_name(set_id: str, set_name: str) -> None:
    """Update the name of an existing DJ set in the database."""
    if not all([set_id, set_name]):
        raise ValueError("Missing set_id or set_name")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE dj_sets SET set_name = ? WHERE set_id = ?
                """,
                (set_name, set_id)
            )
            conn.commit()
            if cursor.rowcount == 0:
                raise ValueError("Set not found")
    except sqlite3.Error as e:
        raise Exception(f"Database error: {str(e)}")