
import sqlite3
import lyrics


def connect_to_db():

    conn = sqlite3.connect("spearworm.db")

    return conn, conn.cursor()


def initial_db_setup(cursor):

    # Create table for recently played songs
    recently_played_table = "CREATE TABLE history(ID INTEGER PRIMARY KEY AUTOINCREMENT, song_id INT, played_at DATETIME)"
    cursor.execute(recently_played_table)

    # Create a table for all songs listened to
    songs_table = "CREATE TABLE songs(ID INTEGER PRIMARY KEY AUTOINCREMENT, song_name TINYTEXT, artist1_id INT, artist2_id INT, lyrics TEXT, first_played DATETIME)"
    cursor.execute(songs_table)

    # Create a table for all artists listened to
    artists_table = "CREATE TABLE artists(ID INTEGER PRIMARY KEY AUTOINCREMENT, artist_name TINYTEXT, first_played DATETIME)"
    cursor.execute(artists_table)


def close_db_cursor_and_conn(conn, cursor):
    """
    Closes SQLITE connection and cursor

    Parameters
    ----------
    conn : SQLITE connnection object \n
    cursor : SQLITE cursor object
    """
    cursor.close()
    conn.close()


def add_track_to_db(cursor, artist_names, song_name, played_at):
    """
    Adds track information and Spotify history to SQLITE database with tables:  
    'songs', 'artists', and 'history'

    Parameters
    ----------
    cursor : SQLITE cursor object
    arist_names : list
        List of artist names featured on track
    song_name : str
        Title of a song
    played_at: datetime object
        Datetime that a track was played
    """

    # Check if artist is in DB already
    # If not, add artist info and get the new id from db
    # If it is, get the id from the tuple
    artist_ids = []
    for artist in artist_names:

        artist_id = find_artist_in_db(cursor, artist)

        if not artist_id:
            add_artist_to_db(cursor, artist, played_at)
            artist_ids.append(find_artist_in_db(cursor, artist)[0])
        else:
            artist_ids.append(artist_id[0])

    # Check if song is already in DB
    # If not, get lyrics and add song info and get the new id from db
    # If it is, get the id from the tuple
    song_id = find_song_in_db(cursor, song_name, artist_ids[0])

    if not song_id:

        print("Fetching song lyrics for %s..." % song_name)
        song_lyrics = lyrics.get_genius_lyrics(
            song_name, artist_names[0]
        )

        add_song_to_db(cursor, song_name, artist_ids, song_lyrics, played_at)
        song_id = find_song_in_db(cursor, song_name, artist_ids[0])[0]

    else:
        song_id = song_id[0]

    # Check if this listening instance has already been recorded
    # If not, add to db
    history_check = "SELECT id FROM history WHERE song_id=? AND played_at=?"
    cursor.execute(history_check, (song_id, played_at))
    history_id = cursor.fetchone()

    if not history_id:
        add_to_history = "INSERT INTO history(song_id, played_at) VALUES(?,?)"
        cursor.execute(add_to_history, (song_id, played_at))

def find_artist_in_db(cursor, artist_name):
    find_artist = "SELECT id FROM artists WHERE artist_name=?"
    cursor.execute(find_artist, (artist_name,))
    artist_id = cursor.fetchone()

    return artist_id

def add_artist_to_db(cursor, artist, played_at):
    add_artist = (
        "INSERT INTO artists(artist_name, first_played) VALUES(?,?)"
    )
    cursor.execute(add_artist, (artist, played_at))

def find_song_in_db(cursor, song_name, artist_id):
    song_check = "SELECT id FROM songs WHERE song_name=? AND artist1_id=?"
    cursor.execute(song_check, (song_name, artist_id))
    song_id = cursor.fetchone()

    return song_id

def add_song_to_db(cursor, song_name, artist_ids, lyrics, played_at):

    # Check if there are more than one artist featured on the track
    if len(artist_ids) > 1:
        add_song = "INSERT INTO songs(song_name, artist1_id, artist2_id, lyrics, first_played) VALUES(?,?,?,?,?)"
        cursor.execute(
            add_song,
            (
                song_name,
                artist_ids[0],
                artist_ids[1],
                lyrics,
                played_at,
            ),
        )

    else:
        add_song = "INSERT INTO songs(song_name, artist1_id, lyrics, first_played) VALUES(?,?,?,?)"
        cursor.execute(
            add_song,
            (
                song_name,
                artist_ids[0],
                lyrics,
                played_at,
            ),
        )

