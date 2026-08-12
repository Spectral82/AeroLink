from typing import Any, List

from src.airplanes import Aeroplane


class AirplaneAdapter:
    """
    Адаптер для преобразования сырых данных OpenSky Network в объекты Aeroplane.
    Отвечает за трансформацию данных (Single Responsibility).
    """

    @staticmethod
    def from_opensky_row(row: List[Any]) -> Aeroplane:
        """
        Преобразует строку состояния самолёта из API OpenSky в объект Aeroplane.

        Args:
            row: Список данных (минимум 17 полей).

        Returns:
            Объект Aeroplane с заполненными полями.

        Raises:
            ValueError: Если формат строки некорректен (менее 17 элементов).
        """
        if not isinstance(row, list) or len(row) < 17:
            raise ValueError(
                "Некорректный формат строки состояния самолёта: ожидается список из 17+ элементов."
            )

        def _to_str(val, default: str = "Unknown") -> str:
            return str(val).strip() if val is not None else default

        def _to_float(val, default: float = 0.0) -> float:
            try:
                return float(val) if val is not None else default
            except (TypeError, ValueError):
                return default

        def _to_int(val, default: int = 0) -> int:
            try:
                return int(val) if val is not None else default
            except (TypeError, ValueError):
                return default

        def _to_bool(val, default: bool = False) -> bool:
            if val is None:
                return default
            return bool(val)

        return Aeroplane(
            icao24=_to_str(row[0]),
            callsign=_to_str(row[1]),
            origin_country=_to_str(row[2]),
            time_position=_to_int(row[3]),
            last_contact=_to_int(row[4]),
            longitude=_to_float(row[5]),
            latitude=_to_float(row[6]),
            baro_altitude=_to_float(row[7]),
            on_ground=_to_bool(row[8]),
            velocity=_to_float(row[9]),
            true_track=_to_float(row[10]),
            vertical_rate=_to_float(row[11]),
            sensors=row[12],
            geo_altitude=_to_float(row[13]),
            squawk=_to_str(row[14]),
            spi=_to_bool(row[15]),
            position_source=_to_int(row[16]),
        )

    @classmethod
    def from_opensky_states(cls, states: List[List[Any]]) -> List[Aeroplane]:
        """
        Преобразует список строк состояний самолётов (OpenSky) в список объектов Aeroplane.
        Некорректные строки пропускаются без прерывания обработки.

        Args:
            states: Список списков — сырые данные от OpenSky API.

        Returns:
            Список валидных объектов Aeroplane.
        """
        result: List[Aeroplane] = []
        for row in states:
            try:
                plane = cls.from_opensky_row(row)
                result.append(plane)
            except ValueError:
                continue
        return result
