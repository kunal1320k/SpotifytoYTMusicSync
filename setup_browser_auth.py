#!/usr/bin/env python3
"""
YouTube Music Browser Authentication Setup
===========================================
Simple 2-minute setup - just copy request headers from your browser!
No Google Cloud project or OAuth setup needed.
"""

import os
import sys

# Add current directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.auth_helper import parse_headers, validate_headers, save_browser_auth
from utils.ui import (
    clear_screen, print_header, print_divider, print_success, 
    print_error, print_warning, print_info, get_multiline_input,
    Colors, safe_print
)

def print_instructions():
    """Print detailed browser-specific instructions."""
    print_header("YOUTUBE MUSIC SETUP", "Simple Browser Authentication")
    
    print("This is EASY! Just follow the steps for your browser:")
    print()
    print("-" * 70)
    print("STEP 1: Open YouTube Music and Sign In")
    print("-" * 70)
    print("  1. Go to: https://music.youtube.com")
    print("  2. Make sure you're SIGNED IN with your Google account")
    print()
    print("-" * 70)
    print("STEP 2: Open Developer Tools")
    print("-" * 70)
    print("  • Press F12 (or Right-click → Inspect)")
    print("  • Click the 'Network' tab at the top")
    print()
    print("-" * 70)
    print("STEP 3: Find an Authenticated Request")
    print("-" * 70)
    print("  • In the Network tab filter box, type: browse")
    print("  • Click on 'Library' in YouTube Music (left sidebar)")
    print("  • Look for a POST request with these details:")
    print("      ✓ Status: 200")
    print("      ✓ Method: POST")
    print("      ✓ Name/File: browse?...")
    print()
    print("-" * 70)
    print("STEP 4: Copy Request Headers (BROWSER-SPECIFIC)")
    print("-" * 70)
    print()
    print("  📌 FIREFOX (Recommended):")
    print("     • Click on the 'browse' request")
    print("     • Right-click → Copy → Copy Request Headers")
    print("     • Done! That's it.")
    print()
    print("  📌 CHROME / EDGE / ANY BROWSER:")
    print("     • Click on the 'browse' request")
    print("     • **BEST OPTION:** Right-click request -> Copy -> **Copy as cURL (bash)**")
    print("     • Run this script and paste the whole thing.")
    print()
    print("=" * 70)
    print()

def main():
    print_instructions()

    headers_text = get_multiline_input("Paste your request headers below (then press Enter twice):")

    if not headers_text or len(headers_text) < 100:
        print()
        print_error("Headers seem too short or empty.")
        print_info("Make sure you copied the full request headers.")
        input("\nPress Enter to exit...")
        return

    # Parse headers
    try:
        headers = parse_headers(headers_text)

        # Show what was extracted
        print()
        print("=" * 70)
        print("EXTRACTED HEADERS:")
        print("=" * 70)
        
        required = ['cookie', 'authorization', 'x-goog-authuser', 'x-goog-visitor-id']
        all_good = True
        
        for key in required:
            if key in headers:
                preview = headers[key][:60] + "..." if len(headers[key]) > 60 else headers[key]
                print(f"[OK] {key}: {preview}")
            else:
                print(f"[MISSING] {key}")
                all_good = False
        
        print("=" * 70)
        print()

        if not all_good:
            print_error("Missing required headers!")
            print()
            print("Common issues:")
            print("  1. x-goog-visitor-id is REQUIRED for playlist operations")
            print("  2. Make sure you copied the COMPLETE cURL command")
            print("  3. Make sure you're copying from music.youtube.com (not youtube.com)")
            print("  4. Try copying from a different 'browse' POST request")
            print("  5. Firefox 'Copy Request Headers' or Chrome 'Copy as cURL (bash)' work best")
            print()
            input("Press Enter to exit...")
            return

        # Save to file
        auth_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_auth.json")
        save_browser_auth(headers, auth_path)

        print_success("Headers saved to browser_auth.json")
        print()
        print_info("Testing connection...")

        # Test the connection with better error handling
        try:
            from ytmusicapi import YTMusic
            ytm = YTMusic(auth_path)

            # Test with actual playlist access (not just search)
            try:
                # Try to get user's playlists - this requires proper auth
                playlists = ytm.get_library_playlists(limit=1)
                
                if playlists is not None:  # Even empty list is success
                    print()
                    print("=" * 70)
                    print_success("SUCCESS! YouTube Music is connected and working!")
                    print("=" * 70)
                    print()
                    if playlists:
                        print(f"  Found {len(playlists)} playlist(s) in your library.")
                    else:
                        print("  No playlists found (but authentication works!)")
                    print()
                    print("You can now:")
                    print("  • Run the main app: python app.py")
                    print("  • Or sync directly: python sync_playlists.py")
                    print()
                else:
                    print()
                    print_warning("Connection test completed, but results are unclear.")
                    print()
                    print("The headers are saved. Try running the sync to see if it works:")
                    print("  python sync_playlists.py --test-ytmusic")

            except Exception as search_error:
                error_str = str(search_error)
                if "401" in error_str or "unauthorized" in error_str.lower():
                    print()
                    print_error("Authentication failed (401 Unauthorized)!")
                    print()
                    print("Common fixes:")
                    print("  1. Missing x-goog-visitor-id header (REQUIRED for playlists)")
                    print("  2. Make sure you copied from music.youtube.com (not youtube.com)")
                    print("  3. Copy from a 'browse' POST request, not GET")
                    print("  4. Make sure you're logged in to YouTube Music")
                    print("  5. Try copying fresh headers (cookies expire)")
                    print()
                    if 'x-goog-visitor-id' not in headers:
                        print_warning("DETECTED: x-goog-visitor-id is MISSING from your headers!")
                        print("   This header is REQUIRED for playlist operations.")
                        print("   Make sure you copy the FULL cURL command including ALL headers.")
                    print()
                elif "400" in error_str or "bad request" in error_str.lower():
                    print()
                    print_warning("Request format issue")
                    print()
                    # ... (rest of error handling same as before but using print_warning)
                    print("This usually means:")
                    print("  • Headers might be incomplete")
                    print("  • Try copying from a different 'browse' request")
                    print("  • Make sure you selected the FULL headers")
                    print()
                else:
                    print()
                    print_warning(f"Connection test error: {search_error}")
                    print()
                    print("Headers are saved, but verification failed.")
                    print("Try running the sync to see if it works anyway:")
                    print("  python sync_playlists.py --test-ytmusic")
                    print()

        except ImportError:
            print()
            print_error("ytmusicapi not installed!")
            print("   Run: pip install ytmusicapi")
        except Exception as e:
            print()
            print_warning(f"Unexpected error: {e}")
            print()
            print("Headers saved. Try testing with:")
            print("  python sync_playlists.py --test-ytmusic")

    except Exception as e:
        print()
        print_error(f"Error: {e}")
        print("   Something went wrong parsing the headers.")
        print("   Make sure you copied the raw request headers correctly.")
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
