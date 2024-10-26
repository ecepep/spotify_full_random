"""
Intend to provide an [almost] random sub-sample of all spotify's songs (to make a small random playlist) 

simple strategy: The "mr good enough" strategy, just search with random title (2 latin-letters) and random genre, so that it feels random
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
from track_search import SearchCriterion, Track, search_tracks, print_search
from sqlite_connector import SqlDB
from workaround import pih

"""
@todo
study distribution of the different criterion
- year
- alphabets (spotify search result is not random)
- genre...

@warning the love elton john search add unexpected result when adding the album name criterion (removing too many entries)
"""

db = SqlDB("simple_strategy")

letters = str.lower(string.ascii_letters)



subgenre = random.sample(genres, 97)
for g in subgenre:
    print("-----------------------------------------------------------------")
    rand_title = "".join(random.sample(letters,3))
    
    query = SearchCriterion()
    query.title = None #None#rand_title #rand_title# "love"
    query.artist = None #"Elton"
    query.album = None #"Lion"
    query.genre = g#"Breakbeat" #g
    query.market = "FR"
    
    # @todo make a cleaner year window selection skewed for newer and with wider window if older 
    year = random.randint(1880,2024)
    search_window = max(0, (2025-year)-random.randint(0,70))
    search_window = random.randint(int(search_window*0.50),search_window)  
    query.year =  str(year)+"-"+str(year+search_window)

    query.offset = 0 #random.randint(0,4)
    query.limit = 50

    print("q => t: ", query.title, "y: ", query.year, "  g: ", query.genre)
    
    tracks, total, next = search_tracks(query)  
    
    print("total: ", total)
    # print_search(tracks, total, next)
    # print("total: ", total)
    db.add_search(tracks, query, total)

    # break
    tracks_id = [t.id for t in tracks]
    pih(tracks_id)