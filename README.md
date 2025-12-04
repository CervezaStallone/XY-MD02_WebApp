# 🌡️ XY-MD02 WebApp

Een professionele real-time klimaatmonitoring dashboard applicatie voor de XY-MD02 sensor die Modbus RTU data inleest, visualiseert en analyseert.

## ✨ Features

- **Real-time monitoring**: Live grafieken met automatische updates (1 seconde interval)
- **Historische data**: Persistente opslag in SQLite database met tijdsfilters (1 min tot 7 dagen)
- **Meerdere metingen**:
  - Temperatuur (°C)
  - Luchtvochtigheid (%)
  - Dauwpunt (berekend)
  - Absolute vochtigheid (g/m³)
  - Behagelijkheidscore (0-6)
- **Meertalig**: Nederlands en Engels, eenvoudig uitbreidbaar
- **Professionele UI**: Modern dashboard met gradient header en card-based layout
- **Configureerbaar**: Alle settings via `.env` bestand

## 📋 Requirements

- Python 3.8+
- Modbus RTU apparaat (RS485)
- Windows, Linux of macOS

## 🚀 Installatie

1. **Clone de repository**
```bash
git clone <repository-url>
cd "Modbus Graph"
```

2. **Maak een virtual environment**
```bash
python -m venv .venv
```

3. **Activeer de virtual environment**

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:
```cmd
.venv\Scripts\activate.bat
```

Linux/macOS:
```bash
source .venv/bin/activate
```

4. **Installeer dependencies**
```bash
pip install -r requirements.txt
```

5. **Configureer de applicatie**

Kopieer het voorbeeld configuratie bestand:
```bash
cp .env.example .env
```

Pas de instellingen aan in `.env`:
```env
# Modbus Settings
MODBUS_PORT=COM11
MODBUS_SLAVE_ID=1
MODBUS_BAUDRATE=9600
MODBUS_REGISTER_TEMP=1
MODBUS_REGISTER_HUMIDITY=2

# Database Settings
DATABASE_FILE=src/modbus_sensor_data.db

# Application Settings
APP_HOST=127.0.0.1
APP_PORT=8050
APP_DEBUG=False
```

6. **Start de applicatie**
```bash
python app.py
```

De applicatie is nu beschikbaar op: `http://127.0.0.1:8050/`

## 📁 Projectstructuur

```
Modbus Graph/
├── app.py                    # Hoofdapplicatie met Modbus communicatie en callbacks
├── layout.py                 # HTML layout en CSS styling
├── translations.py           # Meertalig systeem (NL/EN)
├── .env                      # Configuratie (niet in git)
├── .env.example              # Voorbeeld configuratie
├── requirements.txt          # Python dependencies
├── .gitignore               # Git exclude rules
├── README.md                # Deze file
└── src/                     # Data directory
    └── modbus_sensor_data.db  # SQLite database (niet in git)
```

## 🔧 Configuratie

### Modbus Settings

- `MODBUS_PORT`: Seriële poort (bijv. COM11, /dev/ttyUSB0)
- `MODBUS_SLAVE_ID`: Slave ID van het apparaat
- `MODBUS_BAUDRATE`: Baudrate (9600, 19200, etc.)
- `MODBUS_BYTESIZE`: Aantal data bits (8)
- `MODBUS_PARITY`: Parity bit (N = None, E = Even, O = Odd)
- `MODBUS_STOPBITS`: Stop bits (1, 2)
- `MODBUS_TIMEOUT`: Timeout in seconden
- `MODBUS_FUNCTION_CODE`: Modbus functie code (4 = Read Input Registers)
- `MODBUS_REGISTER_TEMP`: Register nummer voor temperatuur
- `MODBUS_REGISTER_HUMIDITY`: Register nummer voor luchtvochtigheid

### Database Settings

- `DATABASE_FILE`: Pad naar de SQLite database file

### Application Settings

- `APP_HOST`: Server host IP (127.0.0.1 voor lokaal)
- `APP_PORT`: Server poort (8050)
- `APP_DEBUG`: Debug mode (True/False)

## 🌍 Nieuwe taal toevoegen

1. Open `translations.py`

2. Voeg de taal toe aan `LANGUAGE_NAMES`:
```python
LANGUAGE_NAMES = {
    'nl': '🇳🇱 Nederlands',
    'en': '🇬🇧 English',
    'de': '🇩🇪 Deutsch'  # Nieuw!
}
```

3. Voeg de vertalingen toe aan `TRANSLATIONS`:
```python
TRANSLATIONS = {
    'nl': { ... },
    'en': { ... },
    'de': {
        'title': '🌡️ Modbus Klimamonitor',
        'temperature': 'Temperatur',
        'humidity': 'Luftfeuchtigkeit',
        # ... alle andere keys
    }
}
```

De dropdown wordt automatisch bijgewerkt!

## 📊 Behagelijkheidsscore

De applicatie berekent een behagelijkheidsscore (0-6) op basis van temperatuur en luchtvochtigheid:

- **6 - Optimaal**: Ideale omstandigheden (20-22°C, 40-50% RH)
- **5 - Comfortabel**: Behaaglijke omstandigheden
- **4 - Comfortabel laag**: Nog steeds comfortabel
- **3 - Licht onaangenaam**: Merkbaar oncomfortabel
- **2 - Onaangenaam**: Duidelijk oncomfortabel
- **1 - Ongezond**: Gezondheidsrisico's mogelijk
- **0 - Ongezond (risico)**: Ernstige gezondheidsrisico's

## 📈 Database Schema

De SQLite database slaat alle metingen op:

```sql
CREATE TABLE measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    dewpoint REAL,
    absolute_humidity REAL
);
```

## 🛠️ Development

### Requirements.txt genereren
```bash
pip freeze > requirements.txt
```

### Code structuur
- **app.py**: Modbus communicatie, database operaties, Dash callbacks
- **layout.py**: UI componenten en styling
- **translations.py**: Vertaalsysteem

## 🐛 Troubleshooting

### Modbus connectie problemen
- Controleer of de seriële poort correct is (`MODBUS_PORT` in `.env`)
- Verifieer de baudrate en andere seriële instellingen
- Controleer de register nummers in de apparaat documentatie

### Database errors
- Zorg dat de `src/` folder bestaat
- Controleer schrijfrechten in de project folder

### Port al in gebruik
- Wijzig `APP_PORT` in `.env` naar een andere poort

## 📝 License

[Voeg hier je license toe]

## 👤 Author

[Voeg hier je naam toe]

## 🙏 Acknowledgments

- Dash/Plotly voor de visualisatie framework
- MinimalModbus voor de Modbus communicatie
- Python-dotenv voor environment configuratie
