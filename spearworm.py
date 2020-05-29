
import os
import sqlite3
import sys
from datetime import datetime

import lyricsgenius
import spotipy
import spotipy.util as util


def connect_to_spotify(username):
    token = util.prompt_for_user_token(username, scope="user-read-recently-played")
    
    if token:
        return spotipy.Spotify(auth=token)
    else:
        sys.exit("Failed to connect to Spotify")

def get_recently_played(sp):

    # Get recernly played songs in JSON format form Spotify
    recently_played_json = sp.current_user_recently_played(limit=2)
    
    # Initialize list for recently played data
    recently_played = []
    
    # Initializing track dictionary for track values
    track = {}

    # Iterate over the recently played tracks and add them to track_dict 
    # then append track to recently played list
    for item in recently_played_json["items"]:
        track["song_name"] = item["track"]["name"]
        track["artist_name"] = item["track"]["artists"][0]["name"]
        track["played_at"] = datetime.strptime(item["played_at"], '%Y-%m-%dT%H:%M:%S.%fZ')

        recently_played.append(track)

        # Clear for next track
        track = {}

    return recently_played


def get_genius_lyrics(recently_played):

    genius = lyricsgenius.Genius(os.environ.get("GENIUS_CLIENT_ACCESS_TOKEN"))
    genius.verbose = False
    genius.remove_section_headers = True

    for song in recently_played:
        song_name = song["song_name"]
        artist_name = song["artist_name"]
        genius_search = genius.search_song(song_name, artist_name)

        if not genius_search:
            recently_played["lyrics"] = ""
            break
    
        recently_played["lyrics"] = genius_search.lyrics

    return recently_played

def connect_to_db():
    
    conn = sqlite3.connect("spearworm.db")
    
    return conn, conn.cursor()

def initial_db_setup(cursor):

    # Create table for recently played songs
    recently_played_table = "CREATE TABLE recently_played(ID INTEGER PRIMARY KEY AUTOINCREMENT , song_id INT, last_played DATETIME)"
    cursor.execute(recently_played_table)

    # Create a table for all songs listened to
    songs_table = "CREATE TABLE songs(ID INTEGER PRIMARY KEY AUTOINCREMENT, song_name TINYTEXT, artist1_id INT, artist2_id INT, lyrics TEXT, first_played DATETIME)"
    cursor.execute(songs_table)

    # Create a table for all artists listened to
    artists_table = "CREATE TABLE artists(ID INTEGER PRIMARY KEY AUTOINCREMENT, artist_name TINYTEXT, first_played DATETIME)"
    cursor.execute(artists_table)
    

def close_db_cursor_and_conn(conn, cursor):
    cursor.close()
    conn.close()

def add_recently_played_to_db(recently_played, cursor):

    # Order changed to make songs appear in order they were listened to
    recently_played.reverse()

    for song in recently_played:

        # Check if artist is in DB already
        # If not, add artist info and get the new id from db
        # If it is, get the id from the tuple

        artist_check = "SELECT id FROM artists WHERE artist_name=?"
        cursor.execute(artist_check, (song["artist_name"],))
        artist_id = cursor.fetchone()

        if not artist_id:
            add_artist = "INSERT INTO artists(artist_name, first_played) VALUES(?,?)"
            cursor.execute(add_artist, (song["artist_name"], song["played_at"]))
            cursor.execute(artist_check, (song["artist_name"],))
            artist_id = cursor.fetchone()[0]
        else:
            artist_id = artist_id[0]

        # Check if song is already in DB
        song_check = "SELECT id FROM songs WHERE song_name=? AND artist1_id=?"
        cursor.execute(song_check, (song["song_name"], artist_id))
        song_id = cursor.fetchone()

        if not song_id:
            add_artist = "INSERT INTO songs(song_name, artist1_id, first_played) VALUES(?,?,?)"
            cursor.execute(add_artist, (song["song_name"],artist_id, song["played_at"]))
            cursor.execute(song_check, (song["song_name"], artist_id))
            song_id = cursor.fetchone()[0]
        else:
            song_id = song_id[0]

        #TODO secondary artist handling, adding values to recently_played (maybe rename to listening_history), enter in the old data, setup interface to search for lyrics (filter by artist, name, lyric, dates (first/recent)), set up to backup periodically (maybe when spotify is open for period of time/when it is closed) 
        print("song_name: %s \nartist: %s \nlast_played: %s \n" % (song["song_name"], song["artist_name"], song["played_at"]))

def main():

    # username = input("Please enter your Spotify username: ")
    username = "mewuzhere"

    print("Connecting to Spotify...")
    sp =connect_to_spotify(username)

    print("Retrieving {username}'s recently played...".format(username=username))
    recently_played = get_recently_played(sp)

    # print("Fetching song lyrics...")
    # recently_played = get_genius_lyrics(recently_played)

    print("Connecting to database...")
    conn, cursor = connect_to_db()
    check_tables_exist = "SELECT name FROM sqlite_master WHERE type='table';"
    cursor.execute(check_tables_exist)
    
    # Check if tables have already been created
    if not cursor.fetchall():
        print("Creating tables...")
        initial_db_setup(cursor)
    
    print("Adding recent data...")
    add_recently_played_to_db(recently_played, cursor)

    print("Committing changes...")
    conn.commit()

    print("Closing connection...")
    close_db_cursor_and_conn(conn, cursor)

if __name__ == "__main__":
    main()
