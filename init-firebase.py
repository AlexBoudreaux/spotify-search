import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firestore():
    # Initialize Firebase Admin SDK
    cred = credentials.Certificate("spotify-db-firebase-admin-creds.json")
    firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    # Define collections
    collections = ['artists', 'albums', 'playlists', 'playlist_artists']
    
    for collection in collections:
        # Create a placeholder document to initialize the collection
        doc_ref = db.collection(collection).document('init_doc')
        doc_ref.set({"initialized": True})
        print(f"Initialized collection: {collection}")

    print("Firestore initialization complete.")

if __name__ == "__main__":
    initialize_firestore()
