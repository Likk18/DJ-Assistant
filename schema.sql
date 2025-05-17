CREATE TABLE users (
    user_id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) NOT NULL
);

CREATE TABLE dj_sets (
    set_id UUID PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(user_id),
    set_name VARCHAR(255) NOT NULL,
    genre VARCHAR(100),
    country VARCHAR(100),
    track_id VARCHAR(255),
    sl_no INTEGER,
    title VARCHAR(255),
    artist_name VARCHAR(255),
    image_url TEXT,
    key VARCHAR(3),
    bpm INTEGER,
    UNIQUE(set_id, sl_no)
);

