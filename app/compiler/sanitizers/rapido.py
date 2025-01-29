def get_seat_capacity(data):
    if 'seatingCapacity' in data:
        return data['seatingCapacity']
    else:
        return None
    

def get_vehicle_eta(data):
    if 'pickupEtaInMin' in data:
        return data['pickupEtaInMin']
    else:
        return None
    

def get_dropEtaInMin(data):
    if 'dropEtaInMin' in data:
        return data['dropEtaInMin']
    else:
        return None
    
def get_distance_in_meter(x):
    if x:
        return x*1000
    else:   
        return None
    
def get_safe_ride_charge(data):
    unit_insurance_charges = data.get("amountBreakup", {}).get("insuranceCharges", {}).get("unit", None)
    return unit_insurance_charges

def get_per_distance_charge(data):
    per_distance_charge = data.get("amountBreakup", {}).get("distanceFare", {}).get("unit", None)
    return per_distance_charge

def per_minute_ride_charge(data):
    per_minute_ride_charge = data.get("amountBreakup", {}).get("timeFare", {}).get("unit", None)
    return per_minute_ride_charge