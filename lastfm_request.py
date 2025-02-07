import httpx
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class LastFMClient:
    """Async client for fetching data from Last.fm API."""

    BASE_URL = "http://ws.audioscrobbler.com/2.0/"
    PERIOD_MAPPING = {
        "7day": "7 days",
        "1month": "1 month",
        "3month": "3 months",
        "6month": "6 months",
        "12month": "1 year",
    }

    def __init__(self, api_key, user, user_agent="LastFMStatsBot/1.0"):
        """Initialize the LastFMClient with API key and user."""
        self.api_key = api_key
        self.user = user
        self.headers = {"User-Agent": user_agent}
        self.timeout = httpx.Timeout(10.0, connect=60.0)

    async def fetch_data(self, method, period="1month", limit=10):
        """Fetch data from Last.fm asynchronously."""
        params = {
            "method": method,
            "user": self.user,
            "api_key": self.api_key,
            "format": "json",
            "period": period,
            "limit": limit,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logging.error("Request to Last.fm timed out")
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e.response.status_code}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
        return None

    def format_data(self, data, item_type="tracks", num_items=10, period="1month"):
        """
        Format top tracks or artists from Last.fm data.
        """
        key_map = {"tracks": ("toptracks", "track"), "artists": ("topartists", "artist")}

        if item_type not in key_map:
            return "Invalid item type specified."

        parent_key, child_key = key_map[item_type]
        if data and parent_key in data:
            items = data[parent_key][child_key]
            title = f"Top {num_items} {item_type.capitalize()} for last {self.PERIOD_MAPPING.get(period, period)}:\n"
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
