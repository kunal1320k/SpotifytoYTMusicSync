"""
YouTube Music Validator Module
================================
Utilities for validating YTMusic authentication and playlist access.
Helps differentiate between authentication errors and missing playlists.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def is_auth_error(exception) -> bool:
    """
    Check if an exception is an authentication error (expired headers).
    
    Args:
        exception: The exception to check
        
    Returns:
        bool: True if this is an authentication/authorization error
    """
    error_str = str(exception).lower()
    
    # Common authentication error indicators
    auth_indicators = [
        '401',
        'unauthorized',
        'authentication',
        'invalid credentials',
        'expired',
        'forbidden',
        '403'
    ]
    
    return any(indicator in error_str for indicator in auth_indicators)


def check_ytmusic_auth() -> tuple:
    """
    Test if YTMusic authentication is still valid.
    
    Returns:
        Tuple of (is_valid: bool, message: str, error_type: str)
        error_type can be: 'none', 'missing', 'expired', 'network', 'unknown'
    """
    import os
    
    # First check if browser_auth.json exists
    auth_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'browser_auth.json'
    )
    
    if not os.path.exists(auth_file):
        return (False, "YouTube Music headers not configured. Run: python setup_browser_auth.py", 'missing')
    
    # File exists, now test if the headers are valid
    try:
        from utils.clients import get_ytmusic_client
        
        ytm = get_ytmusic_client()
        
        # Try a simple operation to verify auth works
        # Using search is lightweight and tests auth
        ytm.search('test', filter='songs', limit=1)
        
        return (True, "YouTube Music authentication is valid", 'none')
        
    except FileNotFoundError as e:
        # This shouldn't happen since we checked above, but just in case
        return (False, str(e), 'missing')
        
    except Exception as e:
        error_str = str(e)
        
        # Check if it's an authentication error
        if is_auth_error(e):
            return (False, "YouTube Music headers have EXPIRED. Please re-run: python setup_browser_auth.py", 'expired')
        
        # Network/connectivity issues
        if 'network' in error_str.lower() or 'connection' in error_str.lower():
            return (False, f"Network error: {error_str}", 'network')
        
        # Unknown error
        return (False, f"Error testing YouTube Music: {error_str}", 'unknown')


def validate_playlist_access(ytm, playlist_id: str) -> tuple:
    """
    Check if a specific playlist can be accessed.
    
    Args:
        ytm: YTMusic client instance
        playlist_id: The playlist ID to check
        
    Returns:
        Tuple of (accessible: bool, error_type: str, message: str)
        error_type can be: 'none', 'auth', 'not_found', 'unknown'
    """
    try:
        # Try to fetch the playlist
        ytm.get_playlist(playlist_id, limit=1)
        return (True, 'none', 'Playlist is accessible')
        
    except Exception as e:
        error_str = str(e).lower()
        
        # Check for authentication errors
        if is_auth_error(e):
            return (False, 'auth', 'Authentication error - headers may be expired')
        
        # Check for not found errors
        not_found_indicators = ['404', 'not found', 'does not exist', 'deleted']
        if any(indicator in error_str for indicator in not_found_indicators):
            return (False, 'not_found', 'Playlist does not exist or has been deleted')
        
        # Unknown error
        return (False, 'unknown', f'Error accessing playlist: {str(e)}')


def validate_all_playlists(ytm, playlist_mapping: dict) -> dict:
    """
    Validate all playlists in a mapping.
    
    Args:
        ytm: YTMusic client instance
        playlist_mapping: Dict of {spotify_id: ytmusic_id}
        
    Returns:
        Dict with validation results:
        {
            'valid': [(sp_id, yt_id), ...],
            'missing': [(sp_id, yt_id), ...],
            'auth_errors': [(sp_id, yt_id), ...],
            'unknown_errors': [(sp_id, yt_id, error_msg), ...]
        }
    """
    results = {
        'valid': [],
        'missing': [],
        'auth_errors': [],
        'unknown_errors': []
    }
    
    for sp_id, yt_id in playlist_mapping.items():
        if not yt_id:
            # No YT playlist mapped
            results['valid'].append((sp_id, yt_id))
            continue
        
        accessible, error_type, message = validate_playlist_access(ytm, yt_id)
        
        if accessible:
            results['valid'].append((sp_id, yt_id))
        elif error_type == 'auth':
            results['auth_errors'].append((sp_id, yt_id))
        elif error_type == 'not_found':
            results['missing'].append((sp_id, yt_id))
        else:
            results['unknown_errors'].append((sp_id, yt_id, message))
    
    return results


# Self-test
if __name__ == "__main__":
    print("Testing YTMusic Validator...")
    print()
    
    # Test auth check
    is_valid, message, error_type = check_ytmusic_auth()
    print(f"Auth Status: {'✅ Valid' if is_valid else '❌ Invalid'}")
    print(f"Message: {message}")
    print(f"Error Type: {error_type}")
