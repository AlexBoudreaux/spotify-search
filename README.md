# 🎵 Spotify Data to Firebase Saver 🎵

## Description

This script fetches your Spotify data (followed artists, saved albums, and playlists) and stores it in a Firebase database. It's perfect for backing up your Spotify data or integrating it with other services.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How it Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

- Python 3.7+
- A Spotify Developer account
- A Firebase project

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/spotify-data-to-firebase.git
   cd spotify-data-to-firebase
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Spotify API Setup:
   - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Create a new app and note down the Client ID and Client Secret
   - Add `http://localhost:8888/callback` to the Redirect URIs in your app settings

2. Firebase Setup:
   - Go to the [Firebase Console](https://console.firebase.google.com/)
   - Create a new project (or use an existing one)
   - In Project Settings > Service Accounts, generate a new private key
   - Save the JSON file as `spotify-db-firebase-admin-creds.json` in the project root

3. Environment Variables:
   - Copy the `.env.sample` file to `.env`:
     ```bash
     cp .env.sample .env
     ```
   - Edit `.env` and fill in your Spotify and Firebase credentials

4. (Optional) Initialize Firebase Collections:
   - To test your Firebase connection and initialize the collections, run:
     ```bash
     python init-firebase.py
     ```
   - This step is optional but recommended, especially if you're setting up the project for the first time. It will create the necessary collections in your Firebase database.

## Usage

### Running as a standalone script

1. Ensure your virtual environment is activated
2. Run the script:
   ```bash
   python populate-firebase.py
   ```

### Using the function in another file

If you want to use the main function in another Python file:

1. Import the function in your Python script:
   ```python
   from populate-firebase import fetch_and_save_spotify_data_to_firebase
   ```

2. Call the function:
   ```python
   fetch_and_save_spotify_data_to_firebase()
   ```

## How it Works

1. The script initializes connections to Spotify API and Firebase
2. It fetches your followed artists, saved albums, and playlists from Spotify
3. The data is then structured and saved into Firebase collections
4. After saving, it displays the contents of the Firebase database

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.