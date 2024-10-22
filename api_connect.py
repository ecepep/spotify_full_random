### https://developer.spotify.com/documentation/web-api/tutorials/getting-started
### Fetch a valid token for requesting spotify web api

import requests as re
import json
import os.path
import datetime

TOKEN = None
TOKEN_FILE = 'ressource/token.json'

# Client id & secret to be found in the "setting" of your app dashboard
def get_client_creds():
    confidential = "../confidential_spotify_webapi.json"
    with open(confidential) as f:
        creds = json.load(f)
        # print(creds)

    client_id = creds["client_id"]
    client_secret = creds["client_secret"]

    return client_id, client_secret

def request_token():
    client_id, client_secret = get_client_creds()
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    data = "grant_type=client_credentials"+\
            "&client_id="+client_id+\
            "&client_secret="+client_secret

    res = re.post("https://accounts.spotify.com/api/token",
            headers=headers,
            data=data)
    
    if (res.status_code == 200):
        print("Succesfully fetched token")
    else:
        print("Token request failed: ", res.status_code)
        raise Exception("Token request failed")

    content = res.content
    content = json.loads(content)
    
    expiration_delta = datetime.timedelta(seconds=int(content["expires_in"]))
    expiration = datetime.datetime.now() + expiration_delta
    content["expiration"] = expiration.isoformat()

    # \todo mksubdir
    with open(TOKEN_FILE, 'w') as f:
        json.dump(content, f)

    return content

def get_creds():
    global TOKEN, TOKEN_FILE

    if TOKEN is None and os.path.isfile(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            TOKEN = json.load(f)
    elif TOKEN is None:
        TOKEN = request_token()

    expiration = datetime.datetime.fromisoformat(TOKEN["expiration"])
    expiration_delta = datetime.timedelta(seconds=int(TOKEN["expires_in"]))

    if expiration - datetime.datetime.now() < (expiration_delta*0.75):
        TOKEN = request_token()

    access_token = TOKEN["access_token"]
    token_type = TOKEN["token_type"]
    
    print("Renewing token")
    print("access_token", access_token)
    print("token_type", token_type)

    return access_token, token_type

get_creds()
# testload()