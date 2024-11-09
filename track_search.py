"""
Search for tracks with criterion
"""

import json
import requests as re
from dataclasses import dataclass

from api_connect import get_client_authorizaton_headers

# learn on isrc and use it:
# https://isrc.ifpi.org/en/

# @todo why the hell am i not using dataframe?
@dataclass
class Track:
    id = None
    title = None
    artist = None
    popularity = None
    year = None
    album = None

@dataclass
class SearchCriterion:
    title = None
    artist = None
    year = None
    album = None
    genre = None
    market = None
    isrc = None
    limit = 10
    offset = 0

def search_tracks(q: SearchCriterion):
    query = ""
    if q.title:
        query += ("%20title:"+str(q.title))
    if q.artist:
        query += ("%20artist:"+str(q.artist))
    if q.year:
        query += ("%20year:"+str(q.year))
    if q.title:
        query += ("%20track:"+str(q.title))
    if q.album:
        query += ("%20album:"+str(q.album))
    if q.genre:
        query += ("%20genre:"+str(q.genre))
    if q.isrc:
        query += ("%20isrc:"+str(q.isrc))
    market = "" if q.market is None else ("&market="+q.market)

    url = "https://api.spotify.com/v1/search?q="\
        + query + "&type=track" + market +\
        "&limit="+str(q.limit)+"&offset="+str(q.offset)

    res = re.get(url=url, headers= get_client_authorizaton_headers())
    if res.status_code != 200:
        raise Exception(str(res.status_code) + ": " + str(res.content))

    content = json.loads(res.content)
    # print("content: ", json.dumps(content, indent=4))
    # with open("ressource/itemfound.json", 'w') as f:
    #     json.dump(content, f, indent=4)
    
    jtracks = content["tracks"]
    
    total = jtracks["total"]
    next = jtracks["next"]

    tracks = []
    for item in jtracks["items"]:
        t = Track()
        t.title = item["name"]
        t.artist = str.join("|", [a["name"] for a in item["artists"]])
        t.album= item["album"]["name"]
        t.year = item["album"]["release_date"][:4]
        t.popularity = item["popularity"]
        t.id = item["id"]
        
        tracks.append(t)
    return tracks, total, next

def print_search( tracks, total, next):
    print("total: ", total)
    header = Track
    header.title = "title"
    header.artist = "artist"
    header.album = "album"
    for t in [header] + tracks:
        print("| {:<30} | {:<30} | {:<30} |"\
              .format(t.title[:30], t.artist[:30], t.album[:30]))

# query = SearchCriterion()
# query.title = "love"
# query.artist = "Elton"
# query.album = "Lion"
# query.genre = "Rock"
# query.market = "FR"
# query.year = "1995-2024"
# tracks, total, next = search_tracks(query)  
# print_search(tracks, total, next)