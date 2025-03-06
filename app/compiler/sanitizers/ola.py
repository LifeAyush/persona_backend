def get_vehicle_fare(value):
    fare = value.get('pricing', {}).get("fare", {}).get("default", {}).get("value")
    if fare:
        if '-' in fare:
            return sum(map(float,fare.split('-')))/2
        else:
            return float(fare)
    else:
        return None

def get_vehicle_eta(value):
    return value.get('eta', {}).get('value')

def ola(value):
    return 'ola'

def ola(value):
    return 'client'