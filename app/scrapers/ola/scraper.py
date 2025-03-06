import random
import os
import logging
from datetime import datetime, timezone
from .tokens import tokens_list
from ..base import Scraper as BaseScraper
from .scraper_helper import ScraperHelper

class Scraper(BaseScraper):
    def __init__(self):
        self.name = "ola"
        self.auth_token = random.choice(tokens_list).get('access_token')
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
        param = {
            "pickup_latitude" : route.get('pickup_latitude'),
            "pickup_longitude": route.get('pickup_longitude'),
            "drop_latitude": route.get('drop_latitude'),
            "drop_longitude": route.get('drop_longitude')
        }
        price_data = ScraperHelper.get_price_data(param=param, access_token=self.auth_token)
        eta_data = ScraperHelper.get_eta_data(param=param, access_token=self.auth_token)
        raw_data = ScraperHelper.combine_data(price_data=price_data, eta_data=eta_data)
        print(raw_data)
        raw_data.update(param)
        return {"raw_data": raw_data}