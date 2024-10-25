"""
OAuth to access one's spotify account
"""

import json
import requests as re
# oopsy (-‿-")
import re as regex
import secrets
import base64
import webbrowser
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import os

from api_connect import get_client_authorizaton_headers, get_client_creds, SpotifyTokenRenewer

# @todo find a better way to share this data
CODE_RETRIEVED_TO_SHARE = None
STATE_RETRIEVED_TO_SHARE = None


def get_me_user_id():
    
    url = "https://api.spotify.com/v1/me"
    
    res = re.get(url=url, headers=get_user_authorizaton_headers())
    
    if res.status_code != 200:
        raise Exception("Failed to create playlist, "+ str(res.status_code)+ ": "+ str(res.content))
    
    content = json.loads(res.content)
    id = content["id"]

    return id

"""
Handle redirection callback following OAuth authorization for OAuthLoger server.
Parse to get the token
@see OAuthLoger
"""
class OAuthRedirectHandler(BaseHTTPRequestHandler):  
    # @todo handle denied access
    def do_GET(self):
        global CODE_RETRIEVED_TO_SHARE
        global STATE_RETRIEVED_TO_SHARE
        
        # Parsing the params
        reg_code = r"\/callback\?code=(.*)&state=(.*)"
        found = regex.match(reg_code, self.path)
        if found:
            CODE_RETRIEVED_TO_SHARE = found.group(1)
            STATE_RETRIEVED_TO_SHARE = found.group(2)
        
        # Display success
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Login successful =)</title></head>", "utf-8"))
        self.wfile.write(bytes("<body><p>We gonna have fun.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

"""
Call get_user_credential to open a spotify OAuth authorization page in the browser
which redirect to a localhost server parsing the redirect params to get the 
user token (credential) for interacting with his owned resource.  
@see OAuthRedirectHandler
https://developer.spotify.com/documentation/web-api/tutorials/code-flow
https://datatracker.ietf.org/doc/html/rfc6749
@WARNING do not forget to add the redirect uri ("http://localhost:8000/callback") to your app 
accepted redirect URI in the settings of your app available from "spotify for developers" dashboard 
"""
class OAuthLoger:
    def __init__(self, scope = "playlist-read-private playlist-modify-private playlist-modify-public"):
        self.hostName = "localhost"
        self.hostPort = 8000
        self.scope = scope
        self.server_thread = None
        self.state = None
        
        self.oauth_redirect_server = HTTPServer((self.hostName, self.hostPort), OAuthRedirectHandler)
        # self.oauth_redirect_server.timeout = 1000
        
        if self.hostName != "localhost":
            raise Exception("Implement TLS")
        
        # redirect URI must be registered in the app settings
        self.redirect_uri="http://"+self.hostName+":"+str(self.hostPort)+"/callback"
        
    def _handle_request(self):
        try:
            print(time.asctime(), "Redirect Server Starts - %s:%s" % (self.hostName, self.hostPort))
            self.oauth_redirect_server.handle_request()
        except KeyboardInterrupt:
            pass

    def _start_server(self):
        self.server_thread = threading.Thread(target = self._handle_request, args = ())
        self.server_thread.start()

    def _wait_answer(self, timeout_s = None):
        self.server_thread.join(timeout_s)

        if self.server_thread.is_alive():
            raise Exception("Request timeout")
        
    def _stop_server(self):
        self.oauth_redirect_server.server_close()
        print(time.asctime(), "Redirect Server Stopped - %s:%s" % (self.hostName, self.hostPort))

    def _open_browser_for_authorization(self):        
        client_id, _ = get_client_creds()
        response_type="code"
        self.state = secrets.token_hex(nbytes=16)
        
        OAuthURL = "https://accounts.spotify.com/authorize?" + \
            "&client_id=" + client_id + \
            "&response_type=" + response_type + \
            "&redirect_uri=" + self.redirect_uri + \
            "&state=" + self.state + \
            "&scope=" + self.scope

        webbrowser.open(OAuthURL)

    """
    @param scope, authorization to be granted. 
    https://developer.spotify.com/documentation/web-api/concepts/scopes
    """
    def _request_user_authorization(self):            
        self._start_server()
        self._open_browser_for_authorization()
        self._wait_answer(180)
        # In the meanwhile, OAuthRedirectHandler parsed the code and state
        self._stop_server()

        # @todo clean this global variable mess (share between OAuthLoger & OAuthRedirectionHandler)
        if CODE_RETRIEVED_TO_SHARE is None or STATE_RETRIEVED_TO_SHARE is None:
            raise Exception("Parsing failed?")

        if self.state != STATE_RETRIEVED_TO_SHARE:
            raise Exception("State is not the same. cross-site request forgery? XP")
        
        return CODE_RETRIEVED_TO_SHARE

    def request_an_access_token(self):
        code = self._request_user_authorization()
        
        client_id, client_secret = get_client_creds()
        client_creds_base64 = base64.b64encode(str.encode(client_id + ':' + client_secret))
        client_creds_base64 = client_creds_base64.decode("utf-8")

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            "Authorization": "Basic " + client_creds_base64 
        }

        grant_type = "authorization_code"
        url = "https://accounts.spotify.com/api/token?grant_type=%s&code=%s&redirect_uri=%s" %\
            (grant_type, code, self.redirect_uri)

        res = re.post(url=url,
                headers=headers)
        
        if res.status_code != 200:
            raise Exception("Failed to retrieve token. %s: %s" % (res.status_code, res.content))
        
        token = json.loads(res.content)
        token["scope"] = self.scope
        return token


OAUTH_LOGER = OAuthLoger()
USER_TOKEN_FILE = 'ressource/user_token.json'
USER_TOKEN = SpotifyTokenRenewer(USER_TOKEN_FILE, OAUTH_LOGER.request_an_access_token)

def get_user_authorizaton_headers():
    global USER_TOKEN
    return USER_TOKEN.get_authorization_headers()

# headers_client = get_client_authorizaton_headers()
# headers_user = get_user_authorizaton_headers()

# print("headers_client: ", headers_client)
# print("headers_user: ", headers_user)

# print("user id: ", get_me_user_id())