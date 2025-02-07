import os
import gzip
import json
import logging
import random
import requests
from datetime import datetime, timezone
from ..base import Scraper as BaseScraper
from .tokens import tokens_list

class Scraper(BaseScraper):
    BASE_URL = "https://customer.rapido.bike/android/fare/estimates"
    APP_VERSION = "8.42.0"
    APP_VERSION_CODE = "431"
    APP_KEY = "r@pido333"
    DEFAULT_DEVICE_ID = "ff1bb73feda43c9e"
    
    def __init__(self):
        self.name = "rapido"
        self.auth_token = random.choice(tokens_list)
        self.device_id = self.DEFAULT_DEVICE_ID
        self._setup_timestamps()
        self._setup_directories()
        
    def _setup_timestamps(self):
        now = datetime.now(tz=timezone.utc)
        self.current_time = now.strftime("%H-00")
        self.current_hour = now.strftime("%Y-%m-%dT%H-00-00Z")
        self.current_timestamp = now.strftime("%Y-%m-%dT%H-%M-%SZ")
        self.current_date = now.strftime("%Y-%m-%d")
        
    def _setup_directories(self):
        self.base_folder = "data/rapido"
        folders = [
            f"{self.base_folder}/raw/{self.current_date}/{self.current_time}"
        ]
        for folder in folders:
            self._create_directory(folder)
            
    def _create_directory(self, folder_path):
        try:
            os.makedirs(folder_path, exist_ok=True)
            logging.info(f"Directory created: {folder_path}")
        except Exception as e:
            logging.error(f"Failed to create directory {folder_path}: {e}")
            
    def scrape(self, route: dict, account_manager: object = None) -> dict:
        logging.info(f"Starting scrape for coordinates: {route.get('pickup_latitude')}, {route.get('pickup_longitude')}")
        raw_data = self._get_data(route)
        return {"raw_data": raw_data}
    
    def _get_data(self, route):
        try:
            raw_data = self._get_fare_estimate(
                route.get('pickup_latitude'),
                route.get('pickup_longitude'),
                route.get('drop_latitude'),
                route.get('drop_longitude'),
                route.get('city')
            )
            return raw_data
            
        except Exception as e:
            logging.error(f"Data retrieval failed: {e}")
            return {"status": False}
            
    def _get_fare_estimate(self, pickup_lat: float, pickup_lng: float, drop_lat: float, drop_lng: float, city: str):
        headers = self._build_headers(pickup_lat, pickup_lng, city)
        payload = self._build_payload(pickup_lat, pickup_lng, drop_lat, drop_lng, city)
        
        for attempt in range(3):
            try:
                response = requests.post(self.BASE_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                
        logging.error("All fare estimate attempts failed")
        return None
        
    def _build_headers(self, pickup_lat, pickup_lng, city):
        return {
            'accept': 'application/json,application/protobuf',
            'accept-charset': 'UTF-8,ISO-859-1;q=0.1',
            'accept-encoding': 'gzip',
            'app_variant': 'v8',
            'appid': '2',
            'appversion': self.APP_VERSION_CODE,
            'appversionstring': self.APP_VERSION,
            'authorization': self.auth_token,
            'channel-entity': 'customer',
            'channel-host': 'android',
            'channel-name': 'app',
            'city': city,
            'connection': 'Keep-Alive',
            'content-type': 'application/json',
            'currentdatetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'deviceid': self.device_id,
            'host': 'customer.rapido.bike',
            'key': self.APP_KEY,
            'latitude': str(pickup_lat),
            'longitude': str(pickup_lng),
            'user-agent': 'Ktor client'
        }
        
    def _build_payload(self, pickup_lat, pickup_lng, drop_lat, drop_lng, city):
        return {
            "pickupLocation": {
                "lat": pickup_lat,
                "lng": pickup_lng,
                "locationType": "gps",
                "placeIdProvider": "google_odrd"
            },
            "dropLocation": {
                "lat": drop_lat,
                "lng": drop_lng,
                "locationType": "static_recos",
                "placeIdProvider": "google"
            },
            "paymentType": "cash",
            "upiAppName": "",
            "couponCode": "",
            "locationAccuracy": 0,
            "applyAutoAppliedOffer": True,
            "checkUserRole": True,
            "currentCity": city,
            "skipMultiFareEstimates": False,
            "skipSnapToRoad": True
        }
        
            