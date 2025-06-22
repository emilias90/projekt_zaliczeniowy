import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "air_quality.db")

def create_connection():
    return sqlite3.connect(DB_PATH)

def create_table():
    '''Funkcja tworząca nową tabelę do zapisu danych o stacjach'''
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stations (
            id_stacji INTEGER PRIMARY KEY,
            name TEXT,
            lat TEXT,
            lon TEXT,
            city TEXT,
            street TEXT
        );
    """)
    conn.commit()
    conn.close()


def insert_station(station):
    '''Funkcja zapisuje dane stacji'''
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO stations (id_stacji, name, lat, lon, city, street)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        station['id'],
        station['stationName'],
        station['gegrLat'],
        station['gegrLon'],
        station.get('city', {}).get('name', ''),
        station.get('addressStreet', '')
    ))
    conn.commit()
    conn.close()


def create_measurements_table():
    '''Funkcja tworząca nową tabelę do zapisu danych z sensora'''
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id INTEGER,
            date TEXT,
            value REAL,
            param_key TEXT
        );
    """)
    conn.commit()
    conn.close()


def insert_measurements(sensor_id, param_key, measurements):
    '''Funkcja zapisuje dane z sensora'''
    conn = create_connection()
    cursor = conn.cursor()

    for m in measurements:
        cursor.execute("""
            INSERT INTO measurements (sensor_id, date, value, param_key)
            VALUES (?, ?, ?, ?)
        """, (
            sensor_id,
            m['date'],
            m['value'],
            param_key
        ))

    conn.commit()
    conn.close()


def create_sensors_table():
    '''Funkcja tworząca tabelę czujników (stanowisk pomiarowych)'''
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            id_sensor INTEGER PRIMARY KEY,
            station_id INTEGER,
            param_name TEXT,
            param_formula TEXT,
            param_code TEXT,
            param_id INTEGER
        );
    """)
    conn.commit()
    conn.close()



def insert_sensor(sensor):
    '''Funkcja zapisuje dane czujnika do bazy danych'''
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO sensors (id_sensor, station_id, param_name, param_formula, param_code, param_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        sensor['id'],
        sensor['stationId'],
        sensor['param']['paramName'],
        sensor['param']['paramFormula'],
        sensor['param']['paramCode'],
        sensor['param']['idParam']
    ))
    conn.commit()
    conn.close()

def clear_database():
    conn = sqlite3.connect("air_quality.db")
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM measurements;")
        cursor.execute("DELETE FROM sensors;")
        cursor.execute("DELETE FROM stations;")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e  # Przekaż błąd do GUI
    finally:
        cursor.close()
        conn.close()