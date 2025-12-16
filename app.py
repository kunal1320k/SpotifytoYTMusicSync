#!/usr/bin/env python3
"""
Spotify to YouTube Music Sync - Interactive Menu
=================================================
Run this file for easy setup and sync operations.
"""

import os
import sys
import json

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def safe_print(message):
    """Print with fallback for Unicode issues."""
    try:
        print(message)
    except UnicodeEncodeError:
        # Replace emoji with ASCII
        safe = message.encode('ascii', errors='replace').decode('ascii')
        print(safe)

def print_header(title):
    clear_screen()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()

def print_menu(options):
    for i, option in enumerate(options, 1):
        safe_print(f"  [{i}] {option}")
    print(f"  [0] Back / Exit")
    print()

def get_choice(max_option):
    while True:
        try:
            choice = input("Enter choice: ").strip()
            if choice == "":
                continue
            num = int(choice)
            if 0 <= num <= max_option:
                return num
        except ValueError:
            pass
        print("Invalid choice. Please try again.")

def pause():
    input("\nPress Enter to continue...")

# =============================================================================
# STATUS CHECKS
# =============================================================================

def check_spotify_status():
    """Check if Spotify is configured."""
    try:
        import config
        if config.SPOTIFY_CLIENT_ID and config.SPOTIFY_CLIENT_ID != "YOUR_SPOTIFY_CLIENT_ID":
            return True
    except:
        pass
    return False

def check_ytmusic_status():
    """Check if YouTube Music is configured."""
    return os.path.exists("browser_auth.json")



def get_playlist_mapping():
    """Get current playlist mappings."""
    try:
        import importlib
        import config
        importlib.reload(config)
        if hasattr(config, 'PLAYLIST_MAPPING'):
            return config.PLAYLIST_MAPPING
    except:
        pass
    return {}

# =============================================================================
# SETUP FUNCTIONS
# =============================================================================

def setup_spotify():
    print_header("SPOTIFY SETUP")
    print("You need to create a Spotify Developer App to use this tool.")
    print()
    print("Steps:")
    print("  1. Go to: https://developer.spotify.com/dashboard")
    print("  2. Log in and click 'Create App'")
    print("  3. Fill in any name and description")
    print("  4. Set Redirect URI to: http://127.0.0.1:8888/callback")
    print("  5. Save and get your Client ID and Client Secret")
    print()
    
    client_id = input("Enter your Spotify Client ID: ").strip()
    if not client_id:
        print("Cancelled.")
        return False
    
    client_secret = input("Enter your Spotify Client Secret: ").strip()
    if not client_secret:
        print("Cancelled.")
        return False
    
    # Update config.py
    try:
        with open("config.py", "r") as f:
            content = f.read()
        
        # Replace the placeholders
        import re
        content = re.sub(
            r'SPOTIFY_CLIENT_ID = "[^"]*"',
            f'SPOTIFY_CLIENT_ID = "{client_id}"',
            content
        )
        content = re.sub(
            r'SPOTIFY_CLIENT_SECRET = "[^"]*"',
            f'SPOTIFY_CLIENT_SECRET = "{client_secret}"',
            content
        )
        
        with open("config.py", "w") as f:
            f.write(content)
        
        print("\n[OK] Spotify credentials saved!")
        
        # Test connection
        print("\nTesting Spotify connection...")
        try:
            import importlib
            import config
            importlib.reload(config)
            
            import spotipy
            from spotipy.oauth2 import SpotifyOAuth
            
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=config.SPOTIFY_CLIENT_ID,
                client_secret=config.SPOTIFY_CLIENT_SECRET,
                redirect_uri=config.SPOTIFY_REDIRECT_URI,
                scope="playlist-read-private playlist-read-collaborative"
            ))
            user = sp.current_user()
            print(f"[OK] Connected as: {user['display_name']}")
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            print("Make sure your credentials are correct and Redirect URI is set.")
        
        pause()
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        pause()
        return False

