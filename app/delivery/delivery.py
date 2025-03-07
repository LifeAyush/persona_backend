from typing import Dict, List
    
def convert_to_delivery_format(fare_details: Dict[str, List[Dict]]) -> dict[str, List[dict]]:
    formatted_data = {}
    for app_name, app_data in fare_details.items():
        unique_vehicle_categorys = set()
        key = f"{app_name.upper()}_DATA"
        formatted_data[key] = []
        for vehicle in app_data:
            if vehicle["vehicle_category"] in unique_vehicle_categorys:
                continue
            unique_vehicle_categorys.add(vehicle["vehicle_category"])
            formatted_data[key].append({
                "vehicle_category": vehicle["vehicle_category"],
                "price": vehicle["upfront_fare"],
                "eta": vehicle["vehicle_eta"],
            })

    return formatted_data
