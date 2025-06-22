import pytest
from unittest.mock import patch
from api.sensors import get_sensor_data, APIConnectionError
import requests

@patch("api.sensors.requests.get")
def test_get_sensor_data_success(mock_get):
    """
    Testuje poprawne pobieranie danych z API.
    Sprawdza, czy funkcja zwraca dane z API gdy odpowiedź jest poprawna.
    """
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"key": "value"}

    result = get_sensor_data(123)
    assert result == {"key": "value"}
    mock_get.assert_called_once_with("https://api.gios.gov.pl/pjp-api/rest/data/getData/123", timeout=10)

@patch("api.sensors.requests.get", side_effect=requests.exceptions.ConnectionError("Connection failed"))
def test_get_sensor_data_failure(mock_get):
    """
    Testuje zachowanie funkcji przy błędzie połączenia.
    Sprawdza, czy funkcja rzuca APIConnectionError w przypadku wyjątku requests.
    """
    with pytest.raises(APIConnectionError) as exc_info:
        get_sensor_data(999)

    assert "Błąd pobierania danych z czujnika" in str(exc_info.value)

@patch("api.sensors.requests.get")
def test_get_sensor_data_empty_response(mock_get):
    """
    Testuje obsługę pustej odpowiedzi z API.
    Sprawdza, czy funkcja prawidłowo zwraca pustą listę danych.
    """
    mock_response = mock_get.return_value
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"values": []}

    result = get_sensor_data(123)

    assert result == {"values": []}