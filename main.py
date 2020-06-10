
import spotify
import database as db
import os
import sys

ALREADY_BACKED_UP = 0

# TODO enter in the old data
# TODO setup interface to search for lyrics (filter by artist, name, lyric, dates (first/recent))
# TODO set up to backup periodically (maybe when spotify is open for period of time/when it is closed

def main():

    # username = input("Please enter your Spotify username: ")
    username = "mewuzhere"

    print("Connecting to database...")
    conn, cursor = db.connect_to_db()
    check_tables_exist = "SELECT name FROM sqlite_master WHERE type='table';"
    cursor.execute(check_tables_exist)

    # Check if tables have already been created
    if not cursor.fetchall():
        print("Creating tables...")
        db.initial_db_setup(cursor)
    
    print("Would you like to load your streaming history (Y or N)...")
    load_history = input()

    if load_history == 'Y':
        mydata_check = os.path.exists("MyData")
        streaming_history_check = os.path.exists("MyData/streaminghistory0.json")

        if not mydata_check or not streaming_history_check:
            print("Streaming history could not be found...")
            print("Please download data from Spotify and add to this directory...")
            sys.exit()
        
        print("Adding streaming history...")
        streaming_history = spotify.get_streaming_history()
        
        total_tracks = 0

        for file_data in streaming_history:
            for count, track in enumerate(file_data):

                # Skip over ones previously logged
                total_tracks += 1
                if total_tracks < ALREADY_BACKED_UP:
                    print("Skipping songs already backed up...")
                    continue

                db.add_track_to_db(cursor, artist_names=[track["artistName"]], song_name=track["trackName"], played_at=track["endTime"])

                if not count % 20:
                    print("Commited up to #%i..." % total_tracks)
                    conn.commit()
    print("Connecting to Spotify...")
    spotify_conn = spotify.connect_to_spotify(username)

    print("Retrieving {username}'s recently played...".format(username=username))
    recently_played = spotify.get_recently_played(spotify_conn)

    print("Adding recent data...")
    for track in recently_played:
        db.add_track_to_db(cursor, artist_names=track["artist_names"], song_name=track["song_name"], played_at=track["played_at"])

    print("Committing changes...")
    conn.commit()

    print("Closing connection...")
    db.close_db_cursor_and_conn(conn, cursor)


if __name__ == "__main__":
    main()
