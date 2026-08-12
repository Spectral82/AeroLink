import json
import os
import tempfile

import pytest

from src.adapter import AirplaneAdapter
from src.airplanes import Aeroplane
from src.storage import JSONSaver

# Тесты для airplanes.py


class TestAeroplane:
    """Тесты для класса Aeroplane: создание, сравнение, строковое представление."""

    @pytest.fixture
    def plane(self):
        """Создаёт тестовый экземпляр Aeroplane с фиксированными значениями."""
        return Aeroplane(
            icao24="abc123",
            callsign="FLT999",
            origin_country="DE",
            time_position=123456,
            last_contact=123500,
            longitude=10.0,
            latitude=50.0,
            baro_altitude=3000.0,
            on_ground=False,
            velocity=200.0,
            true_track=90.0,
            vertical_rate=2.0,
            sensors=None,
            geo_altitude=3100.0,
            squawk="4000",
            spi=False,
            position_source=1,
        )

    def test_basic_creation(self, plane: Aeroplane) -> None:
        """Проверяет корректность инициализации и значений ключевых полей."""
        assert plane.callsign == "FLT999"
        assert plane.geo_altitude == 3100.0
        assert plane.velocity == 200.0

    def test_comparison_by_altitude(self, plane: Aeroplane) -> None:
        """Проверяет сравнение самолётов по высоте (geo_altitude)."""
        plane_higher = Aeroplane(
            icao24="x1",
            callsign="HIGHER",
            origin_country="XX",
            time_position=0,
            last_contact=0,
            longitude=0.0,
            latitude=0.0,
            baro_altitude=0.0,
            on_ground=False,
            velocity=0.0,
            true_track=0.0,
            vertical_rate=0.0,
            sensors=None,
            geo_altitude=4000.0,
            squawk="0000",
            spi=False,
            position_source=0,
        )
        assert plane < plane_higher
        assert not (plane > plane_higher)
        assert plane_higher > plane

    def test_compare_by_velocity_less(self, plane: Aeroplane) -> None:
        """Проверяет compare_by_velocity при меньшей скорости второго самолёта."""
        other = Aeroplane(
            icao24="y1",
            callsign="SLOWER",
            origin_country="YY",
            time_position=0,
            last_contact=0,
            longitude=0.0,
            latitude=0.0,
            baro_altitude=0.0,
            on_ground=False,
            velocity=100.0,
            true_track=0.0,
            vertical_rate=0.0,
            sensors=None,
            geo_altitude=0.0,
            squawk="0000",
            spi=False,
            position_source=0,
        )
        assert plane.compare_by_velocity(other) == 1
        assert other.compare_by_velocity(plane) == -1

    def test_compare_by_velocity_equal(self, plane: Aeroplane) -> None:
        """Проверяет compare_by_velocity при равной скорости."""
        other = Aeroplane(
            icao24="z1",
            callsign="EQUAL",
            origin_country="ZZ",
            time_position=0,
            last_contact=0,
            longitude=0.0,
            latitude=0.0,
            baro_altitude=0.0,
            on_ground=False,
            velocity=plane.velocity,
            true_track=0.0,
            vertical_rate=0.0,
            sensors=None,
            geo_altitude=0.0,
            squawk="0000",
            spi=False,
            position_source=0,
        )
        assert plane.compare_by_velocity(other) == 0

    def test_repr(self, plane: Aeroplane) -> None:
        """Проверяет, что __repr__ возвращает строку с ключевыми данными."""
        r = repr(plane)
        assert "Aeroplane" in r
        assert "FLT999" in r

    def test_invalid_comparison(self, plane: Aeroplane) -> None:
        """Проверяет выброс TypeError при сравнении с не‑Aeroplane объектом."""
        with pytest.raises(TypeError):
            plane.compare_by_velocity("not a plane")


# Тесты для storage.py


