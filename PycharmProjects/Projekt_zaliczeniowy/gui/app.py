import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from api.stations import get_all_stations, filter_stations_by_city, get_sensors_for_station, APIConnectionError
from api.sensors import get_sensor_data
from db.database import (
    create_table,
    create_measurements_table,
    insert_station,
    insert_measurements,
    create_sensors_table,
    insert_sensor,
    clear_database
)
from visualization.plotting import plot_measurements


class AirQualityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor Jakości Powietrza")

        create_table()
        create_measurements_table()
        create_sensors_table()

        self.city_var = tk.StringVar()
        self.station_var = tk.StringVar()
        self.sensor_var = tk.StringVar()
        self.date_from_var = tk.StringVar()
        self.date_to_var = tk.StringVar()

        self.stations = []
        self.sensors = []
        self.sensor_id = None
        self.stats_label = None

        # Statystyki
        self.stats_frame = None
        self.max_label = None
        self.min_label = None
        self.avg_label = None

        self.build_ui()


    def build_ui(self):
        # Konfiguracja kolumn
        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)

        # Miasto
        ttk.Label(self.root, text="Miasto:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.root, textvariable=self.city_var).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(self.root, text="Pobierz stacje", command=self.load_stations).grid(row=0, column=2, padx=5, pady=5)

        # Lista stacji
        self.station_box = ttk.Combobox(self.root, textvariable=self.station_var, state="readonly", width=50)
        self.station_box.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        ttk.Button(self.root, text="Pobierz czujniki", command=self.load_sensors).grid(row=1, column=3, padx=5)

        # Lista czujników
        self.sensor_box = ttk.Combobox(self.root, textvariable=self.sensor_var, state="readonly", width=50)
        self.sensor_box.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        # Pobierz daty
        ttk.Button(self.root, text="Pobierz daty", command=self.load_available_dates).grid(
            row=2, column=3, columnspan=2, padx=5)

        # Data od / do
        ttk.Label(self.root, text="Data od:").grid(row=4, column=0, sticky="e", padx=5)
        self.date_from_box = ttk.Combobox(self.root, textvariable=self.date_from_var, state="readonly", width=20)
        self.date_from_box.grid(row=4, column=1, sticky="w", padx=5)

        ttk.Label(self.root, text="Data do:").grid(row=4, column=2, sticky="e", padx=5)
        self.date_to_box = ttk.Combobox(self.root, textvariable=self.date_to_var, state="readonly", width=20)
        self.date_to_box.grid(row=4, column=3, sticky="w", padx=5)

        # Pobierz dane
        ttk.Button(self.root, text="Pobierz dane", command=self.load_measurements).grid(
            row=5, column=1, columnspan=2, sticky="ew", padx=5, pady=10
        )

        # Ramka na statystyki
        self.stats_frame = ttk.LabelFrame(self.root, text="Statystyki pomiarów")
        self.stats_frame.grid(row=6, column=0, columnspan=4, sticky="ew", padx=10, pady=10)

        self.max_label = ttk.Label(self.stats_frame, text="Maksimum: -")
        self.max_label.grid(row=0, column=0, sticky="w", padx=10)

        self.min_label = ttk.Label(self.stats_frame, text="Minimum: -")
        self.min_label.grid(row=1, column=0, sticky="w", padx=10)
        self.min_label.grid(row=1, column=0, sticky="w", padx=10)

        self.avg_label = ttk.Label(self.stats_frame, text="Średnia: -")
        self.avg_label.grid(row=2, column=0, sticky="w", padx=10)

        # pozostałe
        ttk.Button(self.root, text="Wykres", command=self.plot_data).grid(
            row=7, column=1, sticky="ew", padx=5, pady=10
        )
        ttk.Button(self.root, text="Wyczyść dane", command=self.clear_data).grid(
            row=7, column=2, sticky="ew", padx=5, pady=10
        )
        ttk.Button(self.root, text="Usuń dane z bazy", command=self.delete_data_from_db).grid(
            row=8, column=1, columnspan=2, sticky="ew", padx=5, pady=10
        )

    def load_stations(self):
        """
        Pobiera i wyświetla listę stacji pomiarowych dla wybranego miasta.

        Działanie funkcji:
        1. Odczytuje nazwę miasta wprowadzonego przez użytkownika w polu tekstowym.
        2. Jeśli pole miasta jest puste – wyświetla ostrzeżenie i kończy działanie.
        3. Pobiera wszystkie dostępne stacje z API i filtruje je według podanego miasta.
        4. Jeśli nie znaleziono stacji – informuje użytkownika i kończy działanie.
        5. Wyświetla listę znalezionych stacji w rozwijanym polu (Combobox).
        6. Zapisuje informacje o każdej znalezionej stacji do bazy danych (SQLite).
        7. Automatycznie zaznacza pierwszą stację z listy jako domyślną.
        """
        city = self.city_var.get().strip()
        if not city:
            messagebox.showwarning("Uwaga", "Wprowadź nazwę miasta.")
            return

        try:
            all_stations = get_all_stations()
        except APIConnectionError as e:
            messagebox.showerror("Błąd połączenia", str(e))
            all_stations = []

        self.stations = filter_stations_by_city(all_stations, city)

        if not self.stations:
            messagebox.showinfo("Brak wyników", f"Brak stacji w mieście: {city}")
            return

        self.station_box['values'] = [f"{s['stationName']} (ID: {s['id']})" for s in self.stations]
        for s in self.stations:
            insert_station(s)
        self.station_box.current(0)


    def load_sensors(self):
        """
        Pobiera i wyświetla listę czujników dostępnych dla wybranej stacji pomiarowej.

        Działanie funkcji:
        1. Sprawdza, czy użytkownik wybrał stację z listy (Combobox).
           Jeśli nie – wyświetla ostrzeżenie i kończy działanie.
        2. Pobiera indeks wybranej stacji i na jego podstawie identyfikuje obiekt stacji.
        3. Pobiera z API listę czujników przypisanych do danej stacji.
        4. Jeśli brak czujników – informuje użytkownika i kończy działanie.
        5. Aktualizuje listę czujników (Combobox) wyświetlając nazwę parametru, wzór chemiczny i ID czujnika.
        6. Zapisuje dane czujników do lokalnej bazy danych (SQLite).
        7. Automatycznie zaznacza pierwszy czujnik na liście jako domyślny.
        """

        if not self.station_box.get():
            messagebox.showwarning("Uwaga", "Najpierw wybierz stację.")
            return

        index = self.station_box.current()
        station = self.stations[index]
        try:
            self.sensors = get_sensors_for_station(station['id'])
        except APIConnectionError as e:
            messagebox.showerror("Błąd połączenia", str(e))
            return

        if not self.sensors:
            messagebox.showinfo("Brak czujników", "Brak czujników dla tej stacji.")
            return

        self.sensor_box['values'] = [f"{s['param']['paramName']} ({s['param']['paramFormula']}) - ID: {s['id']}" for s in self.sensors]
        for s in self.sensors:
            insert_sensor(s)
        self.sensor_box.current(0)



    def load_available_dates(self):
        """
        Pobiera i wyświetla dostępne daty pomiarów dla wybranego czujnika.

        Działanie funkcji:
        1. Sprawdza, czy użytkownik wybrał czujnik z listy.
           Jeśli nie – wyświetla ostrzeżenie i przerywa działanie.
        2. Pobiera dane pomiarowe dla wybranego czujnika (po ID) z API.
        3. Weryfikuje, czy dane istnieją i zawierają pomiary. Jeśli nie – informuje użytkownika.
        4. Filtrowane są tylko wartości, które posiadają niepuste wartości (`value is not None`).
        5. Z danych wyodrębnia listę unikalnych dat (w formacie `YYYY-MM-DD`) i sortuje je.
        6. Jeśli nie ma dostępnych dat – wyświetla odpowiedni komunikat.
        7. Wypełnia listy wyboru (Comboboxy) dla zakresu dat („od” i „do”) dostępnymi wartościami.
        8. Resetuje ewentualne wcześniejsze wybory dat.
        9. Informuje użytkownika o liczbie dostępnych dat

        """
        if not self.sensor_box.get():
            messagebox.showwarning("Uwaga", "Najpierw wybierz czujnik.")
            return

        index = self.sensor_box.current()
        sensor = self.sensors[index]
        self.sensor_id = sensor['id']

        try:
            data = get_sensor_data(self.sensor_id)
        except APIConnectionError as e:
            messagebox.showerror("Błąd połączenia", str(e))
            return

        if not data or 'values' not in data:
            messagebox.showinfo("Brak danych", "Brak danych pomiarowych dla tego czujnika.")
            return

        self.raw_values = [
            (item['date'], item['value'])
            for item in data['values']
            if item['value'] is not None
        ]

        # Wyciągnięcie listy unikalnych dat
        all_dates = sorted({item['date'][:10] for item in data['values'] if item['value'] is not None})

        if not all_dates:
            messagebox.showinfo("Brak danych", "Brak dostępnych dat pomiarowych.")
            return

        self.date_from_box['values'] = all_dates
        self.date_to_box['values'] = all_dates

        # Wyczyść poprzednie wybory
        self.date_from_var.set("")
        self.date_to_var.set("")

        messagebox.showinfo("Sukces", f"Pobrano {len(all_dates)} dostępnych dat.")



    def load_measurements(self):
        """
        Pobiera dane pomiarowe z wybranego czujnika, filtruje je według zakresu dat i wyświetla statystyki.

        Działanie funkcji:
        1. Sprawdza, czy użytkownik wybrał czujnik z listy. Jeśli nie – wyświetla ostrzeżenie i kończy działanie.
        2. Na podstawie indeksu w `sensor_box` identyfikuje czujnik oraz jego ID i nazwę parametru.
        3. Pobiera dane pomiarowe z API dla danego czujnika.
        4. Jeśli dane są puste lub nie zawierają listy pomiarów – wyświetla informację i kończy działanie.
        5. Wstawia dane pomiarowe do lokalnej bazy danych.
        6. Filtruje dane, pozostawiając tylko te, które zawierają wartość (`value != None`), i zapisuje je do `self.raw_values`.
        7. Tworzy listę unikalnych dat z danych i przypisuje je do comboboxów wyboru zakresu dat.
        8. Ustawia domyślny zakres dat, jeśli nie został wcześniej wybrany.
        9. Pobiera wartości mieszczące się w wybranym zakresie dat.
        10. Oblicza i wyświetla statystyki: minimum, maksimum oraz średnią wartość dla danego okresu.
        11. Wyniki są prezentowane w GUI oraz przechowywane w `self.filtered_values`.

        Efekt:
        - Statystyki (minimum, maksimum, średnia) dla pomiarów z wybranego zakresu dat zostają obliczone i pokazane w interfejsie.

        """
        if not self.sensor_box.get():
            messagebox.showwarning("Uwaga", "Najpierw wybierz czujnik.")
            return

        index = self.sensor_box.current()
        sensor = self.sensors[index]
        self.sensor_id = sensor['id']

        try:
            data = get_sensor_data(self.sensor_id)
        except APIConnectionError as e:
            messagebox.showerror("Błąd połączenia", str(e))
            return

        self.param_name = sensor['param']['paramName']

        if not data or 'values' not in data:
            messagebox.showinfo("Brak danych", "Brak danych pomiarowych dla tego czujnika.")
            return

        param_key = data.get('key', '')
        insert_measurements(self.sensor_id, param_key, data['values'])

        self.raw_values = [
            (item['date'], item['value'])
            for item in data['values']
            if item['value'] is not None
        ]
        # Wyciągnięcie listy dostępnych dat
        all_dates = sorted({item['date'][:10] for item in data['values'] if item['value'] is not None})
        if not all_dates:
            messagebox.showinfo("Brak danych", "Brak wartości do analizy.")
            return

        # Ustaw dostępne daty w dropdownach
        self.date_from_box['values'] = all_dates
        self.date_to_box['values'] = all_dates

        if not self.date_from_var.get():
            self.date_from_var.set(all_dates[0])
        if not self.date_to_var.get():
            self.date_to_var.set(all_dates[-1])

        date_range = self.get_valid_date_range()
        if not date_range:
            return
        date_from, date_to = date_range

        values = [
            (item['date'], item['value'])
            for item in data['values']
            if item['value'] is not None and date_from <= datetime.strptime(item['date'][:10], "%Y-%m-%d") <= date_to
        ]

        if not values:
            messagebox.showinfo("Brak danych", "Brak wartości w wybranym zakresie dat.")
            return

        # Min / Max / Średnia
        min_entry = min(values, key=lambda x: x[1])
        max_entry = max(values, key=lambda x: x[1])
        avg_value = round(sum(v[1] for v in values) / len(values), 2)

        date_from_str = date_from.strftime("%Y-%m-%d")
        date_to_str = date_to.strftime("%Y-%m-%d")

        zakres = f"Statystyki pomiarów ({date_from_str} — {date_to_str})"
        self.stats_frame.config(text=zakres)

        self.min_label.config(text=f"Minimum: {min_entry[1]} ({min_entry[0][:16].replace('T', ' ')})")
        self.max_label.config(text=f"Maksimum: {max_entry[1]} ({max_entry[0][:16].replace('T', ' ')})")
        self.avg_label.config(text=f"Średnia: {avg_value:.2f}")

        # Zapisz przefiltrowane dane do atrybutu
        self.filtered_values = values

    def plot_data(self):
        """
        Tworzy wykres danych pomiarowych dla wybranego czujnika i zakresu dat.
        Jeśli dane nie są dostępne, wyświetlany jest komunikat informacyjny.
        """

        filtered = self.get_filtered_values()
        if not filtered:
            messagebox.showinfo("Brak danych", "Brak danych do wyświetlenia wykresu.")
            return

        # Konwertuj dane do formatu dla plot_measurements
        data_for_plot = [(d, v, None) for d, v in filtered]
        plot_measurements(data_for_plot, self.param_name)


    def clear_data(self):
        """
        Czyści wszystkie pola wejściowe, wybory i statystyki pomiarów w interfejsie.
        """
        self.station_box.set("")
        self.sensor_box.set("")
        self.sensor_id = None
        self.station_var.set("")
        self.sensor_var.set("")
        self.city_var.set("")
        self.date_from_var.set("")
        self.date_to_var.set("")
        self.date_from_box['values'] = []
        self.date_to_box['values'] = []
        if self.stats_frame:
            self.stats_frame.config(text="Statystyki pomiarów")
            self.min_label.config(text="Minimum: -")
            self.max_label.config(text="Maksimum: -")
            self.avg_label.config(text="Średnia: -")
        messagebox.showinfo("Wyczyszczono", "Dane i statystyki zostały wyczyszczone.")

    def get_filtered_values(self):
        """
        Zwraca listę pomiarów (data, wartość) z `self.raw_values`,
        które mieszczą się w wybranym zakresie dat określonym przez
        pola `date_from_var` i `date_to_var`.

        Jeśli `raw_values` nie istnieje lub zakres dat jest niepoprawny,
        zwraca pustą listę.

        Format daty w `raw_values` jest oczekiwany jako ISO (YYYY-MM-DD...).
        """
        if not hasattr(self, 'raw_values'):
            return []

        date_range = self.get_valid_date_range()
        if not date_range:
            return []
        date_from, date_to = date_range

        return [
            (d, v)
            for d, v in self.raw_values
            if date_from <= datetime.strptime(d[:10], "%Y-%m-%d") <= date_to
        ]

    def get_valid_date_range(self):
        """
        Zwraca krotkę (date_from, date_to) jako obiekty datetime,
        lub None jeśli daty są niepoprawne lub w złej kolejności.
        """
        date_from_str = self.date_from_var.get()
        date_to_str = self.date_to_var.get()

        try:
            date_from = datetime.strptime(date_from_str, "%Y-%m-%d")
            date_to = datetime.strptime(date_to_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowy format daty.")
            return None

        if date_from > date_to:
            messagebox.showerror("Błąd", "Data OD nie może być późniejsza niż data DO.")
            return None

        return date_from, date_to

    def delete_data_from_db(self):
        confirm = messagebox.askyesno("Potwierdzenie", "Czy na pewno chcesz usunąć wszystkie dane z bazy?")
        if confirm:
            try:
                clear_database()
                messagebox.showinfo("Sukces", "Wszystkie dane zostały usunięte z bazy.")
                self.clear_data()
            except Exception as e:
                messagebox.showerror("Błąd", f"Wystąpił problem podczas usuwania danych:\n{e}")

