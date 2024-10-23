import json
import requests as re

from api_connect import get_token

# learn on isrc and use it:
# https://isrc.ifpi.org/en/

market = "" # "&market=FR"
query_year = "1990"
query_song = "lov"
query_artist = "ju"
query = "%20year:"+query_year+"%20track:"+query_song+"%20artist:"+query_artist
url = "https://api.spotify.com/v1/search?q="+ query+ "&type=track"+market+"&limit=10&offset=0"

access_token, token_type = get_token()
headers = {"Authorization": token_type + " " + access_token}

res = re.get(url=url, headers=headers)
print("status: ", res.status_code)
if res.status_code != 200:
    print("res.content", res.content)
else:
    content = json.loads(res.content)
    # print("content: ", json.dumps(content, indent=4))
    with open("ressource/itemfound.json", 'w') as f:
        json.dump(content, f, indent=4)
    
    tracks = content["tracks"]
    
    total = tracks["total"]
    print("total", total)

    for item in tracks["items"]:
        artist_name = ""
        for artist in item["artists"]:
            artist_name += (artist["name"] + " ")
        
        album_release_year = item["album"]["release_date"][:4]
        music_name = item["name"]
        popularity = item["popularity"]
        
        super_name = music_name + " | " + artist_name + " | " + str(popularity) + " | " + album_release_year + " | " + music_name + " | "
        print(super_name)