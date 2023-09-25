# 🎵 Spotify Data Saver 🎵

## Description

This script fetches your favorite Spotify artists, albums, and playlists and stores them into a Supabase database. Perfect for those who want to keep a backup or integrate Spotify data with other services.

> 🎨 **Why it's cool**: This isn't just a data backup tool. It's the first step in a journey to create NFC-powered CD cases that can play your favorite Spotify media when scanned! 📀🎶

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Tech Stack](#tech-stack)
- [How it Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

\`\`\`bash
# Clone the repo
git clone https://github.com/AlexBoudreax/spotify-search.git

# Navigate into the directory
cd spotify-data-saver

# Install dependencies
pip3 install -r requirements.txt

# Add your environment variables
cp .env.sample .env.local
\`\`\`

Edit \`.env.local\` with your own Spotify and Supabase credentials.

---

## Usage

Run the script:

\`\`\`bash
python3 add_saved_media_to_db.py
\`\`\`

Your Spotify data will now be stored into your Supabase database.

---

## Tech Stack

- **Spotify Web API**: To fetch Spotify data.
- **Supabase**: To store the fetched data.
- **Python**: The backbone of this script.

---

## How it Works

1. **Fetch Data**: The script uses Spotipy, a Python library for the Spotify Web API, to fetch your followed artists, saved albums, and playlists.

2. **Structure Data**: The fetched data is structured in a Python dictionary.

3. **Store Data**: The data is then saved into respective tables in Supabase using its Python client.

---

## Contributing

Feel free to fork the project, open a PR, or submit an issue.

---

## License

MIT License. See \`LICENSE\` for more information.

---

👨‍💻 **Happy Coding!**
