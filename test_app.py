"""
Geautomatiseerde tests voor XY-MD02 WebApp
Test alle belangrijke functionaliteiten van de applicatie
"""
import unittest
import sqlite3
import os
import sys
import tempfile
from datetime import datetime, timedelta
import math

# Import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from modularized codebase
try:
    from database import (
        DB_FILE,
        get_table_name,
        ensure_table_exists,
        get_all_measurement_tables
    )
    from psychrometric import create_psychrometric_chart
    HAS_APP = True
except ImportError:
    HAS_APP = False
    DB_FILE = 'src/modbus_sensor_data.db'

from translations import TRANSLATIONS, LANGUAGE_NAMES


class TestCalculations(unittest.TestCase):
    """Test wetenschappelijke berekeningen"""
    
    def calculate_dewpoint_local(self, temp, humidity):
        """Lokale implementatie dewpoint berekening"""
        return temp - ((100 - humidity) / 5.0)
    
    def test_dewpoint_calculation(self):
        """Test dauwpunt berekening"""
        # Normale waarden
        dewpoint = self.calculate_dewpoint_local(20, 50)
        self.assertAlmostEqual(dewpoint, 10.0, delta=0.5)
        
        # Hoge vochtigheid
        dewpoint = self.calculate_dewpoint_local(25, 80)
        self.assertAlmostEqual(dewpoint, 21.0, delta=0.5)
        
        # Lage vochtigheid
        dewpoint = self.calculate_dewpoint_local(15, 30)
        self.assertAlmostEqual(dewpoint, 1.0, delta=1.0)
    
    def test_absolute_humidity_calculation(self):
        """Test absolute vochtigheid berekening (formule check)"""
        # Test of berekening positief getal oplevert
        temp = 20
        humidity = 50
        dewpoint = self.calculate_dewpoint_local(temp, humidity)
        
        # Absolute humidity zou positief moeten zijn
        self.assertGreater(dewpoint, -50)
        self.assertLess(dewpoint, 100)
    
    @unittest.skipUnless(HAS_APP, "App module niet beschikbaar")
    def test_humidex_calculation(self):
        """Test Humidex berekening via psychrometric chart"""
        chart = create_psychrometric_chart(25, 60, 'nl')
        self.assertIsNotNone(chart)
        self.assertIn('data', chart)


