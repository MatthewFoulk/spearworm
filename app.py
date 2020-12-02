from flask import Flask, request, render_template, jsonify

import database

app = Flask("__name__")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():

    # Get the searched lyrics and artist from ajax get request
    lyrics = request.args.get("lyrics")
    artist = request.args.get("artist")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # If nothing searched, return blank html
    if not any([lyrics, artist, start_date, end_date]):
        return jsonify({"html": ""})

    # Connect to database and get cursor
    conn, cursor = database.connect_to_db()

    # Check if an artist name was searched,
    # If so, then try to find an associated artist_id
    if artist:
        artist_query = "SELECT id FROM artists WHERE artist_name LIKE '%' || ? || '%'"
        cursor.execute(artist_query, (artist,))
        artist_ids = cursor.fetchall()
        artist_ids = tuple(i[0] for i in artist_ids)

        # SQLITE has a max limit for wildcards at 999
        if len(artist_ids) > 999:
            artist_ids = artist_ids[:998]

    # If only artist searched,
    # Then select songs based on artists
    if artist and not any([lyrics, start_date, end_date]):
        song_query = (
            "SELECT song_name, artist1_id, first_played FROM songs WHERE artist1_id IN ("
            + ",".join("?" * len(artist_ids))
            + ")"
        )

        song_parameters = artist_ids

    # If only lyrics searched,
    # Then select songs based on lyrics
    elif lyrics and not any([artist, start_date, end_date]):
        song_query = """SELECT songs.song_name, artists.artist_name, songs.first_played FROM songs INNER JOIN artists ON songs.artist1_id = artists.ID    
            WHERE lyrics LIKE '%' || ? || '%'"""
        song_parameters = (lyrics,)

    # If only start date set,
    # Then select all songs
    elif start_date and not any([artist, lyrics, end_date]):
        song_query = "SELECT song_name, artist1_id, first_played FROM songs INNER JOIN artists ON songs.artist1_id = artists.ID WHERE first_played > ?"
        song_parameters = (start_date,)

    # If only end date set,
    # Then select all songs
    elif end_date and not any([artist, lyrics, start_date]):
        song_query = "SELECT song_name, artist1_id, first_played FROM songs WHERE first_played < ?"
        song_parameters = (end_date,)

    # If both artist and lyrics searched, but no timerange set
    elif artist and lyrics and not any([start_date, end_date]):
        song_query = (
            """SELECT song_name, artist1_id, first_played FROM songs WHERE lyrics LIKE '%' || ? || '%'
            AND artist1_id IN ("""
            + ",".join("?" * len(artist_ids))
            + ")"
        )

        song_parameters = [lyrics]
        for i in artist_ids:
            song_parameters.append(i)
        song_parameters = tuple(song_parameters)

    # If both artist and start date
    elif artist and start_date and not any([lyrics, end_date]):
        song_query = (
            """SELECT song_name, artist1_id, first_played FROM songs WHERE first_played > ?
            AND artist1_id IN ("""
            + ",".join("?" * len(artist_ids))
            + ")"
        )

        song_parameters = [start_date]
        for i in artist_ids:
            song_parameters.append(i)
        song_parameters = tuple(song_parameters)

    # If both artist and end date
    elif artist and end_date and not any([lyrics, start_date]):
        song_query = (
            """SELECT song_name, artist1_id, first_played FROM songs WHERE first_played < ?
            AND artist1_id IN ("""
            + ",".join("?" * len(artist_ids))
            + ")"
        )

        song_parameters = [end_date]
        for i in artist_ids:
            song_parameters.append(i)
        song_parameters = tuple(song_parameters)

    elif lyrics and start_date and not any([artist, end_date]):
        song_query = """SELECT song_name, artist_id, first_played FROM songs WHERE lyrics LIKE '%' || ? || '%'
            AND first_played > ?"""
        song_parameters = (lyrics, start_date)

    # Execute search and get all results
    cursor.execute(song_query, song_parameters)
    songs = cursor.fetchall()

    # Close database connection and cursor
    database.close_db_cursor_and_conn(conn, cursor)

    return jsonify(
        {
            "html": "<ul>\n{}</ul>".format(
                "\n".join("<li>{}</li>".format(s) for s in songs)
            )
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
