import requests

class APIConnectionError(Exception):
    """Wyjątek podnoszony, gdy wystąpi problem z połączeniem do API."""
    pass


def get_all_stations():
    """
    Pobiera listę wszystkich stacji pomiarowych w Polsce z API GIOŚ.
    Zwraca listę słowników z informacjami o stacjach.
    Rzuca APIConnectionError w przypadku błędu sieciowego.
    """
    url = "https://api.gios.gov.pl/pjp-api/rest/station/findAll"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise APIConnectionError(f"Błąd pobierania danych o stacjach: {e}")


def filter_stations_by_city(stations, city_name):
    """
    Zwraca listę stacji znajdujących się w danym mieście (ignorując wielkość liter).
    """
    return [
        station for station in stations
        if station.get("city", {}).get("name", "").lower() == city_name.lower()
    ]


def get_sensors_for_station(station_id):
    """
    Pobiera listę czujników (stanowisk pomiarowych) dla danej stacji.
    Rzuca APIConnectionError w przypadku błędu sieciowego.
    """
    url = f"https://api.gios.gov.pl/pjp-api/rest/station/sensors/{station_id}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise APIConnectionError(f"Błąd pobierania czujników stacji {station_id}: {e}")
