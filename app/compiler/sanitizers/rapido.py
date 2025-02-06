def get_vehicle_eta(data):
    if 'pickupEtaInMin' in data:
        return data['pickupEtaInMin']
    else:
        return None