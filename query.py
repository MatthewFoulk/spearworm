import os
import sys

import database as db


def main():

    print("Connecting to database...")
    conn, cursor = db.connect_to_db()

    # song_info = select_song(cursor)
    # print(song_info)

    history_info = select_history(cursor)
    print(history_info)

    print("Closing connection...")
    db.close_db_cursor_and_conn(conn, cursor)


def select_song(cursor):

    song_query = "SELECT ID, song_name, artist1_id, artist2_id, first_played FROM `songs` WHERE song_name='Mr Loverman'"
    cursor.execute(song_query)
    song_info = cursor.fetchall()

    return song_info


def select_history(cursor):
    history_query = "SELECT ID, song_id, played_at FROM `history` WHERE song_id='8012'"
    cursor.execute(history_query)
    history_info = cursor.fetchall()

    return history_info


if __name__ == "__main__":
    main()
