import os
import json
import time
import requests

class ScraperHelper:
    MAX_RETRIES = 3 
    APP_VERSION = '6.4.4'
    DEVICE_MODEL = 'CPH2381'
    USER_TOKEN = os.environ.get("OLA_USER_TOKEN", "")
    PICKUP_CITY = 'banglore'
    DEVICE_ID = 'd3KdG3E7TTKV_HgK_RcbEL'
    PRICE_BASE_URL = "https://apps.olacabs.com/v1/pricing"
    ETA_BASE_URL = "https://apps.olacabs.com/v1/availability"
    AUTH_TOKEN = ''

    @classmethod
    def get_price_data(cls, access_token:str, param: dict, retry: int = 0) -> dict:
        try:
            payload = cls._build_price_payload(param = param)
            headers = cls._build_headers(access_token=access_token)
            response = requests.post(
                url = cls.PRICE_BASE_URL,
                headers = headers,
                data = json.dumps(payload)
            )
            if retry == cls.MAX_RETRIES:
                return {"Not able to get data token expired"}
            if response.status_code == 401:
                access_token = cls.update_token_in_storage()
                return cls.get_price_data(param=param, access_token=access_token['token'], retry=retry + 1)
            elif response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            raise e
    
    @classmethod
    def get_eta_data(cls, param: dict, access_token: str, retry: int = 0) -> dict:
        try:
            payload = cls._build_eta_payload(param = param)
            headers = cls._build_headers(access_token=access_token)
            response = requests.post(
                url = cls.ETA_BASE_URL,
                headers = headers,
                data=json.dumps(payload)
            )
            if retry == cls.MAX_RETRIES:
                return {"Not able to get data token expired"}
            if response.status_code == 401:
                access_token = cls.update_token_in_storage()
                return cls.get_eta_data(param=param, access_token=access_token['token'], retry=retry + 1)
            elif response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            raise e


    @classmethod
    def _build_headers(cls, access_token: str) -> dict:
        return {
            'accept-encoding': 'gzip',
            'accept-language': 'en_GB',
            'api-key': '@ndro1d',
            'app_version': cls.APP_VERSION,
            'client': 'android',
            'content-type': 'application/json; charset=UTF-8',
            'device_id': cls.DEVICE_ID,
            'formatter-language': 'en_GB',
            'user-agent': 'OlaConsumerApp/6.4.4 (android/13)',
            'x-device-model': cls.DEVICE_MODEL,
            'x-os': 'android_13',
            'x-pickup-city': cls.PICKUP_CITY,
            'x-request-id': 'E510s0y7na/S2mYczZbsHs8wznI=',
            'x-session-id': '7f744cd1-9419-4e49-95b9-e3e1ecb9267c',
            'x-trace-id': '1700118531037',
            'x-user-token': cls.USER_TOKEN,
            'authorization': f"consumerapps {access_token}"
        }
    
    @staticmethod
    def _build_price_payload(param: dict) -> dict:
        lat_start = param.get('pickup_latitude', {})
        lng_start = param.get('pickup_longitude', {})
        lat_end = param.get('drop_latitude', {})
        lng_end = param.get('drop_longitude', {})
        return {
            "profile": "personal",
            "pickup": {
                "mode": "now",
                "lng": str(lng_start),
                "lat": str(lat_start)
            },
            "waypoints": [
                {
                    "lng": float(lng_end),
                    "type": 1,
                    "lat": float(lat_end)
                }
            ],
            "category_metadata": {
                "compact": {
                    "eta_enabled": True,
                    "price_enabled": True,
                    "eta_challenge": False
                },
                "kp": {
                    "eta_enabled": True,
                    "price_enabled": True,
                    "eta_challenge": False
                },
                "book_any": {
                    "eta_enabled": True,
                    "price_enabled": True,
                    "eta_challenge": False,
                    "book_any_categories": [
                        "compact",
                        "luxury_sedan"
                    ]
                },
                "economy_suv": {
                    "eta_enabled": True,
                    "price_enabled": True,
                    "eta_challenge": False
                },
                "prime_plus": {
                    "eta_enabled": True,
                    "price_enabled": True,
                    "eta_challenge": False
                },
                "luxury_sedan": {
                    "eta_enabled": True,
                    "price_enabled": True,
                    "eta_challenge": False
                },
                "cool_cab": {
                    "eta_enabled": True,
                    "price_enabled": True,
                    "eta_challenge": False
                },
                "local": {
                    "eta_enabled": True,
                    "price_enabled": True,
                    "eta_challenge": False
                }
            },
            "background_call": False,
            "preferred_instrument": {
                "profile": "personal",
                "id": "1013719492",
                "subText": "cash"
            },
            "eta_challenge_time": 0,
            "disable_update_consent": False,
            "device": {
                "lng": str(lng_start),
                "device_model": "CPH2381",
                "rooted": "False",
                "lat": str(lng_end)
            }
        }
    
    @staticmethod
    def _build_eta_payload(param: dict) -> dict:
        lat_start = param.get('pickup_latitude', {})
        lng_start = param.get('pickup_longitude', {})
        lat_end = param.get('drop_latitude', {})
        lng_end = param.get('drop_longitude', {})
        return {
            "show_book_any": True,
            "show_new_panel_design": True,
            "pickup": {
                "lng": float(lng_start),
                "lat": float(lat_start)
            },
            "rooted": "True",
            "accuracy": "5.818149",
            "zone_shown": False,
            "show_os_upsell": True,
            "waypoints": [
                {
                    "lng": float(lng_end),
                    "lat": float(lat_end)
                }
            ],
            "user_loc": {
                "lng": str(lng_end),
                "lat": str(lat_end)
            },
            "discovery_tab": "daily"
        }
    
    @classmethod 
    def update_token_in_storage(cls, token_file: str = f"app/scrapers/ola/tokens.py"):
        try:
            access_token_data = cls.refresh_token()
            new_token_data = {
                "time_generated": int(time.time()),
                **access_token_data
            }
            with open(token_file, "w") as token_file:
                token_file.write(f"tokens_list = {json.dumps([new_token_data], indent=4)}")
            return {
                "token": access_token_data.get("access_token")
            }
        except Exception as e:
            raise e
    
    @classmethod
    def refresh_token(cls):
        try:
            url = "https://apps.olacabs.com/v1/tokens/refresh"
            payload = "{\"auth_refresh_token\":\"\",\"install_id\":\"\"}"
            headers = {
                "app_version": "7.1.2",
                "device_id": "dDYSwbaETE-QzbP_wp_rD0",
                "user-agent": "OlaConsumerApp/7.1.2 (android/13)",
                "x-request-id": "vXX9uCCnsosEPNjofs8C4hpvU5A=",
                "formatter-language": "en_US",
                "x-os": "android_13",
                "api-key": "@ndro1d",
                "x-device-model": "Pixel 8 Pro",
                "client": "android",
                "accept-language": "en_US",
                "x-trace-id": "1731924874196",
                "x-session-id": "044e47a3-6480-466b-ab34-df2b1685cdc6",
                "content-type": "application/json; charset=utf-8",
                "accept-encoding": "gzip"
            }

            response = requests.post(url, data=payload, headers=headers)
            if response.status_code != 200:
                raise ReferenceError
            return response.json().get("session", {})
        except Exception as e:
            raise e
        
    @staticmethod
    def combine_data(price_data: dict, eta_data: dict) -> dict:
        try:
            flattened_data = []
            category_id_name_map = {}
            eta_id_data_raw = eta_data.get("discovery", {}).get("etas", {})
            tag_line_data_raw = eta_data.get("merchandising", {}).get("category_merchandising", {})
            eta_id_data = {}
            category_id_name_data = eta_data.get("categories", [])
            for data in category_id_name_data:
                category_id = data.get("id")
                display_name = data.get("display_name")
                eta_id_data[category_id] = eta_id_data_raw.get(category_id, {})
                category_id_name_map[category_id] = display_name
            category_data = price_data.get('category_map', {})
            category_keys = category_data.keys()
            for key in category_keys:
                if category_id_name_map.get(key) == None:
                    continue
                key_data = category_data.get(key, {})
                key_data["display_name"] = category_id_name_map.get(key)
                key_data['eta'] = eta_id_data.get(key)
                key_data['estimate_trip_distance'] =eta_data.get("discovery", {}).get('estimate_trip_distance', None)
                key_data["tag_line"] = tag_line_data_raw.get(key,{}).get('sub_text')
                flattened_data.append(key_data)

            return { 'flattened_data':flattened_data}
        except Exception as e:
            raise e

    
