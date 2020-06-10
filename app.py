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

    # If nothing searched, return blank html
    if not artist and not lyrics:
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

    # If artist searched, and no lyrics searched,
    # Then select songs based on artists
    if artist and not lyrics:

        # Add wildcard placeholder for the number of ids in artist_ids
        song_by_artist_query = (
            "SELECT song_name, artist1_id, first_played FROM songs WHERE artist1_id IN ("
            + ",".join("?" * len(artist_ids))
            + ")"
        )
        cursor.execute(song_by_artist_query, artist_ids)
        songs = cursor.fetchall()

    # If artist not searched and lyrics searched,
    # Then select songs based on lyrics
    elif not artist and lyrics:
        song_by_lyrics_query = "SELECT song_name, artist1_id, first_played FROM songs WHERE lyrics LIKE '%' || ? || '%'"
        cursor.execute(song_by_lyrics_query, (lyrics,))
        songs = cursor.fetchall()

    elif artist and lyrics:
        song_by_artist_lyrics_query = (
            """SELECT song_name, artist1_id, first_played FROM songs WHERE lyrics LIKE '%' || ? || '%'
            AND artist1_id IN ("""
            + ",".join("?" * len(artist_ids))
            + ")"
        )

        query_parameters = [lyrics]
        for i in artist_ids:
            query_parameters.append(i)
        query_parameters = tuple(query_parameters)

        cursor.execute(song_by_artist_lyrics_query, (query_parameters))
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
