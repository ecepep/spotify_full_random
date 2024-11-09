"""
This new attempt use an open data thirdparty database to generate random list without limitations
and then try to find those songs in spotify

@note having some issue with spotify not fetching the desired artist|song even when it has it.
artist: Break => spotify output Breaking Benjamin
song: may not be able to find it if something is added like "- single version"

Firstly trying out discogs & maybe musicbrainz.
https://www.discogs.com/developers
https://musicbrainz.org/

alt.
The internet archives
Too exhaustiv?
https://archive.org

alt.
Music modernization act
God bless the US of A for transparency though i don't got 100 dolls/month for my own fun.
https://www.themlc.com/dataprograms

alt.
It seems there ain't no such thing as a free lunch
https://soundcharts.com/pricing

alt.
Money rules the world
https://jaxsta.com/subscriptions
"""

import time
from genre import genres
import random
import string
import pandas as pd

from discogs import get_discogs_song
from create_spotify_playlist import create_own_spotify_playlist
from track_search import SearchCriterion, Track, search_tracks, print_search
from sqlite_connector import SqlDB
from workaround import pih

DB = SqlDB("open_data_strategy")

i = 0
playlist_size = 100
tracks_id = []

while len(tracks_id) < playlist_size and i < playlist_size*2:
    i+=1

    try:
        # Discogs seems to be very biased toward occidental music
        random_id = random.randint(1, 32000000)
        print('random id {:,}'.format(random_id))
        titles, release_name, year, artists = get_discogs_song(random_id)

        is_various = artists[0] == "Various"

        # @note spotify search for artist may be not strict enough to my taste but too lazy to make a custom filter
        query = SearchCriterion()
        # query.title = random.choice(titles)
        query.artist = None if is_various else artists[0]
        query.album = release_name if query.artist == None else None
        query.year = str(year) if year > 0 else None
        query.limit = 10
        # print("titles: ", titles, "  release: ", release_name, " year:", year, " artists:", artists[0])
        print("query: t: ", query.title, "  a: ", query.artist, " y: ", query.year, "  r: ", release_name)
        tracks, total, next = search_tracks(query)  
        print_search(tracks, total, next)

        DB.add_search(tracks, query, total)

        track = random.choice(tracks)
        tracks_id.append(track.id)
    except Exception as e:
        print("failed", e)
    pih([])

name = "discogs strategy"
description = "A random selection of discogs.com songs."
create_own_spotify_playlist(name, description, tracks_id, False)