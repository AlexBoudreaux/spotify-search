import os
from datetime import datetime
from dotenv import load_dotenv
from collections import Counter

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from supabase_py import create_client, Client


# Load environment variables
load_dotenv(".env.local")

# Initialize Spotipy and Supabase clients
sp = Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                                       client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                                       redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
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
            playlist_id = item['id']
            playlist_tracks = sp.playlist_tracks(playlist_id, fields='items(track(artists(id,name)))')
            
            # Collect artists
            all_artists = []
            for track_item in playlist_tracks['items']:
                track_artists = track_item['track']['artists']
                for artist in track_artists:
                    all_artists.append((artist['id'], artist['name']))
            
            # Find 8 most featured artists
            counter = Counter(all_artists)
            most_common_artists = counter.most_common(8)
            most_common_artists = [artist[0] for artist in most_common_artists]
            
            playlist = {
                'spotify_id': item['id'],
                'name': item['name'],
                'cover_image_url': item['images'][0]['url'] if item['images'] else None,
                'artists': most_common_artists
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