def setup_ytmusic():
    print_header("YOUTUBE MUSIC SETUP")
    print("Simple 2-minute setup - just copy request headers!")
    print()
    print("OPTION 1 - Easiest (Recommended):")
    print("  Run the setup script for detailed instructions:")
    print("  → python setup_browser_auth.py")
    print()
    print("OPTION 2 - Quick (if you know what you're doing):")
    print("  1. Go to https://music.youtube.com (make sure you're signed in)")
    print("  2. Press F12 → Network tab → filter 'browse'")
    print("  3. Click 'Library' in YouTube Music")
    print("  4. Find a POST request to 'browse?...'")
    print()
    print("  Firefox: Right-click → Copy → Copy Request Headers")
    print("  Chrome:  Copy everything from 'accept: */*' in Request Headers section")
    print()
    
    choice = input("Continue with quick setup here? (y/n): ").strip().lower()
    
    if choice != 'y':
        print("\nRun: python setup_browser_auth.py")
        print("That script has detailed step-by-step instructions!")
        pause()
        return False
    
    print("\nPaste your request headers below (press Enter twice when done):")
    print("-" * 50)
    
    lines = []
    empty_count = 0
    while True:
        try:
            line = input()
            if line.strip() == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
        except (EOFError, KeyboardInterrupt):
            break
    
    headers_text = '\n'.join(lines)
    
    if not headers_text or len(headers_text) < 100:
        print("\n[X] Headers too short or empty. Cancelled.")
        pause()
        return False
    
    try:
        from ytmusicapi import setup
        setup(filepath='browser_auth.json', headers_raw=headers_text)
        print("\n[OK] YouTube Music browser auth saved!")
        
        # Test connection
        print("\nTesting YouTube Music connection...")
        from ytmusicapi import YTMusic
        ytm = YTMusic('browser_auth.json')
        result = ytm.search('test', filter='songs', limit=1)
        if result:
            print("[OK] YouTube Music connected and working!")
        else:
            print("[WARN] Connected but no search results.")
        
        pause()
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        print("\nTry running: python setup_browser_auth.py")
        print("for detailed instructions.")
        pause()
        return False



# =============================================================================
# PLAYLIST MANAGEMENT
# =============================================================================

def manage_playlists():
    while True:
        print_header("PLAYLIST MANAGEMENT")
        
        mapping = get_playlist_mapping()
        
        if mapping:
            print("Current playlist mappings:")
            print("-" * 50)
            for i, (sp_id, yt_id) in enumerate(mapping.items(), 1):
                print(f"  {i}. Spotify: {sp_id[:25]}...")
                print(f"     YT Music: {yt_id}")
                print()
        else:
            print("No playlists configured yet.")
        
        print()
        print_menu([
            "Add new playlist mapping",
            "Remove a playlist mapping",
            "View Spotify playlists",
            "View YouTube Music playlists",
        ])
        
        choice = get_choice(4)
        
        if choice == 0:
            break
        elif choice == 1:
            add_playlist_mapping()
        elif choice == 2:
            remove_playlist_mapping()
        elif choice == 3:
            view_spotify_playlists()
        elif choice == 4:
            view_ytmusic_playlists()

def add_playlist_mapping():
    print_header("ADD PLAYLIST MAPPING")
    print("Enter the playlist IDs to map:")
    print()
    print("Spotify ID: From playlist URL, the part after /playlist/")
    print("YT Music ID: From playlist URL, the part after ?list= (starts with PL)")
    print()
    
    spotify_id = input("Spotify Playlist ID: ").strip()
    if not spotify_id:
        return
    
    ytmusic_id = input("YouTube Music Playlist ID: ").strip()
    if not ytmusic_id:
        return
    
    # Update config.py
    try:
        with open("config.py", "r") as f:
            content = f.read()
        
        # Find PLAYLIST_MAPPING and add the new entry
        import re
        
        # Find the mapping dict
        pattern = r'(PLAYLIST_MAPPING = \{[^}]*)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            old_mapping = match.group(1)
            # Add new entry before the closing brace
            new_entry = f'\n    "{spotify_id}": "{ytmusic_id}",'
            new_mapping = old_mapping + new_entry
            content = content.replace(old_mapping, new_mapping)
            
            with open("config.py", "w") as f:
                f.write(content)
            
            print(f"\n[OK] Added mapping!")
            print(f"   Spotify: {spotify_id}")
            print(f"   YT Music: {ytmusic_id}")
        else:
            print("[ERROR] Could not find PLAYLIST_MAPPING in config.py")
    except Exception as e:
        print(f"Error: {e}")
    
    pause()

