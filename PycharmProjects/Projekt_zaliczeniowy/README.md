# Monitor Jakości Powietrza (GUI z użyciem Tkinter)

Aplikacja desktopowa w Pythonie służąca do monitorowania jakości powietrza w wybranym mieście. Umożliwia pobieranie danych pomiarowych z API GIOŚ, ich wizualizację, analizę statystyczną oraz zapis do lokalnej bazy danych SQLite.

## Spis treści

- [Opis projektu](#opis-projektu)
- [Wymagania](#wymagania)
- [Struktura projektu](#struktura-projektu)
- [Instalacja](#instalacja)
- [Sposób użycia](#sposob-uzycia)
- [Przykład działania](#przyklad-dzialania)
- [Testy](#testy)

---

## Opis projektu

Projekt stworzony jako zaliczenie studiów podyplomowych "Akademia Programowania w Pythonie". 
Aplikacja umożliwia:

- Wyszukiwanie stacji pomiarowych na podstawie miasta
- Wybór dostępnych czujników i zakresów dat
- Pobieranie danych pomiarowych z API
- Wyświetlanie statystyk (min, max, średnia)
- Rysowanie wykresu pomiarów
- Przechowywanie danych w lokalnej bazie SQLite
- Czyszczenie oraz resetowanie bazy danych

## Wymagania

- Python 3.13
- Biblioteki:
  - `tkinter`
  - `matplotlib`
  - `requests` 
  - `sqlite3`



## Struktura projektu

projekt_zaliczeniowy

├── api/

│   ├── stations.py         - Obsługa zapytań dot. stacji

│   └── sensors.py          - Obsługa zapytań dot. czujników

├── db/

│   └── database.py         - Operacje na bazie danych SQLite

├── gui/

│   └── app.py              - Główny plik z interfejsem GUI

├── tests/                  - testy

│   └── test_get_sensor.py         

│   └── test_stations.py        

├── visualization/

│   └── plotting.py         - Tworzenie wykresów i analiz

├── air_quality.db          - Plik bazy danych SQLite z danymi o pomiarach

├── main.py                 - Plik do uruchomienia GUI

├── README.md               - Ten plik

├── requirements.txt        - Lista zależności projektu



## Instalacja
git clone ********** # (tu podam później link do ostatecznego repozytorium, np. GitHub)
cd **********
Uruchom aplikację:



## Sposób użycia:

Uruchom aplikację (main.py)

Wpisz nazwę miasta i kliknij "Pobierz stacje"

Wybierz stację i kliknij "Pobierz czujniki"

Wybierz czujnik i kliknij "Pobierz daty"

Wybierz zakres dat i kliknij "Pobierz dane"

Przeglądaj statystyki, rysuj wykresy i zarządzaj bazą danych




## Przykład działania

interfejs GUI

![image](https://github.com/user-attachments/assets/751a4d7e-5af3-41c6-81e5-8fd08058b6f8)

wybrana miejścowiść:

![image](https://github.com/user-attachments/assets/8020af24-9ac4-41b2-bad9-a2861720514c)


pobranie dostępnych dat z zapisanymi wartościami dla danego czujnika:

![image](https://github.com/user-attachments/assets/45bc5fa9-06c0-4239-ac5a-efc3de223321)

pobrane dane z bazy (wyliczona średnia, podana min, max dla wybranego zakresu dat)

![image](https://github.com/user-attachments/assets/0617e0a2-260d-478e-9711-37b897e977a2)


wykres dla wybranego czujnika z wybranym zakresem dat: 

![image](https://github.com/user-attachments/assets/2e310274-3457-4b1f-8afe-22674f0aed67)


wyczyść dane GUI:
![image](https://github.com/user-attachments/assets/678e141c-87b1-4c13-8753-ec7fa4b9bfae)




## Testy

W projekcie są testy do sprawdzenia, czy funkcje działają poprawnie.

Pliki z testami są w folderze tests/:

test_get_sensor.py – testy pobierania danych z czujników

test_stations.py – testy stacji i czujników

Do uruchamiania testów używam pytest. Trzeba go wcześniej zainstalować:

np przez konsolę wpisując: pip install pytest

Testy można potem uruchomić komendą pytest w głównym katalogu projektu.





Uwagi

Aplikacja wykorzystuje dane z publicznego API. W przypadku problemów z połączeniem (np. brak internetu lub przeciążone API), pojawią się odpowiednie komunikaty.

Domyślna baza danych to plik SQLite zapisany lokalnie. Można go łatwo usunąć przy pomocy przycisku "Usuń dane z bazy".

Kod można łatwo rozbudować np. o inne formy wizualizacji, eksport danych do CSV, czy zapis konfiguracji użytkownika.


Autor:

Emilia Staśkowiak
