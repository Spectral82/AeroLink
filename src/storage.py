import json
import os
from typing import List

from src.airplanes import Aeroplane


class JSONSaver:
    """
    Хранилище для списка самолётов в формате JSON.

    Отвечает только за сохранение/загрузку данных (Single Responsibility).
    Гарантирует валидный JSON и дедупликацию по callsign при добавлении.
    """

    def __init__(self, filepath: str = "airplanes.json"):
        """
        Инициализирует хранилище и загружает существующие данные.

        Args:
            filepath: Путь к JSON‑файлу.
        """
        self.filepath = filepath
        self._data: List[dict] = []
        self._load()

    def _load(self) -> None:
        """
        Загружает данные из JSON‑файла.

        Если файл не существует или содержит некорректный JSON,
        устанавливает пустой список.
        """
        if not os.path.exists(self.filepath):
            self._data = []
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self._data = data
                else:
                    self._data = []
        except (json.JSONDecodeError, IOError):
            self._data = []

    def _save(self) -> None:
        """
        Сохраняет текущие данные в JSON‑файл.

        Raises:
            RuntimeError: Если запись в файл не удалась.
        """
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise RuntimeError(f"Не удалось сохранить JSON: {e}") from e

    def add_aeroplane(self, plane: Aeroplane) -> None:
        """
        Добавляет самолёт в хранилище, заменяя запись с тем же callsign.

        Аргумент:
            plane: Объект Aeroplane для сохранения.
        """
        record = {
            "icao24": plane.icao24,
            "callsign": plane.callsign,
            "origin_country": plane.origin_country,
            "time_position": plane.time_position,
            "last_contact": plane.last_contact,
            "longitude": plane.longitude,
            "latitude": plane.latitude,
            "baro_altitude": plane.baro_altitude,
            "on_ground": plane.on_ground,
            "velocity": plane.velocity,
            "true_track": plane.true_track,
            "vertical_rate": plane.vertical_rate,
            "sensors": plane.sensors,
            "geo_altitude": plane.geo_altitude,
            "squawk": plane.squawk,
            "spi": plane.spi,
            "position_source": plane.position_source,
        }
        self._data = [r for r in self._data if r.get("callsign") != plane.callsign]
        self._data.append(record)
        self._save()

    def delete_aeroplane(self, callsign: str) -> bool:
        """
        Удаляет самолёт по callsign.

        Args:
            callsign: Позывной самолёта для удаления.

        Returns:
            True, если запись была удалена; False, если не найдена.
        """
        before_len = len(self._data)
        self._data = [r for r in self._data if r.get("callsign") != callsign]
        changed = len(self._data) < before_len
        if changed:
            self._save()
        return changed

    def get_all_as_objects(self) -> List[Aeroplane]:
        """
        Возвращает все сохранённые самолёты как список объектов Aeroplane.

        Returns:
            Список объектов Aeroplane, восстановленных из JSON.
        """
        return [
            Aeroplane(
                icao24=r["icao24"],
                callsign=r["callsign"],
                origin_country=r["origin_country"],
                time_position=r["time_position"],
                last_contact=r["last_contact"],
                longitude=r["longitude"],
                latitude=r["latitude"],
                baro_altitude=r["baro_altitude"],
                on_ground=r["on_ground"],
                velocity=r["velocity"],
                true_track=r["true_track"],
                vertical_rate=r["vertical_rate"],
                sensors=r["sensors"],
                geo_altitude=r["geo_altitude"],
                squawk=r["squawk"],
                spi=r["spi"],
                position_source=r["position_source"],
            )
            for r in self._data
        ]
