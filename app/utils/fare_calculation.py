from ..config import ENABLED_APPS
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..loader import ScraperLoader
from ..compiler.generic_compiler import GenericCompiler

def fetch_fare(pickup_lat: float, pickup_long: float, drop_lat: float, drop_long: float, country_code: str, **kwargs) -> dict:
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
                'country_code': country_code,
                'route_type': kwargs.get("route_type", "client")
            }
            futures[executor.submit(scraper.scrape, payload)] = app_name
        raw_data = {futures[future]: future.result() for future in as_completed(futures)}

    compiled_data = {}
    for app_name in ENABLED_APPS:
        print(raw_data[app_name].get("raw_data", {}))
        if not raw_data[app_name].get("raw_data", {}):
            compiled_data[app_name] = {}
        else:
            generic_compiler = GenericCompiler(app_name, raw_data[app_name].get("raw_data", {}))
            compiled_data[app_name] = generic_compiler.compile_data()
    return compiled_data

__all__ = [
    "fetch_fare",
]