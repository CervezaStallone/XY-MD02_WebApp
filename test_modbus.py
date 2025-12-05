"""Check database inhoud EN timestamps"""
import sqlite3
from datetime import datetime
from database import DB_FILE, get_all_measurement_tables

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print("=== DATABASE CHECK ===\n")

# Haal alle tabellen op
tables = get_all_measurement_tables(cursor)
print(f"Tabellen gevonden: {tables}\n")

for table in tables:
    # Tel records
    result = cursor.execute(f'SELECT COUNT(*) FROM {table}').fetchone()
    count = result[0]
    print(f"Tabel: {table}")
    print(f"  Records: {count}")
    
    if count > 0:
        # Haal eerste en laatste record op
        first = cursor.execute(f'SELECT timestamp, temperature, humidity FROM {table} ORDER BY timestamp ASC LIMIT 1').fetchone()
        last = cursor.execute(f'SELECT timestamp, temperature, humidity FROM {table} ORDER BY timestamp DESC LIMIT 1').fetchone()
        
        print(f"  Eerste record:")
        print(f"    Timestamp (int): {first[0]}")
        print(f"    Datetime: {datetime.fromtimestamp(first[0])}")
        print(f"    Temp: {first[1]}°C, Humidity: {first[2]}%")
        print(f"  Laatste record:")
        print(f"    Timestamp (int): {last[0]}")
        print(f"    Datetime: {datetime.fromtimestamp(last[0])}")
        print(f"    Temp: {last[1]}°C, Humidity: {last[2]}%")
    print()

conn.close()

# Test ook de query
print("\n=== TEST UNION QUERY ===")
from database import build_union_query
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

columns = ['timestamp', 'temperature', 'humidity']
query, table_count = build_union_query(cursor, columns)

if query:
    print(f"Query gebouwd voor {table_count} tabellen")
    print(f"Query: {query[:200]}...")
    
    # Test uitvoeren
    result = cursor.execute(query).fetchall()
    print(f"\nQuery resultaat: {len(result)} rijen")
    if result:
        print(f"Eerste rij: {result[0]}")
        print(f"Laatste rij: {result[-1]}")
else:
    print("FOUT: Geen query gebouwd!")

conn.close()
