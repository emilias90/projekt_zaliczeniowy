import requests

class APIConnectionError(Exception):
    """Wyjątek podnoszony, gdy wystąpi problem z połączeniem do API."""
    pass


def get_sensor_data(sensor_id):
    """
    Pobiera dane pomiarowe z podanego czujnika.
    """
    url = f"https://api.gios.gov.pl/pjp-api/rest/data/getData/{sensor_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise APIConnectionError(f"Błąd pobierania danych z czujnika {sensor_id}: {e}")