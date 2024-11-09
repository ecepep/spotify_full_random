"""
Intend to provide an [almost] random sub-sample of all spotify's songs (to make a small random playlist) 

simple strategy: The "mr good enough" strategy, just search with random title (2 latin-letters) µor year and random genre, so that it feels random
@todo add other alphabets

Observation:
- If genre criteria is there, title must be exact (full) ==> rather select with years
- The api do not like partial search
- I need dictionnaries
Conclusion:
- This will never be random though it is fun to have spotify own selection for each genre
- Use another database for random selection -> spotify search is too biased...
- @todo take a look at spotify recommandation 
"""
import time
from genre import genres
import random
import string
import pandas as pd

from create_spotify_playlist import create_own_spotify_playlist
from track_search import SearchCriterion, Track, search_tracks, print_search
from sqlite_connector import SqlDB
from workaround import pih

"""
@todo
study distribution of the different criterion (how to obtain unbiased dataset???)
- year
- alphabets (spotify search result is not random)
- genre...

@warning the love elton john search add unexpected result when adding the album name criterion (removing too many entries)
"""

DB = SqlDB("simple_strategy")


def create_dataset():
    global DB
    letters = str.lower(string.ascii_letters)

    subgenre = random.sample(genres, 100)
    for g in subgenre:
        print("-----------------------------------------------------------------")
        # rand_title not working => spotify prevent exhaustiv search kind of thing
        rand_title = "".join(random.sample(letters,3))
        
        query = SearchCriterion()
        query.title = None #None#rand_title #rand_title# "love"
        query.artist = None #"Elton"
        query.album = None #"Lion"
        query.genre = g#"Breakbeat" #g
        query.market = "FR"
        
        # @todo make a cleaner year window selection skewed for newer and with wider window if older 
        year = random.randint(1945,2024)
        search_window = max(0, (2025-year)-random.randint(0,30))
        search_window = random.randint(int(search_window*0.50),search_window)  
        query.year =  str(year)+"-"+str(year+search_window)

        query.offset = 0 #random.randint(0,4)
        query.limit = 50

        print("q => t: ", query.title, "y: ", query.year, "  g: ", query.genre)
        
        tracks, total, next = search_tracks(query)  
        
        print("total: ", total)
        # print_search(tracks, total, next)
        # print("total: ", total)
        DB.add_search(tracks, query, total)

        # break
        tracks_id = [t.id for t in tracks]
        pih(tracks_id)

# @todo cleanup
from df_GUI import print_df_in_browser
def select_in_dataset():
    global DB
    
    where = None
    # where = " title like \"%love%\""
    
    tracks = DB.get_tracks_df(where)
    print("tracks cnt: \n", tracks.shape[0])
    print("tracks.columns: ", tracks.columns)
    tracks[["title", "artist", "album"]] = tracks[["title", "artist", "album"]].map(str.lower)
    tracks["artist"] = tracks["artist"].apply(lambda x: x.split("%7")[0])

    distinct = tracks.sort_values("artist").groupby(["artist"]).first()
    print("tracks distinct artist cnt: \n", distinct.shape[0])
    distinct = distinct.sort_values("album").groupby(["album"]).first()
    print("tracks distinct album cnt: \n", distinct.shape[0])
    print_df_in_browser(distinct)

    tracks_id = list(distinct["spotify_id"])
    tracks_id = random.sample(tracks_id, 100)

    # print(tracks_id)
    return tracks_id


if __name__ == "__main__":   
    # @todo it seems like token renewal is too systematic. Error in datetime??
    tracks_id = select_in_dataset()
    name = "Simple strategy (genre, year)"
    description = "This playlist is generated from many semi random search on genre and year to feel random and exhaustiv, it ain't."
    create_own_spotify_playlist(name, description, tracks_id, False)