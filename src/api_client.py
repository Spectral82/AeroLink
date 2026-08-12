import abc
from typing import Any, Dict, List, Optional

import requests


class BaseClient(abc.ABC):
    """
    Абстрактный базовый класс для клиентов API.

    Обеспечивает единый интерфейс для работы с геоданными и данными о самолётах.
    Соблюдает принципы SOLID (Open/Closed, Liskov Substitution).
    """

    @abc.abstractmethod
    def get_country_bbox(self, country: str) -> Optional[List[float]]:
        """
        Получить bounding box страны.

        Args:
            country: Название страны.

        Returns:
            Список из 4 значений [юг, север, запад, восток] или None, если не найдено.
        """
        pass

    @abc.abstractmethod
    def get_airplanes_in_area(
        self, south: float, north: float, west: float, east: float
    ) -> List[List[Any]]:
        """
        Получить сырые данные о самолётах в заданной прямоугольной области.

        Args:
            south: Южная граница (широта).
            north: Северная граница (широта).
            west: Западная граница (долгота).
            east: Восточная граница (долгота).

        Returns:
            Список списков с данными о самолётах (сырой формат API).
        """
        pass


class NominatimClient(BaseClient):
    """
    Клиент для работы с Nominatim (OpenStreetMap).

    Используется для получения географических границ (bounding box) стран.
    Не предназначен для получения данных о полётах.
    """

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def __init__(self, user_agent: str = "aero-project/1.0"):
        """
        Инициализирует клиент с пользовательским агентом.

        Args:
            user_agent: Значение заголовка User-Agent для соблюдения правил API.
        """
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})

    def _request(self, url: str, params: Optional[Dict[str, Any]] = None):
        """
        Выполняет HTTP GET-запрос к API.

        Args:
            url: Целевой URL.
            params: Параметры запроса.

        Returns:
            JSON-ответ от сервера.

        Raises:
            RuntimeError: При ошибке сетевого запроса.
        """
        try:
            resp = self._session.get(url, params=params or {}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Ошибка запроса к Nominatim: {e}") from e

    def get_country_bbox(self, country: str) -> Optional[List[float]]:
        """
        Получает bounding box для указанной страны через Nominatim.

        Args:
            country: Название страны.

        Returns:
            [юг, север, запад, восток] при успехе, иначе None.
        """
        params = {"country": country, "format": "json", "limit": 1}
        data = self._request(self.BASE_URL, params)
        if not data:
            return None

        place = data[0]
        bbox_str = place.get("boundingbox")
        if not bbox_str or len(bbox_str) != 4:
            return None

        try:
            bbox = [float(x) for x in bbox_str]
            if bbox[0] >= bbox[1] or bbox[2] >= bbox[3]:
                return None
            return bbox
        except (ValueError, TypeError):
            return None

    def get_airplanes_in_area(self, *args, **kwargs) -> List[List[Any]]:
        """
        Заглушка: Nominatim не предоставляет данные о самолётах.

        Returns:
            Пустой список.
        """
        return []


class OpenSkyClient(BaseClient):
    """
    Клиент для работы с OpenSky Network API.

    Предназначен для получения текущих состояний воздушных судов
    в заданной географической области.
    """

    BASE_URL = "https://opensky-network.org/api/states/all"

    def __init__(self) -> None:
        """Инициализирует HTTP-сессию для запросов к OpenSky."""
        self._session = requests.Session()

    def _request(self, url: str, params: Optional[Dict[str, Any]] = None):
        """
        Выполняет HTTP GET-запрос к OpenSky API.

        Args:
            url: Целевой URL.
            params: Параметры запроса.

        Returns:
            JSON-ответ от сервера.

        Raises:
            RuntimeError: При ошибке сетевого запроса.
        """
        try:
            resp = self._session.get(url, params=params or {}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Ошибка запроса к OpenSky: {e}") from e

    def get_country_bbox(self, *args, **kwargs) -> Optional[List[float]]:
        """
        Заглушка: OpenSky не предоставляет геограницы стран.

        Returns:
            None.
        """
        return None

    def get_airplanes_in_area(
        self, south: float, north: float, west: float, east: float
    ) -> List[List[Any]]:
        """
        Получает данные о самолётах в прямоугольной области через OpenSky.

        Args:
            south: Южная граница (lamin).
            north: Северная граница (lamax).
            west: Западная граница (lomin).
            east: Восточная граница (lomax).

        Returns:
            Сырой список состояний самолётов из API (поле states).
        """
        params = {
            "lamin": south,
            "lamax": north,
            "lomin": west,
            "lomax": east,
        }
        response = self._request(self.BASE_URL, params)
        states = response.get("states", [])
        if not isinstance(states, list):
            return []
        return states
