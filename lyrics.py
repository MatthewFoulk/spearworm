
import os
import sys
import time

import lyricsgenius


def get_genius_lyrics(song_name, artist_name):

    # Connect to genius API
    genius = lyricsgenius.Genius(os.environ.get("GENIUS_CLIENT_ACCESS_TOKEN"))

    # Essentially print less information, do the inverse if you want more info
    genius.verbose = False
    genius.remove_section_headers = True

    attempts = 0

    while attempts < 2:
        try:
            # Search for song lyrics
            genius_search = genius.search_song(song_name, artist_name)

            # Break outside while loop
            attempts = 2

        except:
            attempts += 1

            if attempts < 2:
                print("Wait 5 minutes before searching again")
                time.sleep(5*60)
            else:
                print("Error getting lyrics for %s by %s" % (song_name, artist_name))
                sys.exit()

    # Wait to avoid timeout from API
    time.sleep(1)

    # Return the lyrics if found, otherwise return blank string
    return genius_search.lyrics if genius_search else ""
