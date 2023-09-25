# Import statements
import os
from datetime import datetime
from dotenv import load_dotenv

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from supabase_py import create_client, Client


# Load environment variables
load_dotenv(".env.local")

# Initialize Spotipy and Supabase clients
sp = Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                                       client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                                       redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
                                       scope="user-library-read"))

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Function to get followed artists
def get_followed_artists():
    artists = []
    results = sp.current_user_followed_artists(limit=50)
    
    while True:
        for item in results['artists']['items']:
            artist = {
                'spotify_id': item['id'],
                'name': item['name'],
                'cover_image_url': item['images'][0]['url'] if item['images'] else None
            }
            artists.append(artist)
        
        if results['artists']['next']:
            results = sp.next(results['artists'])
        else:
            break
    
    return artists

# Function to get saved albums
def get_saved_albums():
    albums = []
    results = sp.current_user_saved_albums(limit=50)
    
    while True:
        for item in results['items']:
            album = {
                'spotify_id': item['album']['id'],
                'name': item['album']['name'],
                'artist': item['album']['artists'][0]['name'],
                'artist_spotify_id': item['album']['artists'][0]['id'],
                'cover_image_url': item['album']['images'][0]['url'] if item['album']['images'] else None
            }
            albums.append(album)
        
        if results['next']:
            results = sp.next(results)
        else:
            break
    
    return albums

# Function to get playlists
def get_playlists():
    playlists = []
    results = sp.current_user_playlists(limit=50)
    
    while True:
        for item in results['items']:
            playlist = {
                'spotify_id': item['id'],
                'name': item['name'],
                'cover_image_url': item['images'][0]['url'] if item['images'] else None
            }
            playlists.append(playlist)
        
        if results['next']:
            results = sp.next(results)
        else:
            break
    
    return playlists

# Function to save followed artists to Supabase
def save_artists_to_supabase(artists):
    for artist in artists:
        artist['created_at'] = datetime.now().isoformat()
        supabase.table("artists").insert([artist], upsert=True).execute()

# Function to save saved albums to Supabase
def save_albums_to_supabase(albums):
    for album in albums:
        album['created_at'] = datetime.now().isoformat()
        supabase.table("albums").insert([album], upsert=True).execute()

# Function to save playlists to Supabase
def save_playlists_to_supabase(playlists):
    for playlist in playlists:
        playlist['created_at'] = datetime.now().isoformat()
        supabase.table("playlists").insert([playlist], upsert=True).execute()

def main():
    # Fetch Spotify data
    artists = get_followed_artists()
    albums = get_saved_albums()
    playlists = get_playlists()

    # Save data to Supabase
    save_artists_to_supabase(artists)
    save_albums_to_supabase(albums)
    save_playlists_to_supabase(playlists)

if __name__ == "__main__":
    main()