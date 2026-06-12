import os
import sqlite3

DB_PATH = "music.db"

def getDBConnection(DBPath=DB_PATH):
    conn = sqlite3.connect(DBPath)
    conn.row_factory = sqlite3.Row

    return conn

def initDB():
    conn = getDBConnection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(255) NOT NULL,
        album_title VARCHAR(255),
        artist VARCHAR(255),
        featured VARCHAR(255),
        release_year INT,
        duration_seconds INT,
        file_path VARCHAR(512) NOT NULL UNIQUE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lyrics (
        song_id INT PRIMARY KEY,
        raw_lyrics TEXT,
        lrc_timestamped TEXT,
        FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
    );
    ''')

    conn.commit()
    conn.close()
   
   
   
   
   

   
   
   
   
   
   
   
   
   
   

   
   
   
   
   
   
   
   

   



