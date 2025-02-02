import os
import gzip
import json
import logging
import uuid
import requests
import random
from .tokens import tokens_list
from datetime import datetime, timezone
from ..base import Scraper as BaseScraper
from .scraper_helper import ScraperHelper

class Scraper(BaseScraper):
    BASE_URL = "https://api.moving.tech/pilot/app/v2/rideSearch"
    APP_VERSION = "2.5.16"
    BUNDLE_VERSION = "3.0.147"
    CONFIG_VERSION = "2.0.12"
    DEVICE_INFO = "samsung/SM-N935F/Android v13/2 GB/20.73 Inches/1280x768px/mf:samsung"
    
    def __init__(self):
        self.name = "namma_yatri"
        self.session_id = str(uuid.uuid4())
        self.client_id = str(uuid.uuid4())
        self.auth_token = random.choice(tokens_list)
        self._setup_timestamps()
        self._setup_directories()
        
    def _setup_timestamps(self):
        now = datetime.now(tz=timezone.utc)
        self.current_time = now.strftime("%H-00")
        self.current_hour = now.strftime("%Y-%m-%dT%H-00-00Z")
        self.current_timestamp = now.strftime("%Y-%m-%dT%H-%M-%SZ")
        self.current_date = now.strftime("%Y-%m-%d")
        
    def _setup_directories(self):
        self.base_folder = "data/namma_yatri"
        folders = [
            f"{self.base_folder}/raw/{self.current_date}/{self.current_time}",
            f"{self.base_folder}/compile/{self.current_date}/{self.current_time}",
            f"{self.base_folder}/compressed"
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
        search_id = self._get_search_id(route)
        if not search_id:
            return {"status": False, "error": "Failed to obtain search ID"}
            
        raw_data = self._get_data(route, search_id)
        return {"raw_data": raw_data}
        
    def _get_search_id(self, route):
        return ScraperHelper.get_search_id(
            self.session_id,
            self.client_id,
            route.get('pickup_latitude'),
            route.get('pickup_longitude'),
            route.get('drop_latitude'),
            route.get('drop_longitude')
        )
    
    def _get_data(self, route, search_id):
        try:
            raw_data = self._get_fare_estimate(search_id)
            response = self._fill_response(raw_data, route, search_id)
            self._save_compressed_response(response, route)
            return raw_data
            
        except Exception as e:
            logging.error(f"Data retrieval failed: {e}")
            return {"status": False}
            
    def _get_fare_estimate(self, search_id):
        headers = self._build_headers()
        url = f"{self.BASE_URL}/{search_id}/results"
        
        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json()
                logging.warning(f"Attempt {attempt + 1} failed with status code: {response.status_code}")
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                
        logging.error("All fare estimate attempts failed")
        return None
        
    def _build_headers(self):
        return {
            "x-client-version": self.APP_VERSION,
            "x-bundle-version": self.BUNDLE_VERSION,
            "session_id": self.session_id,
            "x-device": self.DEVICE_INFO,
            "client-id": self.client_id,
            "x-config-version": self.CONFIG_VERSION,
            "content-type": "application/json",
            "token": self.auth_token,
            "x-merchant-id": "nammayatri",
            "x-client-id": "nammayatriconsumer",
            "x-app-name": "godel",
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 13; Nexus 4 Build/TQ2B.230505.005.A1)",
            "referer": "in.juspay.nammayatri",
            "accept-language": "en-US,en;q=0.5",
            "x-powered-by": "Juspay EC SDK for Android",
            "host": "api.moving.tech",
            "connection": "Keep-Alive",
            "accept-encoding": "gzip"
        }
        
    def _fill_response(self, response, route_data, search_id):
        try:
            response.update({
                'source': "namma_yatri",
                'search_id': search_id,
                'session_id': self.session_id,
                'client_id': self.client_id,
                'pickup_zone': route_data.get("pickup_zone"),
                'pickup_latitude': route_data.get("pickup_latitude"),
                'pickup_longitude': route_data.get("pickup_longitude"),
                'drop_latitude': route_data.get("drop_latitude"),
                'drop_longitude': route_data.get("drop_longitude"),
                'drop_zone': route_data.get("drop_zone"),
                'city': route_data.get("city"),
                'country_code': route_data.get("country_code"),
                'route_type': route_data.get("route_type"),
                'scraped_at_hour': self.current_hour,
                'scraped_at_timestamp': self.current_timestamp,
                'client': "nammayatri",
                'payload_distance': route_data.get('distance'),
                'route_id': f'{self.current_hour}-{route_data.get("pickup_latitude")}-{route_data.get("pickup_longitude")}-{route_data.get("drop_latitude")}-{route_data.get("drop_longitude")}'
            })
            return response
        except Exception as e:
            logging.error(f"Response filling failed for search ID {search_id}: {e}")
            return response
            
    def _save_compressed_response(self, response, route):
        filename = f"{route.get('pickup_latitude')}_{route.get('pickup_longitude')}_{route.get('drop_latitude')}_{route.get('drop_longitude')}.json.gz"
        directory = f"{self.base_folder}/raw/{self.current_date}/{self.current_time}"
        file_path = f"{directory}/{filename}"
        
        try:
            compressed_data = gzip.compress(json.dumps(response).encode('utf-8'))
            with open(file_path, "wb") as file:
                file.write(compressed_data)
            logging.info(f"Compressed response saved: {file_path}")
        except Exception as e:
            logging.error(f"Failed to save compressed response: {e}")