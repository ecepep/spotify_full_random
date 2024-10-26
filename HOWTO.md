# HOW TO

You must create your own spotify app to be used by this program (client).

## Create a client's app:

- Go on https://developer.spotify.com/
- login with a regular spotify account
- Go on the dashboard: https://developer.spotify.com/dashboard
- "Create app"
- Change created app "Settings" (up right in the app dashboard)
- Copy paste from there the Client ID & Client Secret to the file "confidential_spotify_webapi.json" @todo clean this up
- In the settings, add "http://localhost:8000/callback" to the "redirect uris".
