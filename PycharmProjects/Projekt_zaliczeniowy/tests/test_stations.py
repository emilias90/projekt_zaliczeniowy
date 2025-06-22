import pytest
from unittest.mock import patch, MagicMock
from api.stations import (
    get_all_stations,
    filter_stations_by_city,
    get_sensors_for_station,
    APIConnectionError,
)
import requests


@patch("api.stations.requests.get")
def test_get_all_stations_success(mock_get):
    """
    Testuje poprawne pobranie listy wszystkich stacji.
    Sprawdza, czy funkcja get_all_stations zwraca listę stacji
    oraz czy wywołanie API zostało wykonane z odpowiednim URL i timeoutem.
    """
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 1, "city": {"name": "Warszawa"}}]

    result = get_all_stations()
    assert isinstance(result, list)
    assert result == [{"id": 1, "city": {"name": "Warszawa"}}]
    mock_get.assert_called_once_with("https://api.gios.gov.pl/pjp-api/rest/station/findAll", timeout=10)


@patch("api.stations.requests.get", side_effect=requests.exceptions.ConnectionError("Fail"))
def test_get_all_stations_failure(mock_get):
    """
    Testuje obsługę błędu połączenia podczas pobierania listy stacji.
    Sprawdza, czy w przypadku błędu requests funkcja podnosi APIConnectionError
    z odpowiednim komunikatem.
    """
    with pytest.raises(APIConnectionError) as exc_info:
        get_all_stations()
    assert "Błąd pobierania danych o stacjach" in str(exc_info.value)


def test_filter_stations_by_city():
    """
    Testuje filtrowanie listy stacji według nazwy miasta.
    Sprawdza, czy funkcja filter_stations_by_city poprawnie
    zwraca tylko stacje z podanego miasta, ignorując wielkość liter
    oraz czy ignoruje stacje bez danych o mieście.
    """
    stations = [
        {"city": {"name": "Warszawa"}, "id": 1},
        {"city": {"name": "Kraków"}, "id": 2},
        {"city": {"name": "warszawa"}, "id": 3},
        {"city": {}, "id": 4},
        {"id": 5},
    ]
    filtered = filter_stations_by_city(stations, "warszawa")
    assert len(filtered) == 2
    assert all(station["city"]["name"].lower() == "warszawa" for station in filtered)


@patch("api.stations.requests.get")
def test_get_sensors_for_station_success(mock_get):
    """
    Testuje poprawne pobranie listy czujników dla danej stacji.
    Sprawdza, czy funkcja get_sensors_for_station zwraca listę czujników
    oraz czy zapytanie do API zostało wykonane z odpowiednim URL i timeoutem.
    """
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = [{"id": 101, "param": "PM10"}]

    station_id = 1
    result = get_sensors_for_station(station_id)
    assert isinstance(result, list)
    assert result == [{"id": 101, "param": "PM10"}]
    mock_get.assert_called_once_with(f"https://api.gios.gov.pl/pjp-api/rest/station/sensors/{station_id}", timeout=10)


@patch("api.stations.requests.get", side_effect=requests.exceptions.Timeout("Timeout"))
def test_get_sensors_for_station_failure(mock_get):
    """
    Testuje obsługę błędu timeout podczas pobierania czujników stacji.
    Sprawdza, czy w przypadku błędu requests funkcja podnosi APIConnectionError
    z komunikatem zawierającym ID stacji.
    """
    with pytest.raises(APIConnectionError) as exc_info:
        get_sensors_for_station(999)
    assert "Błąd pobierania czujników stacji 999" in str(exc_info.value)
