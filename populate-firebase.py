import os
from datetime import datetime
from dotenv import load_dotenv
from collections import Counter

from spotipy import Spotify, SpotifyException
from spotipy.oauth2 import SpotifyOAuth
import firebase_admin
from firebase_admin import credentials, firestore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_spotify_and_firebase():
    # Load environment variables
    load_dotenv(".env")

    # Initialize Firebase Admin SDK
    try:
        cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        logger.info("Initialized Firebase Admin SDK.")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
        return None, None

    # Initialize Spotipy with updated scopes
    try:
        sp = Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
            scope="user-library-read playlist-read-private user-follow-read"
        ))
        logger.info("Initialized Spotipy.")
    except Exception as e:
        logger.error(f"Failed to initialize Spotipy: {e}")
        return None, None

    return sp, db

def get_followed_artists(sp):
    artists = []
    try:
        results = sp.current_user_followed_artists(limit=50)
        while True:
            for item in results['artists']['items']:
                artist = {
                    'spotify_id': item['id'],
                    'name': item['name'],
                    'cover_image_url': item['images'][0]['url'] if item['images'] else None,
                    'created_at': datetime.utcnow()
                }
                artists.append(artist)
            
            if results['artists'].get('next'):
                results = sp.next(results['artists'])
            else:
                break
    except SpotifyException as e:
        logger.error(f"Spotify API error while fetching followed artists: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching followed artists: {e}")
    return artists

def get_saved_albums(sp):
    albums = []
    try:
        results = sp.current_user_saved_albums(limit=50)
        while True:
            for item in results['items']:
                album = {
                    'spotify_id': item['album']['id'],
                    'name': item['album']['name'],
                    'artist': item['album']['artists'][0]['name'],
                    'artist_spotify_id': item['album']['artists'][0]['id'],
                    'cover_image_url': item['album']['images'][0]['url'] if item['album']['images'] else None,
                    'created_at': datetime.utcnow()
                }
                albums.append(album)
            
            if results.get('next'):
                results = sp.next(results)
            else:
                break
    except SpotifyException as e:
        logger.error(f"Spotify API error while fetching saved albums: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching saved albums: {e}")
    return albums

def get_playlists(sp):
    playlists = []
    try:
        results = sp.current_user_playlists(limit=50)
        while True:
            for item in results['items']:
                playlist_id = item['id']
                try:
                    playlist_tracks = sp.playlist_tracks(
                        playlist_id,
                        fields='next, items(track(artists(id,name)))',
                        limit=100
                    )
                except SpotifyException as e:
                    logger.error(f"Spotify API error while fetching tracks for playlist {playlist_id}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error while fetching tracks for playlist {playlist_id}: {e}")
                    continue

                all_artists = []
                while True:
                    for track_item in playlist_tracks['items']:
                        if track_item['track'] is None:
                            continue
                        track_artists = track_item['track']['artists']
                        for artist in track_artists:
                            all_artists.append((artist['id'], artist['name']))
                    
                    if playlist_tracks.get('next'):
                        try:
                            playlist_tracks = sp.next(playlist_tracks)
                        except SpotifyException as e:
                            logger.error(f"Spotify API error while paginating tracks for playlist {playlist_id}: {e}")
                            break
                        except Exception as e:
                            logger.error(f"Unexpected error while paginating tracks for playlist {playlist_id}: {e}")
                            break
                    else:
                        break

                counter = Counter(all_artists)
                most_common_artists = counter.most_common(8)
                most_common_artists = [
                    {'spotify_id': artist_tuple[0][0], 'name': artist_tuple[0][1], 'count': artist_tuple[1]}
                    for artist_tuple in most_common_artists
                ]

                playlist = {
                    'spotify_id': item['id'],
                    'name': item['name'],
                    'cover_image_url': item['images'][0]['url'] if item['images'] else None,
                    'artists': most_common_artists,
                    'created_at': datetime.utcnow()
                }
                playlists.append(playlist)

            if results.get('next'):
                try:
                    results = sp.next(results)
                except SpotifyException as e:
                    logger.error(f"Spotify API error while paginating playlists: {e}")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error while paginating playlists: {e}")
                    break
            else:
                break
    except SpotifyException as e:
        logger.error(f"Spotify API error while fetching playlists: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while fetching playlists: {e}")
    return playlists

