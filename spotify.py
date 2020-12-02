import glob
import json
import sys
from datetime import datetime

import spotipy
import spotipy.util as util

import database


def connect_to_spotify(username):
    token = util.prompt_for_user_token(username, scope="user-read-recently-played")

    if token:
        return spotipy.Spotify(auth=token)
    else:
        sys.exit("Failed to connect to Spotify")


def get_recently_played(sp):

    # Get recernly played songs in JSON format form Spotify
    recently_played_json = sp.current_user_recently_played()
    # Initialize list for recently played data
    recently_played = []

    # Iterate over the recently played tracks and add them to track_dict
    # then append track to recently played list
    for item in recently_played_json["items"]:

        track = {}
        track["song_name"] = item["track"]["name"]

        track["artist_names"] = []
        for artist in item["track"]["artists"]:
            track["artist_names"].append(artist["name"])

        try:
            track["played_at"] = datetime.strptime(
                item["played_at"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        except:
            track["played_at"] = datetime.strptime(
                item["played_at"], "%Y-%m-%dT%H:%M:%SZ"
            )

        recently_played.append(track)

    # Reverse so added to db in order from when it was played
    recently_played.reverse()

    return recently_played


def get_streaming_history():

    # Iterate over each streaminghistory file
    streaming_data = []
    for file_name in glob.glob("MyData/StreamingHistory*.json"):
        with open(file_name, encoding="utf-8") as f:
            streaming_data.append(json.load(f))

    return streaming_data


if __name__ == "__main__":
    get_streaming_history()
