import httpx
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def fetch_lastfm_data(user, method, api_key, period="1month", limit=10):
    """Fetch data from Last.fm for a specific user and method."""
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        'method': method,
        'user': user,
        'api_key': api_key,
        'format': 'json',
        'period': period, 
        'limit': limit
    }
    timeout_config = httpx.Timeout(10.0, connect=60.0)
    headers = {
    "User-Agent": "LastFMStatsBot/1.0 (PersonalProject)"
    }
    try:
        async with httpx.AsyncClient(timeout=timeout_config, headers=headers) as client:
            response = await client.get(url, params=params)
            response.raise_for_status() 
            return response.json()
    except httpx.TimeoutException:
        logging.error("Request to Last.fm timed out")
        return None
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error occurred: {e.response.status_code}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

def format_data(data, item_type="tracks", num_items=10, period="1month"):
    """
    Format the top tracks or artists from Last.fm data.

    Args:
        data (dict): The Last.fm API response data.
        item_type (str): Type of items to format ("tracks" or "artists").
        num_items (int): Number of items to format.
        period (str): The time period (e.g., "1month" or "7day").

    Returns:
        str: Formatted message with the top items.
    """
    key_map = {
        "tracks": ("toptracks", "track"),
        "artists": ("topartists", "artist"),
    }

    if item_type not in key_map:
        return "Invalid item type specified."

    parent_key, child_key = key_map[item_type]

    if data and parent_key in data:
        items = data[parent_key][child_key]
        PERIOD_MAPPING = {
            "7day": "7 days",
            "1month": "1 month",
            "3month": "3 months",
            "6month": "6 months",
            "12month": "1 year"
        }

        title = f"Top {num_items} {item_type.capitalize()} for the Current {PERIOD_MAPPING.get(period, period).capitalize()}:\n"
        message = title
        for i, item in enumerate(items, 1):
            if item_type == "tracks":
                message += f"{i}. {item['name']} by {item['artist']['name']} - Plays: {item['playcount']}\n"
            elif item_type == "artists":
                message += f"{i}. {item['name']} - Plays: {item['playcount']}\n"
            if i >= num_items:
                break
        return message.strip()
    return "No data available."