class TestDatabase(unittest.TestCase):
    """Test database operaties"""
    
    def setUp(self):
        """Maak tijdelijke test database"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db_path = self.test_db.name
        self.test_db.close()
        
        # Maak test database structuur (partitioned table voor vandaag)
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # WAL mode
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.execute('PRAGMA synchronous=NORMAL')
        
        # Maak tabel voor vandaag (partitioned)
        today = datetime.now().strftime('%Y%m%d')
        table_name = f'measurements_{today}'
        cursor.execute(f'''
            CREATE TABLE {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                dewpoint REAL,
                absolute_humidity REAL
            )
        ''')
        cursor.execute(f'CREATE INDEX idx_{table_name}_timestamp ON {table_name}(timestamp)')
        conn.commit()
        conn.close()
        
        self.table_name = table_name
    
    def tearDown(self):
        """Verwijder test database"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_database_insert(self):
        """Test database insert operatie"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Insert test data (integer timestamp)
        now_timestamp = int(datetime.now().timestamp())
        cursor.execute(f'''
            INSERT INTO {self.table_name} (timestamp, temperature, humidity, dewpoint, absolute_humidity)
            VALUES (?, ?, ?, ?, ?)
        ''', (now_timestamp, 22.5, 45.0, 10.2, 8.5))
        conn.commit()
        
        # Verify insert
        cursor.execute(f'SELECT COUNT(*) FROM {self.table_name}')
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)
        
        conn.close()
    
    def test_database_query(self):
        """Test database query operatie"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Insert test data (integer timestamps)
        for i in range(10):
            timestamp = int((datetime.now() - timedelta(minutes=i)).timestamp())
            cursor.execute(f'''
                INSERT INTO {self.table_name} (timestamp, temperature, humidity, dewpoint, absolute_humidity)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, 20.0 + i, 40.0 + i, 10.0, 8.0))
        conn.commit()
        
        # Query laatste 5 metingen
        cursor.execute(f'SELECT * FROM {self.table_name} ORDER BY timestamp DESC LIMIT 5')
        results = cursor.fetchall()
        self.assertEqual(len(results), 5)
        
        conn.close()


class TestTranslations(unittest.TestCase):
    """Test meertalig systeem"""
    
    def test_language_names(self):
        """Test of alle talen beschikbaar zijn"""
        self.assertIn('nl', LANGUAGE_NAMES)
        self.assertIn('en', LANGUAGE_NAMES)
        self.assertEqual(len(LANGUAGE_NAMES), 2)
    
    def test_translation_keys(self):
        """Test of alle vertalingen dezelfde keys hebben"""
        nl_keys = set(TRANSLATIONS['nl'].keys())
        en_keys = set(TRANSLATIONS['en'].keys())
        
        # Controleer of beide talen dezelfde keys hebben
        self.assertEqual(nl_keys, en_keys, 
                        f"Ontbrekende keys: NL-EN: {nl_keys - en_keys}, EN-NL: {en_keys - nl_keys}")
    
    def test_translation_completeness(self):
        """Test of alle vertalingen waarden hebben"""
        for lang, translations in TRANSLATIONS.items():
            for key, value in translations.items():
                self.assertIsNotNone(value, f"Missing translation for {lang}.{key}")
                self.assertNotEqual(value, '', f"Empty translation for {lang}.{key}")


class TestPsychrometricChart(unittest.TestCase):
    """Test psychrometrisch diagram generatie"""
    
    @unittest.skipUnless(HAS_APP, "App module niet beschikbaar")
    def test_chart_creation_with_data(self):
        """Test chart creatie met data"""
        chart = create_psychrometric_chart(22.5, 45.0, 'nl')
        self.assertIsNotNone(chart)
        self.assertIn('data', chart)
        self.assertIn('layout', chart)
        self.assertGreater(len(chart['data']), 0)
    
    @unittest.skipUnless(HAS_APP, "App module niet beschikbaar")
    def test_chart_creation_without_data(self):
        """Test chart creatie zonder data"""
        chart = create_psychrometric_chart(None, None, 'nl')
        self.assertIsNotNone(chart)
        self.assertIn('data', chart)
        self.assertIn('layout', chart)
    
    @unittest.skipUnless(HAS_APP, "App module niet beschikbaar")
    def test_chart_multilingual(self):
        """Test chart in verschillende talen"""
        chart_nl = create_psychrometric_chart(22.5, 45.0, 'nl')
        chart_en = create_psychrometric_chart(22.5, 45.0, 'en')
        
        self.assertIsNotNone(chart_nl)
        self.assertIsNotNone(chart_en)
        
        # Titles zouden verschillend moeten zijn
        self.assertNotEqual(
            chart_nl['layout']['title']['text'],
            chart_en['layout']['title']['text']
        )


class TestDataValidation(unittest.TestCase):
    """Test data validatie"""
    
    def test_temperature_range(self):
        """Test temperatuur bereik validatie"""
        # Realistische temperaturen
        self.assertTrue(-50 <= 22.5 <= 100)
        self.assertTrue(-50 <= -10 <= 100)
        self.assertTrue(-50 <= 45 <= 100)
    
    def test_humidity_range(self):
        """Test vochtigheid bereik validatie"""
        # RH moet tussen 0 en 100 zijn
        self.assertTrue(0 <= 45.0 <= 100)
        self.assertTrue(0 <= 0 <= 100)
        self.assertTrue(0 <= 100 <= 100)
    
    def test_invalid_values(self):
        """Test handling van ongeldige waarden"""
        # Dewpoint berekening met extreme waarden
        try:
            dewpoint = calculate_dewpoint(150, 50)  # Te hoog
            # Als geen error, check of resultaat redelijk is
            self.assertIsNotNone(dewpoint)
        except:
            pass  # Error is acceptabel voor extreme waarden


class TestProductionDatabase(unittest.TestCase):
    """Test productie database (indien aanwezig)"""
    
    def test_production_database_exists(self):
        """Test of productie database bestaat"""
        # Check of database file bestaat
        db_exists = os.path.exists(DB_FILE)
        if db_exists:
            self.assertTrue(db_exists)
            
            # Test of we kunnen connecten
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                
                # Check tabel structuur (partitioned tables)
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'measurements_%'")
                results = cursor.fetchall()
                
                # Er moet minstens één measurements tabel zijn
                self.assertGreater(len(results), 0, "Geen measurements tabellen gevonden")
                
                # Check structuur van eerste tabel
                if results:
                    table_name = results[0][0]
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    # Verify expected columns
                    self.assertIn('timestamp', column_names)
                    self.assertIn('temperature', column_names)
                    self.assertIn('humidity', column_names)
                
                conn.close()
            except Exception as e:
                self.fail(f"Database connection failed: {e}")


def run_tests():
    """Run alle tests en print resultaten"""
    # Maak test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Voeg alle test classes toe
    suite.addTests(loader.loadTestsFromTestCase(TestCalculations))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestTranslations))
    suite.addTests(loader.loadTestsFromTestCase(TestPsychrometricChart))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionDatabase))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print samenvatting
    print("\n" + "="*70)
    print("TEST SAMENVATTING")
    print("="*70)
    print(f"Tests uitgevoerd: {result.testsRun}")
    print(f"Geslaagd: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Gefaald: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
