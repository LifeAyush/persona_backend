import requests
import logging
from datetime import datetime, timezone
import random
from .tokens import tokens_list

class ScraperHelper:
    BASE_URL = "https://api.moving.tech/pilot/app/v2/rideSearch"
    API_TOKEN = random.choice(tokens_list)
    DEVICE_INFO = "samsung/SM-N935F/Android v13/2 GB/20.73 Inches/1280x768px/mf:samsung"
    APP_VERSION = "2.5.16"
    BUNDLE_VERSION = "3.0.147"
    CONFIG_VERSION = "2.0.12"

    @classmethod
    def get_search_id(cls, session_id: str, client_id: str, pickup_lat: float, pickup_lon: float, drop_lat: float, drop_lon: float) -> str:
        try:
            headers = cls._build_headers(session_id, client_id)
            payload = cls._build_payload(pickup_lat, pickup_lon, drop_lat, drop_lon)
            
            for attempt in range(3):
                try:
                    response = requests.post(
                        cls.BASE_URL,
                        headers=headers,
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        search_id = data.get('searchId')
                        if search_id:
                            logging.info(f"Search ID obtained successfully: {search_id}")
                            return search_id
                        else:
                            logging.error("Search ID not found in response")
                    else:
                        logging.error(f"Request failed with status code: {response.status_code}")
                        
                except Exception as e:
                    logging.error(f"Attempt {attempt + 1} failed: {e}")
                    
            return None
                    
        except Exception as e:
            logging.error(f"Failed to get search ID: {e}")
            return None

    @classmethod
    def _build_headers(cls, session_id: str, client_id: str) -> dict:
        return {
            "accept-encoding": "gzip",
            "accept-language": "en-US,en;q=0.5",
            "client-id": client_id,
            "connection": "Keep-Alive",
            "content-type": "application/json",
            "host": "api.moving.tech",
            "referer": "in.juspay.nammayatri",
            "session_id": session_id,
            "token": cls.API_TOKEN,
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 13; Nexus 4 Build/TQ2B.230505.005.A1)",
            "x-app-name": "godel",
            "x-bundle-version": cls.BUNDLE_VERSION,
            "x-client-id": "nammayatriconsumer",
            "x-client-version": cls.APP_VERSION,
            "x-config-version": cls.CONFIG_VERSION,
            "x-device": cls.DEVICE_INFO,
            "x-merchant-id": "nammayatri",
            "x-powered-by": "Juspay EC SDK for Android"
        }

    @classmethod
    def _build_payload(cls, pickup_lat: float, pickup_lon: float, drop_lat: float, drop_lon: float) -> dict:
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        
        return {
            "fareProductType": "INTER_CITY",
            "contents": {
                "stops": [
                    {
                        "gps": {
                            "lon": drop_lon,
                            "lat": drop_lat
                        },
                        "address": {}
                    }
                ],
                "startTime": current_time,
                "roundTrip": False,
                "returnTime": None,
                "origin": {
                    "gps": {
                        "lon": pickup_lon,
                        "lat": pickup_lat
                    },
                    "address": {}
                },
                "isReallocationEnabled": True
            }
        }