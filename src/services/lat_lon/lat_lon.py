__all__ = [
    "lat_lon_service",
    "LatLonService",
]

import geocoder

from src.schemas.lat_lon_schema import LatLonServiceResponse


class LatLonService:
    def __init__(self, geocoder_instance: geocoder):
        self.g = geocoder_instance.ip("me")

    def get_lat_lon(self) -> LatLonServiceResponse:
        lat, lon = self.g.latlng
        return LatLonServiceResponse(latitude=lat, longitude=lon)


lat_lon_service = LatLonService(geocoder)
