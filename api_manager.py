"""
API manager to fix Duplicate Code anti-pattern in error handling.
Provides consistent error handling across all API calls.
"""

import aiohttp
import asyncio
import json
from typing import Optional, Dict, Any, Callable, Union
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
            async def wrapper(*args, **kwargs) -> Any:
                try:
                    return await func(*args, **kwargs)
                except aiohttp.ClientResponseError as http_err:
                    print(f'HTTP error occurred in {operation_name}: {http_err}')
                    return f'An HTTP error occurred in {operation_name}'
                except aiohttp.ClientError as err:
                    print(f'Request error occurred in {operation_name}: {err}')
                    return f'A request error occurred in {operation_name}'
                except Exception as err:
                    print(f'Unexpected error occurred in {operation_name}: {err}')
                    return f'An unexpected error occurred in {operation_name}'
            return wrapper
        return decorator


class APIManager:
    """Manages all external API calls with consistent error handling."""
    
    def __init__(self, nasa_api_key: str = 'DEMO_KEY'):
        """Initialize API manager."""
        self.error_handler = APIErrorHandler()
        self.nasa_api_key = nasa_api_key
    
    @APIErrorHandler.handle_api_request("NASA APOD")
    async def get_adop(self) -> Union[Dict[str, Any], str]:
        """Get NASA Astronomy Picture of the Day."""
        async with aiohttp.ClientSession() as session:
            params = {'api_key': self.nasa_api_key}
            async with session.get('https://api.nasa.gov/planetary/apod', params=params) as response:
                response.raise_for_status()
                return await response.json()
    
    @APIErrorHandler.handle_api_request("NASA Images")
    async def get_nasa_images(self, query: str) -> Union[Dict[str, Any], str]:
        """Search NASA images."""
        async with aiohttp.ClientSession() as session:
            params = {'q': query}
            async with session.get('https://images-api.nasa.gov/search', params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get('collection', {}).get('items', [])
    
    @APIErrorHandler.handle_api_request("Valorant Skins")
    async def get_valorant_skins(self) -> Union[Dict[str, Any], str]:
        """Get Valorant weapon skins."""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://valorant-api.com/v1/weapons/skins') as response:
                response.raise_for_status()
                return await response.json()
    
    @APIErrorHandler.handle_api_request("Meme API")
    async def get_meme(self) -> Union[Dict[str, Any], str]:
        """Get random meme."""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://meme-api.com/gimme') as response:
                response.raise_for_status()
                return await response.json()
    
    @APIErrorHandler.handle_api_request("Insult API")
    async def get_insult(self) -> Union[str, str]:
        """Get random insult."""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://evilinsult.com/generate_insult.php?lang=en&type=json') as response:
                response.raise_for_status()
                data = await response.json()
                return data.get('insult', 'Failed to get insult')
    
    @APIErrorHandler.handle_api_request("Advice API")
    async def get_advice(self) -> Union[str, str]:
        """Get random advice."""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.adviceslip.com/advice') as response:
                response.raise_for_status()
                data = await response.json()
                return data.get('slip', {}).get('advice', 'Failed to get advice')
    
    @APIErrorHandler.handle_api_request("Useless Facts API")
    async def get_useless_fact(self) -> Union[str, str]:
        """Get random useless fact."""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://uselessfacts.jsph.pl/random.json?language=en') as response:
                response.raise_for_status()
                data = await response.json()
                return data.get('text', 'Failed to get fact')
 