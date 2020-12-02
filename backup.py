
import os
import sys

import database as db
import spotify

ALREADY_BACKED_UP = 0

def backup():

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

    if not load_history in ["y", "Y", "Yes", "yes"]:
        print("Exiting program...")
        sys.exit()

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

            db.add_track_to_db(
                cursor,
                artist_names=[track["artistName"]],
                song_name=track["trackName"],
                played_at=track["endTime"],
            )

            # Commit every 20 songs to prevent total loss if program encounters error
            if not count % 20:
                print("Commited up to song #%i..." % total_tracks)
                conn.commit()
