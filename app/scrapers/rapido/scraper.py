import os
import gzip
import requests
import json
import logging
import random
from datetime import datetime
from datetime import datetime, timezone
from ..base import Scraper as BaseScraper
from .tokens import tokens_list
from ...loader.scarper_loader import ScraperLoader
from ...config import ENABLED_APPS
from concurrent.futures import ThreadPoolExecutor, as_completed

class Scraper(BaseScraper):
    def __init__(self):
        self.name = "rapido"
        self.auth_token = random.choice(tokens_list)
        self.device_id = 'ff1bb73feda43c9e'
        self.key = 'r@pido333'
        self.current_time = datetime.now(tz=timezone.utc).strftime("%H-00")
        self.current_hour = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H-00-00Z")
        self.current_timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        self.current_date = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
        self.base_folder = f"data/rapido"
        self.make_folders(self.base_folder, self.current_date, self.current_time)
        
    def make_folders(self,base_folder, current_date, current_time):
        # Making all the directories required
        raw_folder = f"{base_folder}/raw"
        raw_date_time_folder = f"{raw_folder}/{current_date}/{current_time}"
        compile_folder_path = f"{base_folder}/compile"
        compile_date_time_folder = f"{compile_folder_path}/{current_date}/{current_time}"
        compressFolder = f"{base_folder}/compressed"
        try:
            self.create_directory(raw_date_time_folder)
            self.create_directory(compile_date_time_folder)
            self.create_directory(compressFolder)
        except Exception as e:
            logging.error(f"Error in creating directories: {e}")    
    
    def create_directory(self,folder_path):
        try:
            os.makedirs(folder_path, exist_ok=True)
            logging.info(f"Directory {folder_path} created succesfully!")
        except Exception as e:
            logging.error(f"Error in creating {folder_path} err is: {e}")
        
    def scrape(self, route: dict, account_manager: object= None)-> dict:
        logging.info(f"Scraping started for: {route.get('pickup_latitude')}, {route.get('pickup_longitude')}, {route.get('drop_latitude')}, {route.get('drop_longitude')}")
        raw_data = self.get_data(route)
        return {
            "raw_data": raw_data
        }
        # scraping_status = raw_data.pop("status")
        # if scraping_status:
        #     return {
        #         "filesMapping" : [
        #             {
        #                 "file_code": "API_RESPONSE_WITH_METADATA",
        #                 "file_description": "Scraped API Responses",
        #                 **raw_data
        #             }
        #         ],
        #         "status" : True,
        #     }
        # else:
        #     return {
        #         "status": False,
        #         "status_code": raw_data.get("status_code")
        #     }
    
    def get_data(self,routes):
        try:
            pickup_lat = routes.get('pickup_latitude')
            pickup_lng = routes.get('pickup_longitude')
            drop_lat = routes.get('drop_latitude')
            drop_lng = routes.get('drop_longitude')
            city = routes.get('city')
            raw_data = self.get_fare_estimate(pickup_lat, pickup_lng, drop_lat, drop_lng,city)
            response = self.fill_response(raw_data , routes, self.current_hour, self.current_timestamp)
            new_compressed_file_path = f"""{routes.get("pickup_latitude")}_{routes.get("pickup_longitude")}_{routes.get("drop_latitude")}_{routes.get("drop_longitude")}.json.gz"""
            compressed_data = gzip.compress(json.dumps(response).encode('utf-8'))
            directory = f"{self.base_folder}/raw/{self.current_date}/{self.current_time}"
            os.makedirs(directory, exist_ok=True)
            compressed_file_path = f'{directory}/{routes.get("pickup_latitude")}_{routes.get("pickup_longitude")}_{routes.get("drop_latitude")}_{routes.get("drop_longitude")}.json.gz'
            with open(compressed_file_path, "wb") as file:
                file.write(compressed_data)
            current_date_time = datetime.now(tz=timezone.utc)
            return raw_data
            # return {
            #         "status": True,
            #         "file_path": compressed_file_path,
            #         "suffix_key": new_compressed_file_path,
            #         "scraped_at": current_date_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            #         "scraped_at_hour": current_date_time.strftime("%Y-%m-%dT%H:00:00Z"),
            #         "country_code": routes.get("country_code"),
            #     }
        except Exception as e:
            logging.error(f"Error in get_data function: {e}")
            return {
                "status": False
            }        

    def get_fare_estimate(self, pickup_lat: float, pickup_lng: float, drop_lat: float, drop_lng: float,city):
        url = "https://customer.rapido.bike/android/fare/estimates"

        headers = {
            'accept': 'application/json,application/protobuf',
            'accept-charset': 'UTF-8,ISO-8859-1;q=0.1',
            'accept-encoding': 'gzip',
            'app_variant': 'v8',
            'appid': '2',
            'appversion': '431',
            'appversionstring': '8.42.0',
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
            'key': self.key,
            'latitude': str(pickup_lat),
            'longitude': str(pickup_lng),
            'user-agent': 'Ktor client'
        }

        payload = json.dumps({
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
        })

        for i in range(3):  # Retry mechanism
            print(f"Attempt {i + 1}: Requesting fare estimate...")
            response = requests.post(url, headers=headers, data=payload)
            # print(f"Response {response.status_code}: {response.text}")
            if response.status_code == 200:
                result = {}
                try:
                    response_json = response.json()  # Extract JSON data from response
                    return response_json
                except ValueError:
                    print("Failed to parse response as JSON")
                    response_json = response.json() 
                    return response_json

        print("Failed to fetch fare estimate after 3 retries.")
        return None
    
    def fill_response(self,response, route_data, current_hour, current_timestamp):
        try:
            response['source'] = "rapido"
            response["pickup_zone"] = route_data.get("pickup_zone")
            response['pickup_latitude'] = route_data.get("pickup_latitude")
            response['pickup_longitude'] = route_data.get("pickup_longitude")
            response['drop_latitude'] = route_data.get("drop_latitude")
            response['drop_longitude'] = route_data.get("drop_longitude")
            response["drop_zone"] = route_data.get("drop_zone")
            response["city"] = route_data.get("city")
            response["country_code"] = route_data.get("country_code")
            response["route_type"] = route_data.get("route_type")
            response['scraped_at_hour'] = current_hour
            response['scraped_at_timestamp'] = current_timestamp
            response['client'] = "namma_yatri"
            response['payload_distance'] = route_data.get('distance')
            response['route_id'] = f'{current_hour}-{route_data.get("pickup_latitude")}-{route_data.get("pickup_longitude")}-{route_data.get("drop_latitude")}-{route_data.get("drop_longitude")}'
            logging.info(
                f'Filled the response with the required details for the location: {route_data.get("pickup_latitude")}, {route_data.get("pickup_longitude")}, {route_data.get("drop_latitude")}, {route_data.get("drop_longitude")}\n Data: {response}')
        except Exception as e:
            message = f'<<SPOT>>Error occurred in fill_response for location: {route_data.get("pickup_latitude")}, {route_data.get("pickup_longitude")}, {route_data.get("drop_latitude")}, {route_data.get("drop_longitude")}, Continuing to the next request!'
            self.send_slack_message(message)
            # print(message)
            logging.error(message)
        return response

    