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


def get_tracks(track_ids):
    if len(track_ids) > 50:
        raise Exception("sorry api refuse more than 50 tracks")
    
    url = "https://api.spotify.com/v1/tracks?ids="+ str.join(',', track_ids)

    res = re.get(url, headers=get_user_authorizaton_headers())

    if res.status_code != 200 and res.status_code != 201:
        raise Exception("Failed to add song to playlist, "+ str(res.status_code)+ ": "+ str(res.content))
    
    content = json.loads(res.content)
    return content


def add_songs_to_playlist(track_ids, playlist_id):
    # Max 100 songs per add to playlist request (webapi limitation), 50 for get tracks
    chuncks = list(chunked(track_ids, 50))

    for i, chunk in enumerate(chuncks):
        if len(chunk) != len(get_tracks(chunk)["tracks"]):
            raise Exception("Some song have invalid ids")
        
        uris = ["spotify:track:"+track_id for track_id in chunk]
        
        url = "https://api.spotify.com/v1/playlists/"+playlist_id+"/tracks?uris="\
            + str.join(',', uris)

        # print("url: ", url)
        
        headers=get_user_authorizaton_headers()
        
        res = re.post(url=url, headers=headers, json=None) #, json=body
        
        if res.status_code != 200 and res.status_code != 201:
            raise Exception("Failed to add song to playlist, "+ str(res.status_code)+ ": "+ str(res.content))
    
        print("res: "+ str(res.status_code)+ ": "+ str(res.content))


def create_own_spotify_playlist(name, description, track_ids, public = False):
    me_id = get_me_user_id()
    
    all_user_playlist = get_user_playlist(me_id)

    name_match = [p for p in all_user_playlist if p[1] == name]
    if len(name_match) > 0:
        raise Exception("Playlist with name: %s already exists. %s" % (name, name_match))
    
    
    playlist_id = create_playlist(name, me_id, description, public )
    add_songs_to_playlist(track_ids, playlist_id)

track_ids = [ '1KQc37jezhunxnOPhvdwSG','2IJJszwGK4NWmh3bNK6CPD','4JsDHMv5PVO8N07DbDq33r','3o9kpgkIcffx0iSwxhuNI2','0dS2u2UFd88TIzDDaZDLvS','0IhmRkTZRvHFnYN1lPwyDt','0ifEFzqrvf3J2PIXecVAOJ','2qOmcSjOQEDIJKosonn75a','7H0ya83CMmgFcOhw0UB6ow']
track_ids = ['40XW3d74CGOrWPcNpJDeUi', '5bAQy2e2gMXnx21FbaQKqX', '4erMZWKJDVPko0AQtWD5ZR', '1xe4IvNW94G8R4KCHrLUt6', '0cPa96zXRs2LVuNIqu06oj', '2lujKh60rajud4t0kIcbGh', '18QR3ZWCOhPYNAWNO8qHNz', '0oewwSNqDXhIe6SEOBAtBS', '2puDADzGyxc5mdnMXHhC4e', '5EZVVYOQeGewr58B2TLknH']   
create_own_spotify_playlist("Test playlist 4", "This is an api test", track_ids, False)
get_tracks(track_ids)