# Spotify to YouTube Music Sync 🎵 → 📺

Sync your Spotify playlists to YouTube Music automatically with high accuracy.

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/kunal-1320/SpotifytoYTMusicSync.git
cd SpotifytoYTMusicSync

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create config file
# Windows: copy config.example.py config.py
# Mac/Linux: cp config.example.py config.py

# 4. Run the interactive menu
python app.py
```

### 📋 Setup Steps in Interactive Menu:
1.  **Setup Spotify** — Connect your Spotify account. (Verify: *Manage Playlists* -> *View Spotify Playlists*)
2.  **Setup YTMusic** — Authenticate with YouTube Music. (Verify: *Manage Playlists* -> *View YT Music Playlists*)
3.  **Map Playlists** — Manually link Spotify IDs to YT Music IDs **OR** use **Auto-Create Playlists**.
4.  **Dry Run** — Preview the sync without making changes.
5.  **Main Sync** — Start the actual transfer.

> [!NOTE]
> YouTube Music request headers expire periodically. If authentication fails, simply run the YTMusic setup again.

---

## ✨ Features

- **Smart Matching** — High accuracy algorithm (supports English, Hindi, French, and more).
- **Simple Browser Auth** — No complex Google Cloud project setup required.
- **Smart Sync** — Detects duplicates automatically and skips already-synced tracks.
- **Auto-Validation** — Identifies broken mappings and differentiates between expired sessions vs. missing playlists.
- **Batch Processing** — Sync multiple playlists in one go.
- **Dry Run Mode** — See exactly what will happen before it happens.
- **Chrome/Brave/Firefox Support** — Supports "Copy as cURL (bash)" for Chrome/Brave and "Copy Request Headers" for Firefox.

## 🛠️ Requirements

- Python 3.8+
- Spotify account (Developer App)
- YouTube Music account (Logged in via browser)

## 📖 Detailed Setup

### 1. Spotify Developer Setup
1.  Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2.  Create a new App.
3.  Set the **Redirect URI** to: `http://127.0.0.1:8888/callback`.
4.  Copy the **Client ID** and **Client Secret** into `config.py` (or enter them through the `app.py` menu).

### 2. YouTube Music Setup
Run `python setup_browser_auth.py` or use the option in `app.py`.
- **Firefox:** Copy "Request Headers".
- **Chrome/Brave:** Copy as "cURL (bash)".

### 3. Playlist Mapping
Edit `PLAYLIST_MAPPING` in `config.py`:
```python
PLAYLIST_MAPPING = {
    "SPOTIFY_PLAYLIST_ID": "YTMUSIC_PLAYLIST_ID",
}
```
- **Spotify ID:** Found in the URL after `/playlist/[ID]`.
- **YT Music ID:** Found in the URL after `?list=[ID]`.

## 📂 Project Structure

- `app.py` — The interactive control center.
- `sync_playlists.py` — Core synchronization engine.
- `setup_browser_auth.py` — Authentication helper for YT Music.
- `config.py` — Your local configuration (Git-ignored).
- `config_updater.py` — Manages automated updates to your config.
- `utils/` — Logic for API clients, UI formatting, and validation.

## 🔒 Security
Your credentials are kept local and never shared.
- `config.py` — Stores your API keys.
- `browser_auth.json` — Stores YouTube session cookies.
**Never commit these files to GitHub!** They are included in `.gitignore` by default.

---
*Created with ❤️ for music lovers.*
