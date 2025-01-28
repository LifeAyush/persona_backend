from ..config import ENABLED_APPS
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..loader import ScraperLoader

def fetch_fare(pickup_lat: float, pickup_long: float, drop_lat: float, drop_long: float, country_code: str) -> dict:
    """
    Mock function to calculate fare based on coordinates.
    Uses a simplified distance calculation and adds some mock pricing logic.
    """
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for app_name in ENABLED_APPS:
            scraper = ScraperLoader.initialize_scraper(app_name)
            payload = {
                'pickup_latitude': pickup_lat,
                'pickup_longitude': pickup_long,
                'drop_latitude': drop_lat,
                'drop_longitude': drop_long,
                'country_code': country_code
            }
            futures[executor.submit(scraper.scrape, payload)] = app_name
        result = {futures[future]: future.result() for future in as_completed(futures)}        
    return result

__all__ = [
    "fetch_fare",
]