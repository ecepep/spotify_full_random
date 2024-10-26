# spotify_full_random

Tired of AI generated playlist just offering you to listen to the same songs
again and again?  
Tired of spotify curated playlist pushing for the songs of the industry?  
This is the true hipster playlist, a shuffle of the whole spotify! (at least, in theory)  

AKA: Can a random estimator beat spotify AI at "what should be the next song"?  
the metric: my own appreciation XP

## Content

<ins>api_connect.py</ins>: Retrieve & renew client token  
<ins>user_authentication.py</ins>: Implements OAuth to fetch user token (interact with my own account)   
<ins>simple_strategy.py</ins>: Simple strategy trying to list spotify songs randomly.  
<ins>track_search.py</ins>: Search for spotify track with criterion.    
<ins>screate_spotify_playlist.py</ins>: Create a spotify playlist on your user with the specified songs. (yet, broken)

## Note on the Search limitation

- max songs per search: 100,
- search answers are not random (push forward famous songs),
- the search endpoint prevent database scrapping,
- there is a limit rate for querying the database,
- the api specify ("we don't want people training AI with it"), 
I don't want my personnal account to be banned because I launched too many queries.

## Strategies as workaround

- do concessions on the randomness of the algorithm.
- use dictionnaries from every languages and combine it with some search
    - weight likelihood of a song to be selected with the total number of song 
    resp in a search. 
    - Do sub search until the total of resp song is < 100.
    - Dictionnaries could be in the first place just alphabets.
    - Store all result in a local sqlite DB
    - Get to know better the API
    - use ISRC
- Use a third party database for songs which is more transparent (like musicbrainz)
to pick some random songs from there and then search them in spotify.