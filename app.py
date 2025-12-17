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
            "Create YouTube Music playlist",
        ])
        
        choice = get_choice(5)
        
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
        elif choice == 5:
            create_ytmusic_playlist_interactive()

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

def create_ytmusic_playlist_interactive():
    """Create a new YouTube Music playlist interactively."""
    print_header("CREATE YOUTUBE MUSIC PLAYLIST")
    
    # Get playlist name
    playlist_name = input("Enter playlist name: ").strip()
    if not playlist_name:
        print("Error: Playlist name cannot be empty.")
        pause()
        return
    
    # Get description (optional)
    description = input("Enter description (optional, press Enter to skip): ").strip()
    
    # Get privacy setting
    print("\nPrivacy options:")
    print("  [1] Private (only you can see it)")
    print("  [2] Public (anyone can see it)")
    print("  [3] Unlisted (anyone with link can see it)")
    
    privacy_choice = input("Choose privacy (1-3, default=1): ").strip()
    
    privacy_map = {
        "1": "PRIVATE",
        "2": "PUBLIC",
        "3": "UNLISTED",
        "": "PRIVATE"  # Default
    }
    
    privacy_status = privacy_map.get(privacy_choice, "PRIVATE")
    
    # Confirm
    print("\n" + "-" * 60)
    safe_print(f"Playlist Name: {playlist_name}")
    print(f"Description:   {description if description else '(none)'}")
    print(f"Privacy:       {privacy_status}")
    print("-" * 60)
    
    confirm = input("\nCreate this playlist? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Cancelled.")
        pause()
        return
    
    # Create the playlist
    try:
        from create_ytmusic_playlist import create_playlist
        playlist_id = create_playlist(playlist_name, description, privacy_status)
        print(f"\n[OK] Playlist created successfully!")
        print(f"Playlist ID: {playlist_id}")
        print("\nYou can now use this ID to map a Spotify playlist to it.")
    except Exception as e:
        print(f"\n[ERROR] Failed to create playlist: {e}")
    
    pause()

# =============================================================================
# AUTO-CREATE YOUTUBE MUSIC PLAYLISTS
# =============================================================================

def auto_create_menu():
    """Submenu for auto-creating YouTube Music playlists."""
    while True:
        print_header("AUTO-CREATE YOUTUBE MUSIC PLAYLISTS----DOESN'T WORK")
        
        print("This feature will:")
        print("  1. Fetch all your Spotify playlists")
        print("  2. Create matching playlists on YouTube Music")
        print("  3. Update config.py with the mappings")
        print()
        
        print_menu([
            "Preview (Dry Run - see what would be created)",
            "Create Playlists (actually create them)",
        ])
        
        choice = get_choice(2)
        
        if choice == 0:
            break
        elif choice == 1:
            auto_create_ytm_playlists(dry_run=True)
        elif choice == 2:
            auto_create_ytm_playlists(dry_run=False)


def auto_create_ytm_playlists(dry_run=False):
    """Auto-create YouTube Music playlists from all Spotify playlists."""
    print_header("AUTO-CREATE YOUTUBE MUSIC PLAYLISTS" + (" (DRY RUN)" if dry_run else ""))
    
    # Check prerequisites
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
        from config_updater import append_playlist_mappings, get_unmapped_playlists
        
        # Connect to Spotify
        print("Connecting to Spotify...")
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=config.SPOTIFY_CLIENT_ID,
            client_secret=config.SPOTIFY_CLIENT_SECRET,
            redirect_uri=config.SPOTIFY_REDIRECT_URI,
            scope="playlist-read-private playlist-read-collaborative"
        ))
        
        # Fetch ALL user's Spotify playlists
        print("Fetching your Spotify playlists...")
        all_playlists = []
        results = sp.current_user_playlists(limit=50)
        while results:
            all_playlists.extend(results['items'])
            if results['next']:
                results = sp.next(results)
            else:
                break
        
        print(f"Found {len(all_playlists)} Spotify playlists.")
        print()
        
        # Get current mapping
        current_mapping = config.PLAYLIST_MAPPING.copy() if hasattr(config, 'PLAYLIST_MAPPING') else {}
        
        # Filter out already mapped playlists
        unmapped_playlists = []
        for pl in all_playlists:
            if pl and pl.get('id') and pl.get('id') not in current_mapping:
                unmapped_playlists.append(pl)
        
        if not unmapped_playlists:
            print("[OK] All your Spotify playlists are already mapped!")
            print(f"Total: {len(all_playlists)} playlists, {len(current_mapping)} already mapped.")
            pause()
            return
        
        print(f"Found {len(unmapped_playlists)} unmapped playlists.")
        print(f"Already mapped: {len(current_mapping)}")
        print()
        
        # Show what will be created
        print("Playlists to create:")
        print("-" * 60)
        for i, pl in enumerate(unmapped_playlists[:10], 1):  # Show first 10
            safe_print(f"  {i}. {pl['name']}")
        
        if len(unmapped_playlists) > 10:
            print(f"  ... and {len(unmapped_playlists) - 10} more")
        print()
        
        # Confirmation for actual creation
        if not dry_run:
            confirm = input(f"Create {len(unmapped_playlists)} playlists on YouTube Music? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("Cancelled.")
                pause()
                return
            print()
        
        # Connect to YouTube Music (only if not dry run)
        if not dry_run:
            print("Connecting to YouTube Music...")
            ytm = YTMusic('browser_auth.json')
        
        # Process each playlist
        new_mappings = {}
        created_count = 0
        error_count = 0
        
        for pl in unmapped_playlists:
            sp_id = pl['id']
            name = pl['name']
            
            try:
                if dry_run:
                    safe_print(f"  Would create: {name}")
                    created_count += 1
                else:
                    safe_print(f"  Creating: {name}")
                    
                    # Create playlist on YouTube Music
                    yt_id = ytm.create_playlist(
                        title=name,
                        description=f"Synced from Spotify: {name}",
                        privacy_status='PRIVATE' if config.YTMUSIC_PLAYLIST_PRIVATE else 'PUBLIC'
                    )
                    
                    new_mappings[sp_id] = yt_id
                    created_count += 1
                    print(f"    ✓ Created (ID: {yt_id})")
                    
            except Exception as e:
                print(f"    ✗ Error: {e}")
                error_count += 1
        
        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"{'Would create' if dry_run else 'Created'}:  {created_count}")
        print(f"Errors:       {error_count}")
        print(f"Already mapped: {len(current_mapping)}")
        print("=" * 60)
        
        # Update config.py if not dry run and we created playlists
        if not dry_run and new_mappings:
            print()
            print("Updating config.py...")
            try:
                append_playlist_mappings(new_mappings)
                print(f"[OK] Added {len(new_mappings)} new mappings to config.py!")
                print("[OK] Backup saved as config.py.backup")
            except Exception as e:
                print(f"[ERROR] Failed to update config.py: {e}")
                print("You'll need to add the mappings manually.")
                print()
                print("Add these lines to PLAYLIST_MAPPING in config.py:")
                print("-" * 60)
                for sp_id, yt_id in new_mappings.items():
                    print(f'    "{sp_id}": "{yt_id}",')  
                print("-" * 60)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    
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
            "Auto-create YouTube Music Playlists",
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

