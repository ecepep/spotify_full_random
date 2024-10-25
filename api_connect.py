"""
https://developer.spotify.com/documentation/web-api/tutorials/getting-started
Fetch a valid client token for requesting spotify web api's
"""

import requests as re
import json
import os.path
import datetime

"""
Handle spotify token renewal before expiration and persistency (save/load to/from file)
"""
class SpotifyTokenRenewer:
    def __init__(self, dump_filename, request_token_callback):
        self.dump_filename = dump_filename
        self.request_token_callback = request_token_callback
        self.token = None
    
    def renew_token(self):
        spotify_token = self.request_token_callback()
        if spotify_token is None or\
            not all([key in spotify_token for key in ["expires_in","access_token","token_type"]]):
            raise Exception("request_token_callback do not return a spotify token dict.")
        
        expiration_delta = datetime.timedelta(seconds=int(spotify_token["expires_in"]))
        expiration = datetime.datetime.now() + expiration_delta
        spotify_token["expiration"] = expiration.isoformat()

        # \todo mksubdir
        with open(self.dump_filename, 'w') as f:
            json.dump(spotify_token, f)

        return spotify_token

    def get_token(self):
        if self.token is None and os.path.isfile(self.dump_filename):
            with open(self.dump_filename, 'r') as f:
                self.token = json.load(f)
        elif self.token is None:
            self.token = self.renew_token()

        expiration = datetime.datetime.fromisoformat(self.token["expiration"])
        expiration_delta = datetime.timedelta(seconds=int(self.token["expires_in"]))

        # Renew token before expiration
        if expiration - datetime.datetime.now() < (expiration_delta*0.75):
            self.token = self.renew_token()

        access_token = self.token["access_token"]
        token_type = self.token["token_type"]
        
        return access_token, token_type, expiration
    
    def get_authorization_headers(self):
        access_token, token_type, _ = self.get_token()
        headers = {"Authorization": token_type + " " + access_token}
        return headers



# Client id & secret to be found in the "setting" of your app dashboard
def get_client_creds():
    confidential = "../confidential_spotify_webapi.json"
    with open(confidential) as f:
        creds = json.load(f)
        # print(creds)

    client_id = creds["client_id"]
    client_secret = creds["client_secret"]

    return client_id, client_secret

def request_client_token():
    client_id, client_secret = get_client_creds()
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    data = "grant_type=client_credentials"+\
            "&client_id="+client_id+\
            "&client_secret="+client_secret

    res = re.post("https://accounts.spotify.com/api/token",
            headers=headers,
            data=data)
    
    if (res.status_code != 200):
        print("Token request failed: ", res.status_code)
        raise Exception("Token request failed")

    content = res.content
    content = json.loads(content)

    return content
    
CLIENT_TOKEN_FILE = 'ressource/client_token.json'
CLIENT_TOKEN = SpotifyTokenRenewer(CLIENT_TOKEN_FILE, request_client_token)

def get_client_authorizaton_headers():
    global CLIENT_TOKEN
    return CLIENT_TOKEN.get_authorization_headers()