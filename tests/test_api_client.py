from unittest.mock import MagicMock, patch

import pytest
import requests

from src.api_client import BaseClient, NominatimClient, OpenSkyClient


class TestBaseClient:
    """Тесты для абстрактного класса BaseClient: проверка невозможности инстанцирования и наличия абстрактных методов."""

    def test_cannot_instantiate_abstract_class(self) -> None:
        """Проверяет, что BaseClient нельзя создать напрямую (абстрактный класс)."""
        with pytest.raises(TypeError):
            BaseClient()  # type: ignore

    def test_abstract_methods_exist(self) -> None:
        """Подтверждает наличие обязательных абстрактных методов в базовом классе."""
        assert hasattr(BaseClient, "get_country_bbox")
        assert hasattr(BaseClient, "get_airplanes_in_area")


class TestNominatimClient:
    """Тесты для NominatimClient: получение bounding box страны и обработка краевых случаев."""

    @patch("src.api_client.requests.Session")
    def test_get_country_bbox_success(self, mock_session: MagicMock) -> None:
        """Проверяет успешное получение bounding box для существующей страны."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = [
            {
                "boundingbox": ["40.0", "50.0", "-10.0", "0.0"],
                "display_name": "Test Country",
            }
        ]
        mock_session.return_value.get.return_value = mock_resp

        client = NominatimClient(user_agent="test/1.0")
        bbox = client.get_country_bbox("Test Country")

        assert bbox is not None
        assert len(bbox) == 4
        assert bbox == [40.0, 50.0, -10.0, 0.0]

    @patch("src.api_client.requests.Session")
    def test_get_country_bbox_empty_response(self, mock_session: MagicMock) -> None:
        """Проверяет возврат None при пустом ответе от API (страна не найдена)."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = []
        mock_session.return_value.get.return_value = mock_resp

        client = NominatimClient()
        bbox = client.get_country_bbox("Unknown Country")
        assert bbox is None

    @patch("src.api_client.requests.Session")
    def test_get_country_bbox_invalid_bbox_format(self, mock_session: MagicMock) -> None:
        """Проверяет обработку некорректного формата bounding box (не 4 значения)."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"boundingbox": ["1", "2"]}]
        mock_session.return_value.get.return_value = mock_resp

        client = NominatimClient()
        bbox = client.get_country_bbox("Bad Format")
        assert bbox is None

    @patch("src.api_client.requests.Session")
    def test_get_country_bbox_inverted_coords(self, mock_session: MagicMock) -> None:
        """Проверяет отсев случаев с инвертированными координатами (юг > север и т.п.)."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = [
            {"boundingbox": ["50.0", "40.0", "-10.0", "0.0"]}
        ]
        mock_session.return_value.get.return_value = mock_resp

        client = NominatimClient()
        bbox = client.get_country_bbox("Inverted")
        assert bbox is None

    @patch("src.api_client.requests.Session")
    def test_get_country_bbox_request_error(self, mock_session: MagicMock) -> None:
        """Проверяет выброс RuntimeError при сетевой ошибке запроса к Nominatim."""
        mock_session.return_value.get.side_effect = requests.RequestException(
            "Network error"
        )

        client = NominatimClient()
        with pytest.raises(RuntimeError):
            client.get_country_bbox("Error Country")

    def test_get_airplanes_in_area_nominatim_always_empty(self) -> None:
        """Убеждается, что Nominatim всегда возвращает пустой список для запросов о самолётах (заглушка)."""
        client = NominatimClient()
        result = client.get_airplanes_in_area(0.0, 1.0, 0.0, 1.0)
        assert result == []


class TestOpenSkyClient:
    """Тесты для OpenSkyClient: получение данных о самолётах и обработка ошибок и невалидных ответов."""

    @patch("src.api_client.requests.Session")
    def test_get_airplanes_in_area_success(self, mock_session: MagicMock) -> None:
        """Проверяет успешный запрос к OpenSky: корректный список состояний самолётов."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "states": [
                [
                    "icao1",
                    "callsign1",
                    "DE",
                    12345,
                    12350,
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
                [
                    "icao2",
                    "callsign2",
                    "FR",
                    12346,
                    12351,
                    11.0,
                    51.0,
                    3200.0,
                    False,
                    210.0,
                    95.0,
                    3.0,
                    [1, 2],
                    3300.0,
                    "4001",
                    False,
                    0,
                ],
            ]
        }
        mock_session.return_value.get.return_value = mock_resp

        client = OpenSkyClient()
        states = client.get_airplanes_in_area(40.0, 60.0, -10.0, 10.0)

        assert isinstance(states, list)
        assert len(states) == 2
        assert states[0][0] == "icao1"
        assert states[1][0] == "icao2"

    @patch("src.api_client.requests.Session")
    def test_get_airplanes_in_area_no_states_field(self, mock_session: MagicMock) -> None:
        """Проверяет поведение при отсутствии поля states в ответе API (возвращает пустой список)."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"other_field": []}  # нет states
        mock_session.return_value.get.return_value = mock_resp

        client = OpenSkyClient()
        states = client.get_airplanes_in_area(40.0, 60.0, -10.0, 10.0)
        assert states == []

    @patch("src.api_client.requests.Session")
    def test_get_airplanes_in_area_states_not_list(self, mock_session: MagicMock) -> None:
        """Проверяет корректную обработку случая, когда states — не список (возвращает пустой список)."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"states": "not a list"}
        mock_session.return_value.get.return_value = mock_resp

        client = OpenSkyClient()
        states = client.get_airplanes_in_area(40.0, 60.0, -10.0, 10.0)
        assert states == []

    @patch("src.api_client.requests.Session")
    def test_get_airplanes_in_area_request_error(self, mock_session: MagicMock) -> None:
        """Проверяет выброс RuntimeError при ошибке сетевого запроса к OpenSky."""
        mock_session.return_value.get.side_effect = requests.RequestException(
            "API down"
        )

        client = OpenSkyClient()
        with pytest.raises(RuntimeError):
            client.get_airplanes_in_area(40.0, 60.0, -10.0, 10.0)

    def test_get_country_bbox_opensky_always_none(self) -> None:
        """Гарантирует, что OpenSkyClient всегда возвращает None для запросов границ страны (не поддерживает эту функциональность)."""
        client = OpenSkyClient()
        bbox = client.get_country_bbox("Any Country")
        assert bbox is None
