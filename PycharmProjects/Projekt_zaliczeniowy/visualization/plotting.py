import matplotlib.pyplot as plt
from datetime import datetime

def plot_measurements(measurements, param_name):
    """
    Tworzy wykres wartości pomiarów, zaznaczając wartości minimalne i maksymalne.
    """
    if not measurements:
        return

    dates = []
    values = []

    for date_str, value, _ in measurements:
        if value is None:
            continue

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

        dates.append(date)
        values.append(value)

    if not dates:
        return

    min_val = min(values)
    max_val = max(values)
    min_idx = values.index(min_val)
    max_idx = values.index(max_val)

    plt.figure(figsize=(10, 5))

   # Rysujemy wszystkie punkty oprócz min i max jako niebieskie
    filtered_dates = [d for i, d in enumerate(dates) if i not in (min_idx, max_idx)]
    filtered_values = [v for i, v in enumerate(values) if i not in (min_idx, max_idx)]

    # Niebieska linia łącząca wszystkie punkty
    plt.plot(dates, values, linestyle='-', color='blue', alpha=0.3)

    # Niebieskie punkty poza min i max
    plt.scatter(filtered_dates, filtered_values, color='blue', label=param_name)



    plt.scatter(dates[min_idx], min_val, color='green', label=f'Min: {min_val} ({dates[min_idx].strftime("%Y-%m-%d %H:%M")})')
    plt.scatter(dates[max_idx], max_val, color='red', label=f'Max: {max_val} ({dates[max_idx].strftime("%Y-%m-%d %H:%M")})')
    plt.title(f"Wykres: {param_name}")
    plt.xlabel("Data")
    plt.ylabel("Wartość")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

