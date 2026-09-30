import requests as req
import os
import spotipy
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth

# --------------------- LOAD ENV KEYS --------------------- #
load_dotenv("secrets.env")
CLIENT_ID = str(os.getenv("client_id"))
CLIENT_SECRET = str(os.getenv("client_secret"))
REDIRECT_URI = str(os.getenv("redirect_uri"))
USERNAME = str(os.getenv("username"))

# --------------------- SCRAPING --------------------- #
# date = input("Which year would you like to travel to? Type the date in this format YYYY-MM-DD: ")
date = "2026-04-18"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/152.0.0.0"
                  " Safari/537.36"}
URL = f"{os.getenv("link")}{date}/"
response = req.get(URL, headers=headers)

# --------------------- START THE SOUP --------------------- #
soup = BeautifulSoup(response.text, "html.parser")
song_names_spans = soup.find_all(name="h3", class_="chart-entry__title")
song_names = [song.getText().strip() for song in song_names_spans]

print(song_names[:5])

# --------------------- INITIALIZE SPOTIPY --------------------- #
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        show_dialog=True,
        cache_path="token.txt",
        scope="playlist-modify-private",
    )
)

user_id = sp.current_user()["id"]
print(user_id)

# --------------------- FIND THE URLS --------------------- #
song_uris = []
year = date.split("-")[0]

for song in song_names:

    print(f"\nSearching Spotify for: {song}")
    result = sp.search(q=f"track:{song}", type="track")
    items = result["tracks"]["items"]

    if items:
        uri = items[0]["uri"]
        print(f"URI: {uri}")
        song_uris.append(uri)
    else:
        print(f"{song} doesn't exist in Spotify. Skipped!")

# --------------------- CREATE A PRIVATE PLAYLIST --------------------- #
playlist = sp.current_user_playlist_create(name=f"{year} Billboard 100", public=False)
print(playlist)

# ---------------------ADD SONGS --------------------- #
print(song_uris)
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
