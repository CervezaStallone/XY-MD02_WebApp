import sqlite3
from datetime import datetime

conn = sqlite3.connect('src/modbus_sensor_data.db')
cursor = conn.cursor()

# Check welke tabellen er zijn
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'measurements_%' ORDER BY name").fetchall()
print(f"Tables found: {[t[0] for t in tables]}")

# Check of er data in de huidige dag tabel is
today_table = f"measurements_{datetime.now().strftime('%Y%m%d')}"
print(f"\nChecking table: {today_table}")

try:
    count = cursor.execute(f"SELECT COUNT(*) FROM {today_table}").fetchone()[0]
    print(f"Records in {today_table}: {count}")
    
    if count > 0:
        latest = cursor.execute(f"SELECT timestamp, temperature, humidity FROM {today_table} ORDER BY timestamp DESC LIMIT 1").fetchone()
        print(f"Latest record: timestamp={latest[0]}, temp={latest[1]}, humidity={latest[2]}")
except Exception as e:
    print(f"Error: {e}")

conn.close()
