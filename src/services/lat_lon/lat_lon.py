__all__ = [
    "lat_lon_service",
]

import geocoder


class GetLatLon:
    def __init__(self):
        self.g = geocoder.ip("me")

    def get_lat_lon(self):
        return self.g.latlng


lat_lon_service = GetLatLon()
