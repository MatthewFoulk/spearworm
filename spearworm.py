
import spotipy
import spotipy.util as util
import sys
import os
import lyricsgenius

from datetime import datetime

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
        


def main():

    # username = input("Please enter your Spotify username: ")
    username = "mewuzhere"

    print("Connecting to Spotify...")
    sp =connect_to_spotify(username)

    print("Retrieving {username}'s recently played...".format(username=username))
    recently_played = get_recently_played(sp)

    print("Fetching song lyrics...")
    recently_played_w_lyrics = get_genius_lyrics(recently_played)

    print(recently_played_w_lyrics)

if __name__ == "__main__":
    main()