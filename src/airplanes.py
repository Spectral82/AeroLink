from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Aeroplane:
    """
    Модель самолёта: хранит телеметрические данные и реализует логику сравнения.

    Содержит 17 атрибутов с корректными типами (str, int, float, bool, Optional).
    Поддерживает сравнение по высоте (стандартные операторы)
    и по скорости (compare_by_velocity).
    """

    icao24: str
    callsign: str
    origin_country: str
    time_position: int
    last_contact: int
    longitude: float
    latitude: float
    baro_altitude: float
    on_ground: bool
    velocity: float
    true_track: float
    vertical_rate: float
    sensors: Optional[Any]
    geo_altitude: float
    squawk: str
    spi: bool
    position_source: int

    def __lt__(self, other: "Aeroplane") -> bool:
        """
        Проверяет, ниже ли текущий самолёт другого (по geo_altitude).

        Args:
            other: Другой объект Aeroplane.

        Returns:
            True, если высота текущего самолёта меньше.
        """
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.geo_altitude < other.geo_altitude

    def __le__(self, other: "Aeroplane") -> bool:
        """
        Проверяет, не выше ли текущий самолёт другого (по geo_altitude).

        Args:
            other: Другой объект Aeroplane.

        Returns:
            True, если высота текущего самолёта <= высоты другого.
        """
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.geo_altitude <= other.geo_altitude

    def __gt__(self, other: "Aeroplane") -> bool:
        """
        Проверяет, выше ли текущий самолёт другого (по geo_altitude).

        Args:
            other: Другой объект Aeroplane.

        Returns:
            True, если высота текущего самолёта больше.
        """
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.geo_altitude > other.geo_altitude

    def __ge__(self, other: "Aeroplane") -> bool:
        """
        Проверяет, не ниже ли текущий самолёт другого (по geo_altitude).

        Args:
            other: Другой объект Aeroplane.

        Returns:
            True, если высота текущего самолёта >= высоты другого.
        """
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.geo_altitude >= other.geo_altitude

    def compare_by_velocity(self, other: "Aeroplane") -> int:
        """
        Сравнивает самолёты по скорости полёта.

        Args:
            other: Другой объект Aeroplane для сравнения.

        Returns:
            -1 — если текущий медленнее,
             1 — если быстрее,
             0 — если скорости равны.

        Raises:
            TypeError: Если other не является экземпляром Aeroplane.
        """
        if not isinstance(other, Aeroplane):
            raise TypeError("Сравнение возможно только с другим объектом Aeroplane.")
        if self.velocity < other.velocity:
            return -1
        elif self.velocity > other.velocity:
            return 1
        return 0

    def __repr__(self) -> str:
        """
        Возвращает читаемое строковое представление объекта.

        Формат: Aeroplane(callsign=..., country=..., velocity=... м/с, geo_altitude=... м)

        Returns:
            Строка с ключевыми параметрами самолёта.
        """
        return (
            f"Aeroplane(callsign={self.callsign!r}, country={self.origin_country!r}, "
            f"velocity={self.velocity:.1f} м/с, geo_altitude={self.geo_altitude:.1f} м)"
        )
