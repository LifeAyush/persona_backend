from typing import Dict, List
    
def convert_to_delivery_format(fare_details: Dict[str, List[Dict]]) -> dict[str, List[dict]]:
    formatted_data = {}

    for app_name, app_data in fare_details.items():
        key = f"{app_name.upper()}_DATA"
        formatted_data[key] = [
            {
                "vehicle_category": vehicle["vehicle_category"],
                "price": vehicle["upfront_fare"],
                "eta": vehicle["vehicle_eta"],
            }
            for vehicle in app_data
        ]

    return formatted_data
