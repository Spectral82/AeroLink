from typing import List

from adapter import AirplaneAdapter
from airplanes import Aeroplane
from api_client import NominatimClient, OpenSkyClient
from storage import JSONSaver


class AeroplanesAPI:
    """
    Оркестратор: связывает API, адаптер и хранилище.
    Соответствует примеру: api = AeroplanesAPI(); aeroplanes = api.get_aeroplanes('Spain')
    """

    def __init__(self, storage_path: str = "airplanes.json"):
        self.nominatim = NominatimClient()
        self.opensky = OpenSkyClient()
        self.saver = JSONSaver(storage_path)
        self.adapter = AirplaneAdapter()

    def get_aeroplanes(self, country: str) -> List[Aeroplane]:
        bbox = self.nominatim.get_country_bbox(country)
        if bbox is None:
            raise ValueError(
                f"Не удалось найти страну '{country}'. Проверьте название."
            )

        south, north, west, east = bbox
        raw_states = self.opensky.get_airplanes_in_area(south, north, west, east)

        planes = self.adapter.from_opensky_states(raw_states)

        for p in planes:
            self.saver.add_aeroplane(p)

        return planes