def remove_playlist_mapping():
    mapping = get_playlist_mapping()
    if not mapping:
        print("No mappings to remove.")
        pause()
        return
    
    print_header("REMOVE PLAYLIST MAPPING")
    print("Select a mapping to remove:")
    print()
    
    items = list(mapping.items())
    for i, (sp_id, yt_id) in enumerate(items, 1):
        print(f"  [{i}] {sp_id[:30]}...")
    print("  [0] Cancel")
    print()
    
    choice = get_choice(len(items))
    if choice == 0:
        return
    
    sp_id_to_remove = items[choice - 1][0]
    
    # Update config.py
    try:
        with open("config.py", "r") as f:
            content = f.read()
        
        # Remove the line with this Spotify ID
        import re
        pattern = rf'\s*"{re.escape(sp_id_to_remove)}"\s*:\s*"[^"]*"\s*,?\s*\n?'
        content = re.sub(pattern, '\n', content)
        
        with open("config.py", "w") as f:
            f.write(content)
        
        print(f"\n[OK] Removed mapping for: {sp_id_to_remove[:30]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    pause()

def view_spotify_playlists():
    print_header("YOUR SPOTIFY PLAYLISTS")
    
    try:
        import importlib
        import config
        importlib.reload(config)
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth
        
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=config.SPOTIFY_CLIENT_ID,
            client_secret=config.SPOTIFY_CLIENT_SECRET,
            redirect_uri=config.SPOTIFY_REDIRECT_URI,
            scope="playlist-read-private playlist-read-collaborative"
        ))
        
        playlists = sp.current_user_playlists(limit=20)
        
        print("Your Spotify Playlists:")
        print("-" * 60)
        for pl in playlists['items']:
            safe_print(f"  Name: {pl['name']}")
            print(f"  ID:   {pl['id']}")
            print()
    except Exception as e:
        print(f"Error: {e}")
    
    pause()

def view_ytmusic_playlists():
    print_header("YOUR YOUTUBE MUSIC PLAYLISTS")
    
    try:
        from ytmusicapi import YTMusic
        ytm = YTMusic('browser_auth.json')
        
        playlists = ytm.get_library_playlists(limit=20)
        
        if playlists:
            print("Your YouTube Music Playlists:")
            print("-" * 60)
            for pl in playlists:
                safe_print(f"  Name: {pl.get('title', 'Unknown')}")
                print(f"  ID:   {pl.get('playlistId', 'N/A')}")
                print()
        else:
            print("No playlists found or could not fetch.")
    except Exception as e:
        print(f"Error: {e}")
    
    pause()

# =============================================================================
# AUTO-CREATE YOUTUBE MUSIC PLAYLISTS
# =============================================================================

def auto_create_menu():
    while True:
        print_header("AUTO-CREATE YOUTUBE MUSIC PLAYLISTS")
        
        print_menu([
            "Dry Run (Preview what would be created)",
            "Create Playlists (Actual creation)",
        ])
        
        choice = get_choice(2)
        
        if choice == 0:
            break
        elif choice == 1:
            auto_create_ytm_playlists(dry_run=True)
        elif choice == 2:
            auto_create_ytm_playlists(dry_run=False)

