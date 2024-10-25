"""
Interact with user's playlist
"""

import json
import requests as re
import itertools as it
from more_itertools import chunked

from api_connect import get_client_authorizaton_headers
from user_authentication import get_me_user_id, get_user_authorizaton_headers

def get_user_playlist(user_id):
    url = "https://api.spotify.com/v1/users/"+user_id+"/playlists"
    
    res = re.get(url, headers=get_user_authorizaton_headers())
    if res.status_code != 200:
        print("failed to get_user_playlist. ", res.status_code, ": ", str(res.content))
    
    content = json.loads(res.content)
    playlist = [(playlist["id"], playlist["name"]) for playlist in content["items"]]
    
    return playlist


def create_playlist(name, user_id, description = "", public = False):

    url = "https://api.spotify.com/v1/users/" + user_id + "/playlists"
    
    body = {
        "name": name,
        "description": description,
        "public": public
    }

    headers=get_user_authorizaton_headers()
    headers["Content-Type"] = "application/json"
    
    res = re.post(url=url, headers=headers, json=body)
    
    if res.status_code != 200 and res.status_code != 201:
        raise Exception("Failed to create playlist, "+ str(res.status_code)+ ": "+ str(res.content))
    
    content = json.loads(res.content)
    id = content["id"]

    return id

def add_songs_to_playlist(track_ids, playlist_id):
    # Max 100 songs per request (webapi limitation)
    chuncks = list(chunked(track_ids, 100))

    for i, chunk in enumerate(chuncks):
        url = "https://api.spotify.com/v1/playlists/"+playlist_id+"/tracks"
        
        body = {
            "uris": ["spotify:track:"+track_id for track_id in chunk]
        }
        print("body: ", body)
        
        headers=get_user_authorizaton_headers()
        headers["Content-Type"] = "application/json"
        
        res = re.post(url=url, headers=headers, json=body)
        
        if res.status_code != 200 and res.status_code != 201:
            raise Exception("Failed to add song to playlist, "+ str(res.status_code)+ ": "+ str(res.content))
    
def create_own_spotify_playlist(name, description, track_ids):
    me_id = get_me_user_id()
    
    all_user_playlist = get_user_playlist(me_id)

    name_match = [p for p in all_user_playlist if p[1] == name]
    if len(name_match) > 0:
        raise Exception("Playlist with name: {name} already exists")
    
    playlist_id = create_playlist(name, me_id, description)
    add_songs_to_playlist(track_ids, playlist_id)
    # track_uris = ["spotify:track:" + id for id in track_ids]


track_ids = ["2up3OPMp9Tb4dAKM2erWXQ", "0kbYTNQb4Pb1rPbbaF0pT4"]

create_own_spotify_playlist("Test playlist", "This is an api test", track_ids)
