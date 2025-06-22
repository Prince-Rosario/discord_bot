"""
API manager to fix Duplicate Code anti-pattern in error handling.
Provides consistent error handling across all API calls.
"""

import requests
import json
from typing import Optional, Dict, Any, Callable
from functools import wraps


class APIErrorHandler:
    """Handles API errors consistently across all API calls."""
    
    @staticmethod
    def handle_api_request(operation_name: str) -> Callable:
        """Decorator to handle API requests with consistent error handling.
        
        This eliminates duplicate error handling code across API functions.
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                try:
                    response = func(*args, **kwargs)
                    if hasattr(response, 'raise_for_status'):
                        response.raise_for_status()
                    return response
                except requests.exceptions.HTTPError as http_err:
                    print(f'HTTP error occurred in {operation_name}: {http_err}')
                    return f'An HTTP error occurred in {operation_name}'
                except requests.exceptions.RequestException as err:
                    print(f'Request error occurred in {operation_name}: {err}')
                    return f'A request error occurred in {operation_name}'
                except Exception as err:
                    print(f'Unexpected error occurred in {operation_name}: {err}')
                    return f'An unexpected error occurred in {operation_name}'
            return wrapper
        return decorator


class APIManager:
    """Manages all external API calls with consistent error handling."""
    
    def __init__(self):
        """Initialize API manager."""
        self.error_handler = APIErrorHandler()
    
    @APIErrorHandler.handle_api_request("NASA APOD")
    def get_nasa_apod(self, api_key: str) -> requests.Response:
        """Get NASA Astronomy Picture of the Day."""
        params = {'api_key': api_key}
        response = requests.get('https://api.nasa.gov/planetary/apod', params=params)
        return response
    
    @APIErrorHandler.handle_api_request("NASA Images")
    def get_nasa_images(self, query: str) -> requests.Response:
        """Search NASA images."""
        params = {'q': query}
        response = requests.get('https://images-api.nasa.gov/search', params=params)
        return response
    
    @APIErrorHandler.handle_api_request("Valorant Skins")
    def get_valorant_skins(self) -> requests.Response:
        """Get Valorant weapon skins."""
        response = requests.get('https://valorant-api.com/v1/weapons/skins')
        return response
    
    @APIErrorHandler.handle_api_request("Meme API")
    def get_random_meme(self) -> requests.Response:
        """Get random meme."""
        response = requests.get('https://meme-api.com/gimme')
        return response
    
    @APIErrorHandler.handle_api_request("Insult API")
    def get_random_insult(self) -> requests.Response:
        """Get random insult."""
        response = requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=json')
        return response
    
    @APIErrorHandler.handle_api_request("Advice API")
    def get_random_advice(self) -> requests.Response:
        """Get random advice."""
        response = requests.get('https://api.adviceslip.com/advice')
        return response
    
    @APIErrorHandler.handle_api_request("Useless Facts API")
    def get_random_fact(self) -> requests.Response:
        """Get random useless fact."""
        response = requests.get('https://uselessfacts.jsph.pl/random.json?language=en')
        return response
    
    def process_nasa_apod_response(self, response: Any) -> str:
        """Process NASA APOD response safely."""
        if isinstance(response, str):  # Error message
            return response
        try:
            data = response.json()
            return data.get('url', 'No image URL found')
        except (json.JSONDecodeError, AttributeError):
            return 'Failed to parse NASA APOD response'
    
    def process_nasa_images_response(self, response: Any) -> str:
        """Process NASA images response safely."""
        if isinstance(response, str):  # Error message
            return response
        try:
            data = response.json()
            items = data.get('collection', {}).get('items', [])
            urls = []
            for item in items:
                if 'links' in item and item['links'] and item['data'][0]['media_type'] == 'image':
                    urls.append(item['links'][0]['href'])
            return '\n'.join(urls[:5]) if urls else 'No images found'
        except (json.JSONDecodeError, AttributeError, KeyError, IndexError):
            return 'Failed to parse NASA images response'
    
    def process_meme_response(self, response: Any) -> str:
        """Process meme response safely."""
        if isinstance(response, str):  # Error message
            return response
        try:
            data = response.json()
            return data.get('url', 'No meme URL found')
        except (json.JSONDecodeError, AttributeError):
            return 'Failed to parse meme response' 