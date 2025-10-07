__all__ = [
    "lat_lon_service",
]

import geocoder

from src.schemas.lat_lon_response import LatLonServiceResponse


class GetLatLon:
    def __init__(self):
        self.g = geocoder.ip("me")

    def get_lat_lon(self) -> LatLonServiceResponse:
        lat, lon = self.g.latlng
        return LatLonServiceResponse(latitude=lat, longitude=lon)


lat_lon_service = GetLatLon()
