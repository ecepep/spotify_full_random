"""
Trying out discogs: https://www.discogs.com/developers
@note: there are some community maintained client to the discogs' api:
https://github.com/joalla/discogs_client

@note Discogs seems very biased toward occidental music
@note out of the 30 million random release, i managed to pick elton john, am i just lucky (possibly)?
@note Seems to be lacking the most obscure artists. Not exhaustiv enough?

an easy deep dive into all music of discogs
#https://www.discogs.com/developers#page:database,header:database-release
#/releases/{release_id}{?curr_abbr}

#https://www.discogs.com/developers#page:database,header:database-search
#/database/search?q={query}&{?
"""

import requests as re
import json
import random
import time

# request token
# GET https://api.discogs.com/oauth/request_token

# access token
# post /oauth/access_token

DISCOGS = "https://api.discogs.com/"

def search_max_id():
    failed_cnt = 100
    # Release id from discogs seems to be somewhat continuous. From a manual dichotomic search:
    min_id = 31001425
    max_id = 36000000

    i = 0
    while i < failed_cnt:
        time.sleep(2)
        print('current min id {:,}'.format(min_id))
        random_id = random.randint(min_id, max_id)
        print('random id {:,}'.format(random_id))
        try:
            titles,release_name, year, artists = get_discogs_song(random_id)
        except Exception as e:
            i+=1
            continue
        
        i = 0
        min_id = random_id
        print(artists[0], " ", year, " ", titles[0])


def get_discogs_song(random_id):
    url = DISCOGS + "/releases/" +  str(random_id)
    res = re.get(url)
    print(url)

    if res.status_code != 200:
        print(res.status_code)
        print(res.content)
    jcont = json.loads(res.content)

    # with open("ressource/temp.json", "w") as f:
    #     json.dump(jcont,f, indent=4)

    # artists = jcont["artists_sort"]
    artists = [a["name"] for a in jcont["artists"]]
    release_name  = jcont["title"] # aka album
    year = jcont["year"]
    titles = [s["title"] for s in jcont["tracklist"]]
    # @note discogs has its own "popularity" factor which is probably less bias than spotify's
    # we could use it instead.

    return titles,release_name, year, artists

if __name__ == "__main__":   
    # titles, release_name, year, artists = get_random_discogs_song()
    # print(artists)
    # print(release_name)
    # print(year)
    # print(titles)
    search_max_id()