def auto_create_ytm_playlists(dry_run=False):
    print_header("AUTO-CREATE YOUTUBE MUSIC PLAYLISTS" + (" (DRY RUN)" if dry_run else ""))
    
    if not check_spotify_status():
        print("[X] Spotify not configured! Set it up first.")
        pause()
        return
    
    if not check_ytmusic_status():
        print("[X] YouTube Music not configured! Set it up first.")
        pause()
        return
    
    try:
        import importlib
        import config
        importlib.reload(config)
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth
        from ytmusicapi import YTMusic
        
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=config.SPOTIFY_CLIENT_ID,
            client_secret=config.SPOTIFY_CLIENT_SECRET,
            redirect_uri=config.SPOTIFY_REDIRECT_URI,
            scope="playlist-read-private playlist-read-collaborative"
        ))
        
        if not dry_run:
            ytm = YTMusic('browser_auth.json')
        
        current_mapping = config.PLAYLIST_MAPPING.copy()
        new_mappings = {}
        
        print("Checking playlists...")
        print()
        
        for sp_id in config.SPOTIFY_PLAYLIST_IDS:
            if sp_id in current_mapping:
                print(f"Skipping {sp_id}: already mapped.")
                continue
            
            try:
                pl = sp.playlist(sp_id)
                if not isinstance(pl, dict):
                    print(f"Skipping {sp_id}: invalid playlist data (not dict).")
                    continue
                name = pl['name']
            except (TypeError, KeyError) as e:
                print(f"Skipping {sp_id}: invalid playlist data ({e})")
                continue
            
            safe_print(f"{'Would create' if dry_run else 'Creating'} playlist: {name}")
            
            if not dry_run:
                yt_pl = ytm.create_playlist(
                    title=name,
                    description=f"Synced from Spotify: {name}",
                    privacy_status='PRIVATE' if config.YTMUSIC_PLAYLIST_PRIVATE else 'PUBLIC'
                )
                
                yt_id = yt_pl
                new_mappings[sp_id] = yt_id
                print(f"Created: {yt_id}")
            else:
                print("(Dry run - not created)")
            print()
        
        if not dry_run and new_mappings:
            # Update mapping
            current_mapping.update(new_mappings)
            
            # Now update config.py
            with open("config.py", "r") as f:
                content = f.read()
            
            # Find PLAYLIST_MAPPING = { ... }
            import re
            pattern = r'(PLAYLIST_MAPPING = \{)(.*?)(\})'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                prefix = match.group(1)
                suffix = match.group(3)
                # Construct new dict string
                lines = [f'    "{k}": "{v}",' for k, v in current_mapping.items()]
                new_dict_content = '\n'.join(lines)
                new_mapping_str = prefix + '\n' + new_dict_content + '\n' + suffix
                
                content = content.replace(match.group(0), new_mapping_str)
                
                with open("config.py", "w") as f:
                    f.write(content)
                
                print(f"\n[OK] Added {len(new_mappings)} new mappings!")
            else:
                print("[ERROR] Could not find PLAYLIST_MAPPING in config.py")
        elif dry_run:
            print(f"\n[Dry Run] Would add {len([sp_id for sp_id in config.SPOTIFY_PLAYLIST_IDS if sp_id not in current_mapping])} new mappings.")
        else:
            print("No new playlists to create.")
        
    except Exception as e:
        print(f"Error: {e}")
    
    pause()

# =============================================================================
# SYNC FUNCTIONS
# =============================================================================

def run_sync(dry_run=False):
    print_header("RUNNING SYNC" + (" (DRY RUN)" if dry_run else ""))
    
    mapping = get_playlist_mapping()
    if not mapping:
        print("[X] No playlist mappings configured!")
        print("Go to Playlist Management to add some.")
        pause()
        return
    
    print(f"Syncing {len(mapping)} playlist(s)...")
    print()
    
    # Import and run sync
    try:
        from sync_playlists import sync_playlists
        sync_playlists(dry_run=dry_run)
    except Exception as e:
        print(f"Error during sync: {e}")
    
    pause()

# =============================================================================
# MAIN MENU
# =============================================================================

def show_status():
    spotify_ok = check_spotify_status()
    ytmusic_ok = check_ytmusic_status()
    playlists = get_playlist_mapping()
    
    print("Current Status:")
    print("-" * 40)
    print(f"  Spotify:   {'[OK] Ready' if spotify_ok else '[X] Not configured'}")
    print(f"  YT Music:  {'[OK] Ready' if ytmusic_ok else '[X] Not configured'}")
    print(f"  Playlists: {len(playlists)} mapped")
    print()
    
    return spotify_ok, ytmusic_ok

def main_menu():
    while True:
        print_header("SPOTIFY TO YOUTUBE MUSIC SYNC")
        
        spotify_ok, ytmusic_ok = show_status()
        
        # Show setup wizard if not ready
        if not spotify_ok or not ytmusic_ok:
            print("[!] Setup required! Select an option below to get started.")
            print()
        
        print_menu([
            "Sync Now",
            "Preview Sync (Dry Run)",
            "Manage Playlists",
            "Setup Spotify",
            "Setup YouTube Music",
            "Auto-create YouTube Music playlists from Spotify playlists",
        ])
        
        choice = get_choice(6)
        
        if choice == 0:
            print("\nGoodbye!")
            break
        elif choice == 1:
            if not spotify_ok:
                print("\n[X] Please set up Spotify first!")
                pause()
            elif not ytmusic_ok:
                print("\n[X] Please set up YouTube Music first!")
                pause()
            else:
                run_sync(dry_run=False)
        elif choice == 2:
            if not spotify_ok or not ytmusic_ok:
                print("\n[X] Please complete setup first!")
                pause()
            else:
                run_sync(dry_run=True)
        elif choice == 3:
            manage_playlists()
        elif choice == 4:
            setup_spotify()
        elif choice == 5:
            setup_ytmusic()
        elif choice == 6:
            auto_create_menu()

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