@pytest.fixture
def temp_json_path() -> None:
    """Создаёт временный JSON‑файл и удаляет его после теста."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


class TestJSONSaver:
    """Тесты для JSONSaver: сохранение, обновление, удаление, обработка ошибок и краевых случаев."""

    def test_create_and_save_single_plane(self, temp_json_path: str) -> None:
        """Проверяет добавление одного самолёта, сохранение в файл и восстановление как объекта."""
        saver = JSONSaver(filepath=temp_json_path)
        plane = Aeroplane(
            icao24="abc123",
            callsign="FLT999",
            origin_country="DE",
            time_position=123456,
            last_contact=123500,
            longitude=10.0,
            latitude=50.0,
            baro_altitude=3000.0,
            on_ground=False,
            velocity=200.0,
            true_track=90.0,
            vertical_rate=2.0,
            sensors=None,
            geo_altitude=3100.0,
            squawk="4000",
            spi=False,
            position_source=1,
        )
        saver.add_aeroplane(plane)

        assert os.path.exists(temp_json_path)
        with open(temp_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["callsign"] == "FLT999"

        objects = saver.get_all_as_objects()
        assert len(objects) == 1
        assert objects[0].callsign == plane.callsign
        assert objects[0].geo_altitude == plane.geo_altitude

    def test_update_existing_plane_by_callsign(self, temp_json_path: str) -> None:
        """Проверяет обновление записи по callsign (дедупликация)."""
        saver = JSONSaver(filepath=temp_json_path)
        plane1 = Aeroplane(
            icao24="a1",
            callsign="UPDATE",
            origin_country="US",
            time_position=0,
            last_contact=0,
            longitude=0.0,
            latitude=0.0,
            baro_altitude=0.0,
            on_ground=False,
            velocity=100.0,
            true_track=0.0,
            vertical_rate=0.0,
            sensors=None,
            geo_altitude=1000.0,
            squawk="1234",
            spi=False,
            position_source=0,
        )
        plane2 = Aeroplane(
            icao24="a2",
            callsign="UPDATE",
            origin_country="CA",
            time_position=0,
            last_contact=0,
            longitude=0.0,
            latitude=0.0,
            baro_altitude=0.0,
            on_ground=False,
            velocity=200.0,
            true_track=0.0,
            vertical_rate=0.0,
            sensors=None,
            geo_altitude=2000.0,
            squawk="5678",
            spi=False,
            position_source=0,
        )

        saver.add_aeroplane(plane1)
        objects_before = saver.get_all_as_objects()
        assert objects_before[0].velocity == 100.0

        saver.add_aeroplane(plane2)
        objects_after = saver.get_all_as_objects()
        assert len(objects_after) == 1
        assert objects_after[0].velocity == 200.0
        assert objects_after[0].origin_country == "CA"

    def test_delete_aeroplane(self, temp_json_path: str) -> None:
        """Проверяет удаление самолёта по callsign и повторный вызов (отсутствие)."""
        saver = JSONSaver(filepath=temp_json_path)
        plane = Aeroplane(
            icao24="del1",
            callsign="DELETE_ME",
            origin_country="FR",
            time_position=0,
            last_contact=0,
            longitude=0.0,
            latitude=0.0,
            baro_altitude=0.0,
            on_ground=False,
            velocity=0.0,
            true_track=0.0,
            vertical_rate=0.0,
            sensors=None,
            geo_altitude=0.0,
            squawk="0000",
            spi=False,
            position_source=0,
        )
        saver.add_aeroplane(plane)
        assert saver.delete_aeroplane("DELETE_ME") is True
        assert saver.delete_aeroplane("DELETE_ME") is False
        objects = saver.get_all_as_objects()
        assert len(objects) == 0

    def test_load_from_empty_file(self, temp_json_path: str) -> None:
        """Проверяет загрузку из пустого файла (корректное поведение без ошибок)."""
        with open(temp_json_path, "w", encoding="utf-8") as f:
            f.write("")
        saver = JSONSaver(filepath=temp_json_path)
        assert saver._data == []
        assert len(saver.get_all_as_objects()) == 0

    def test_load_from_invalid_json(self, temp_json_path: str) -> None:
        """Проверяет обработку невалидного JSON (возвращает пустой список)."""
        with open(temp_json_path, "w", encoding="utf-8") as f:
            f.write("{ not valid json }")
        saver = JSONSaver(filepath=temp_json_path)
        assert saver._data == []

    def test_load_from_non_list_json(self, temp_json_path: str) -> None:
        """Проверяет обработку JSON, который не является списком (возвращает пустой список)."""
        with open(temp_json_path, "w", encoding="utf-8") as f:
            f.write('"just a string"')
        saver = JSONSaver(filepath=temp_json_path)
        assert saver._data == []

    def test_save_raises_runtime_error_on_io_failure(self, temp_json_path: str) -> None:
        """Проверяет выброс RuntimeError при ошибке записи (некорректный путь)."""
        bad_path = os.path.join(temp_json_path, "..", "nonexistent", "data.json")
        saver = JSONSaver(filepath=bad_path)
        plane = Aeroplane(
            icao24="err1",
            callsign="ERR",
            origin_country="XX",
            time_position=0,
            last_contact=0,
            longitude=0.0,
            latitude=0.0,
            baro_altitude=0.0,
            on_ground=False,
            velocity=0.0,
            true_track=0.0,
            vertical_rate=0.0,
            sensors=None,
            geo_altitude=0.0,
            squawk="0000",
            spi=False,
            position_source=0,
        )
        with pytest.raises(RuntimeError):
            saver.add_aeroplane(plane)


# Тесты для adapter.py


class TestAirplaneAdapter:
    """Тесты для AirplaneAdapter: преобразование сырых данных OpenSky в объекты Aeroplane."""

    def test_from_opensky_row_valid(self) -> None:
        """Проверяет конвертацию валидной строки OpenSky в объект Aeroplane."""
        row = [
            "abc123",
            "FLT999",
            "DE",
            123456,
            123500,
            10.0,
            50.0,
            3000.0,
            False,
            200.0,
            90.0,
            2.0,
            None,
            3100.0,
            "4000",
            False,
            1,
        ]
        plane = AirplaneAdapter.from_opensky_row(row)
        assert plane.icao24 == "abc123"
        assert plane.callsign == "FLT999"
        assert plane.origin_country == "DE"
        assert plane.geo_altitude == 3100.0
        assert plane.velocity == 200.0

    def test_from_opensky_row_short_list(self) -> None:
        """Проверяет ValueError при слишком короткой строке (менее 17 элементов)."""
        short_row = ["a", "b"]
        with pytest.raises(ValueError):
            AirplaneAdapter.from_opensky_row(short_row)

    def test_from_opensky_states_mixed(self) -> None:
        """Проверяет обработку смешанного списка: валидные + битые строки (пропуск битых)."""
        states = [
            [
                "abc123",
                "FLT999",
                "DE",
                123456,
                123500,
                10.0,
                50.0,
                3000.0,
                False,
                200.0,
                90.0,
                2.0,
                None,
                3100.0,
                "4000",
                False,
                1,
            ],
            ["short"],
            [
                "xyz789",
                "TEST2",
                "FR",
                0,
                0,
                0.0,
                0.0,
                0.0,
                True,
                150.0,
                0.0,
                0.0,
                [1, 2],
                2500.0,
                "1234",
                True,
                0,
            ],
        ]
        planes = AirplaneAdapter.from_opensky_states(states)
        assert len(planes) == 2
        assert planes[0].callsign == "FLT999"
        assert planes[1].callsign == "TEST2"

    def test_from_opensky_states_empty(self) -> None:
        """Проверяет поведение при пустом списке состояний (возвращает пустой список)."""
        planes = AirplaneAdapter.from_opensky_states([])
        assert len(planes) == 0