def save_artists_to_firestore(db, artists):
    for artist in artists:
        try:
            doc_ref = db.collection('artists').document(artist['spotify_id'])
            doc_ref.set({
                'name': artist['name'],
                'cover_image_url': artist['cover_image_url'],
                'created_at': artist['created_at']
            }, merge=True)
        except Exception as e:
            logger.error(f"Error saving artist {artist['spotify_id']} to Firestore: {e}")
    logger.info(f"Saved {len(artists)} artists to Firestore.")

def save_albums_to_firestore(db, albums):
    for album in albums:
        try:
            doc_ref = db.collection('albums').document(album['spotify_id'])
            doc_ref.set({
                'name': album['name'],
                'artist': album['artist'],
                'artist_spotify_id': album['artist_spotify_id'],
                'cover_image_url': album['cover_image_url'],
                'created_at': album['created_at']
            }, merge=True)
        except Exception as e:
            logger.error(f"Error saving album {album['spotify_id']} to Firestore: {e}")
    logger.info(f"Saved {len(albums)} albums to Firestore.")

def save_playlists_to_firestore(db, playlists):
    for playlist in playlists:
        try:
            doc_ref = db.collection('playlists').document(playlist['spotify_id'])
            doc_ref.set({
                'name': playlist['name'],
                'cover_image_url': playlist['cover_image_url'],
                'created_at': playlist['created_at']
            }, merge=True)
            
            playlist_artists_ref = doc_ref.collection('playlist_artists')
            
            for artist in playlist['artists']:
                try:
                    artist_doc_ref = playlist_artists_ref.document(artist['spotify_id'])
                    artist_doc_ref.set({
                        'name': artist['name'],
                        'count': artist['count']
                    }, merge=True)
                except Exception as e:
                    logger.error(f"Error saving artist {artist['spotify_id']} to playlist_artists in Firestore: {e}")
        except Exception as e:
            logger.error(f"Error saving playlist {playlist['spotify_id']} to Firestore: {e}")
    logger.info(f"Saved {len(playlists)} playlists to Firestore.")

def show_firestore_contents(db):
    collections = ['artists', 'albums', 'playlists']
    for collection in collections:
        try:
            logger.info(f"\nContents of {collection}:")
            docs = db.collection(collection).stream()
            for doc in docs:
                logger.info(f"{doc.id} => {doc.to_dict()}")
        except Exception as e:
            logger.error(f"Error retrieving collection {collection}: {e}")
    
    try:
        logger.info("\nContents of playlist_artists:")
        playlists = db.collection('playlists').stream()
        for playlist in playlists:
            playlist_data = playlist.to_dict()
            logger.info(f"\nPlaylist ID: {playlist.id}, Name: {playlist_data.get('name')}")
            try:
                playlist_artists = playlist.reference.collection('playlist_artists').stream()
                for artist in playlist_artists:
                    logger.info(f"  Artist ID: {artist.id} => {artist.to_dict()}")
            except Exception as e:
                logger.error(f"Error retrieving playlist_artists for playlist {playlist.id}: {e}")
    except Exception as e:
        logger.error(f"Error retrieving playlists for playlist_artists: {e}")

def fetch_and_save_spotify_data_to_firebase():
    sp, db = initialize_spotify_and_firebase()
    if not sp or not db:
        logger.error("Failed to initialize Spotify or Firebase. Exiting.")
        return

    logger.info("Fetching followed artists...")
    artists = get_followed_artists(sp)
    logger.info(f"Retrieved {len(artists)} artists.")
    
    logger.info("Fetching saved albums...")
    albums = get_saved_albums(sp)
    logger.info(f"Retrieved {len(albums)} albums.")
    
    logger.info("Fetching playlists...")
    playlists = get_playlists(sp)
    logger.info(f"Retrieved {len(playlists)} playlists.")
    
    logger.info("Saving artists to Firestore...")
    save_artists_to_firestore(db, artists)
    
    logger.info("Saving albums to Firestore...")
    save_albums_to_firestore(db, albums)
    
    logger.info("Saving playlists to Firestore...")
    save_playlists_to_firestore(db, playlists)
    
    logger.info("Displaying Firestore contents...")
    show_firestore_contents(db)

if __name__ == "__main__":
    fetch_and_save_spotify_data_to_firebase()