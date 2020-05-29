
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

    recently_played_json = sp.current_user_recently_played(limit=2)
    recently_played = list()

    for item in recently_played_json["items"]:
        track_name = item["track"]["name"]
        artist_name = item["track"]["artists"][0]["name"]
        played_at = datetime.strptime(item["played_at"], '%Y-%m-%dT%H:%M:%S.%fZ')
        recently_played.append([track_name, artist_name, played_at])
    
    return recently_played


def get_genius_lyrics(recently_played):

    genius = lyricsgenius.Genius(os.environ.get("GENIUS_CLIENT_ACCESS_TOKEN"))
    genius.verbose = False
    genius.remove_section_headers = True

    for count, song in enumerate(recently_played):
        song_name = song[0]
        artist_name = song[1]
        genius_search = genius.search_song(song_name, artist_name)

        if not genius_search:
            recently_played[count].append("")
            break
    
        recently_played[count].append(genius_search.lyrics)
    
    return recently_played

def connect_to_db():
    
    conn = sqlite3.connect("spearworm.db")
    
    return conn, conn.cursor()

def initial_db_setup(cursor):

    # Create table for recently played songs
    recently_played_table = "CREATE TABLE recently_played(ID INT AUTO_INCREMENT PRIMARY KEY, song_id INT, last_played DATETIME)"
    cursor.execute(recently_played_table)

    # Create a table for all songs listened to
    songs_table = "CREATE TABLE songs(ID INT AUTO_INCREMENT PRIMARY KEY, song_name TINYTEXT, artist1_id INT, artist2_id INT, lyrics TEXT, first_played DATETIME)"
    cursor.execute(songs_table)

    # Create a table for all artists listened to
    artists_table = "CREATE TABLE artists(ID INT AUTO_INCREMENT PRIMARY KEY, artist_name TINYTEXT, first_played DATETIME)"
    cursor.execute(artists_table)
    

def close_db_cursor_and_conn(conn, cursor):
    cursor.close()
    conn.close()

def add_recent_to_db(recent_data, cursor):
    for song in recent_data:
        #TODO need to check for artist_id, and check for song_id for last_played
        print("song_name: %s \nartist: %s \nlast_played: %s \nlyrics: %s \n" % (song[0], song[1], song[2], song[3]))

def main():

    # username = input("Please enter your Spotify username: ")
    username = "mewuzhere"

    print("Connecting to Spotify...")
    sp =connect_to_spotify(username)

    print("Retrieving {username}'s recently played...".format(username=username))
    recently_played = get_recently_played(sp)

    print("Fetching song lyrics...")
    recently_played = get_genius_lyrics(recently_played)

    print("Connecting to database...")
    conn, cursor = connect_to_db()
    check_tables_exist = "SELECT name FROM sqlite_master WHERE type='table';"
    cursor.execute(check_tables_exist)
    
    # Check if tables have already been created
    if not cursor.fetchall():
        print("Creating tables in database...")
        initial_db_setup(cursor)
    
    print("Adding recent data to database")
    add_recent_to_db(recently_played, cursor)

    print("Closing connection to database...")
    close_db_cursor_and_conn(conn, cursor)

if __name__ == "__main__":
    main()
