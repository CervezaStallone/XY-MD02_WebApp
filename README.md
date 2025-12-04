# 🌡️ XY-MD02 WebApp

[🇳🇱 Nederlands](#-nederlands) | [🇬🇧 English](#-english)

---

## 🇳🇱 Nederlands

Een professionele real-time klimaatmonitoring dashboard applicatie voor de XY-MD02 sensor die Modbus RTU data inleest, visualiseert en analyseert.

### ✨ Features

- **Real-time monitoring**: Live grafieken met automatische updates (1 seconde interval)
- **Historische data**: Persistente opslag in SQLite database met tijdsfilters (1 min tot 6 maanden)
- **Data retentie**: Configureerbare automatische cleanup van oude data
- **Meerdere metingen**:
  - Temperatuur (°C)
  - Luchtvochtigheid (%)
  - Dauwpunt (berekend)
  - Absolute vochtigheid (g/m³)
  - Humidex (wetenschappelijke behagelijkheidsindex)
  - Behagelijkheidscore (0-6, gebaseerd op Humidex)
- **Psychrometrisch diagram**: Mollier diagram met live indicator en comfortzone visualisatie
- **Wetenschappelijke analyse**: Humidex formule volgens Environment Canada standaard
- **Meertalig**: Nederlands en Engels, eenvoudig uitbreidbaar
- **Professionele UI**: Modern dashboard met gradient header en card-based layout
- **Zoom behoud**: Inzoomen op grafieken blijft behouden tijdens live updates
- **Robuust**: Uitgebreide input validatie en error handling
- **Configureerbaar**: Alle settings via `.env` bestand

### 📋 Requirements

- Python 3.8+
- Modbus RTU apparaat (RS485)
- Windows, Linux of macOS

### 🚀 Installatie

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

### 📁 Projectstructuur

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

### 🔧 Configuratie

#### Modbus Settings

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

#### Database Settings

- `DATABASE_FILE`: Pad naar de SQLite database file
- `DATA_RETENTION_DAYS`: Data retentie in dagen (0 = oneindig, anders aantal dagen dat data bewaard blijft)

#### Application Settings

- `APP_HOST`: Server host IP (127.0.0.1 voor lokaal)
- `APP_PORT`: Server poort (8050)
- `APP_DEBUG`: Debug mode (True/False)

### 🌍 Nieuwe taal toevoegen

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

### 📊 Behagelijkheidsscore & Humidex

De applicatie gebruikt de **Humidex** (Humidity Index) voor wetenschappelijke behagelijkheidsberekening volgens Environment Canada standaard.

#### Humidex Formule
```
Humidex = T + 0.5555 × (e - 10)
```
waarbij:
- T = temperatuur in °C
- e = dampdrukverzadiging in hPa (berekend via dauwpunt)

#### Comfort classificatie op basis van Humidex:

- **< 20**: Te koud - Score 0 🥶
- **20-27**: Comfortabel koel - Score 4 🙂
- **27-30**: Comfortabel - Score 5 😊
- **30-35**: Optimaal comfortabel - Score 6 ✨
- **35-40**: Enig ongemak - Score 3 😓
- **40-46**: Veel ongemak, vermijd fysieke inspanning - Score 2 😟
- **46-54**: Gevaarlijk, hittekrampen mogelijk - Score 1 🔥
- **> 54**: Heatstroke dreigend - Score 0 ⚠️

### 📐 Mollier Diagram (Psychrometric Chart)

De applicatie toont een interactief **psychrometrisch diagram** onderaan de pagina met:

- **Verzadigingslijn**: 100% relatieve vochtigheid curve
- **RH lijnen**: 10%, 20%, ..., 90% relatieve vochtigheid
- **Comfortzone**: Gemarkeerd gebied (20-26°C, 30-60% RH)
- **Live indicator**: Real-time positie van huidige klimaatconditie (rode ster ⭐)
- **Vochtigheidsratio**: Y-as toont absolute vochtigheid in g water / kg droge lucht

Dit diagram helpt om in één oogopslag te zien of de klimaatconditie binnen de comfortzone valt en hoe deze zich verhoudt tot verzadigingsgrenzen.

### 📈 Database Schema

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

### 🛠️ Development

#### Requirements.txt genereren
```bash
pip freeze > requirements.txt
```

#### Code structuur
- **app.py**: Modbus communicatie, database operaties, Dash callbacks
- **layout.py**: UI componenten en styling
- **translations.py**: Vertaalsysteem

### 🐛 Troubleshooting

#### Modbus connectie problemen
- Controleer of de seriële poort correct is (`MODBUS_PORT` in `.env`)
- Verifieer de baudrate en andere seriële instellingen
- Controleer de register nummers in de apparaat documentatie

#### Database errors
- Zorg dat de `src/` folder bestaat
- Controleer schrijfrechten in de project folder

#### Port al in gebruik
- Wijzig `APP_PORT` in `.env` naar een andere poort

### 📜 Licentie

Dit project is open source en beschikbaar onder de [MIT License](LICENSE).

```
MIT License

Copyright (c) 2025 XY-MD02 WebApp Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🇬🇧 English

A professional real-time climate monitoring dashboard application for the XY-MD02 sensor that reads, visualizes, and analyzes Modbus RTU data.

### ✨ Features

- **Real-time monitoring**: Live charts with automatic updates (1 second interval)
- **Historical data**: Persistent storage in SQLite database with time filters (1 min to 6 months)
- **Data retention**: Configurable automatic cleanup of old data
- **Multiple measurements**:
  - Temperature (°C)
  - Humidity (%)
  - Dew Point (calculated)
  - Absolute Humidity (g/m³)
  - Humidex (scientific comfort index)
  - Comfort Score (0-6, based on Humidex)
- **Psychrometric chart**: Mollier diagram with live indicator and comfort zone visualization
- **Scientific analysis**: Humidex formula according to Environment Canada standard
- **Multilingual**: Dutch and English, easily expandable
- **Professional UI**: Modern dashboard with gradient header and card-based layout
- **Zoom persistence**: Graph zoom stays preserved during live updates
- **Robust**: Extensive input validation and error handling
- **Configurable**: All settings via `.env` file

### 📋 Requirements

- Python 3.8+
- Modbus RTU device (RS485)
- Windows, Linux or macOS

### 🚀 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd "Modbus Graph"
```

2. **Create a virtual environment**
```bash
python -m venv .venv
```

3. **Activate the virtual environment**

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

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure the application**

Copy the example configuration file:
```bash
cp .env.example .env
```

Adjust the settings in `.env`:
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

6. **Start the application**
```bash
python app.py
```

The application is now available at: `http://127.0.0.1:8050/`

### 📁 Project Structure

```
Modbus Graph/
├── app.py                    # Main application with Modbus communication and callbacks
├── layout.py                 # HTML layout and CSS styling
├── translations.py           # Multilingual system (NL/EN)
├── .env                      # Configuration (not in git)
├── .env.example              # Example configuration
├── requirements.txt          # Python dependencies
├── .gitignore               # Git exclude rules
├── README.md                # This file
└── src/                     # Data directory
    └── modbus_sensor_data.db  # SQLite database (not in git)
```

### 🔧 Configuration

#### Modbus Settings

- `MODBUS_PORT`: Serial port (e.g. COM11, /dev/ttyUSB0)
- `MODBUS_SLAVE_ID`: Slave ID of the device
- `MODBUS_BAUDRATE`: Baudrate (9600, 19200, etc.)
- `MODBUS_BYTESIZE`: Number of data bits (8)
- `MODBUS_PARITY`: Parity bit (N = None, E = Even, O = Odd)
- `MODBUS_STOPBITS`: Stop bits (1, 2)
- `MODBUS_TIMEOUT`: Timeout in seconds
- `MODBUS_FUNCTION_CODE`: Modbus function code (4 = Read Input Registers)
- `MODBUS_REGISTER_TEMP`: Register number for temperature
- `MODBUS_REGISTER_HUMIDITY`: Register number for humidity

#### Database Settings

- `DATABASE_FILE`: Path to the SQLite database file
- `DATA_RETENTION_DAYS`: Data retention in days (0 = infinite, otherwise number of days to keep data)

#### Application Settings

- `APP_HOST`: Server host IP (127.0.0.1 for local)
- `APP_PORT`: Server port (8050)
- `APP_DEBUG`: Debug mode (True/False)

### 🌍 Adding a New Language

1. Open `translations.py`

2. Add the language to `LANGUAGE_NAMES`:
```python
LANGUAGE_NAMES = {
    'nl': '🇳🇱 NL',
    'en': '🇬🇧 EN',
    'de': '🇩🇪 DE'  # New!
}
```

3. Add the translations to `TRANSLATIONS`:
```python
TRANSLATIONS = {
    'nl': { ... },
    'en': { ... },
    'de': {
        'title': '🌡️ Modbus Klimamonitor',
        'temperature': 'Temperatur',
        'humidity': 'Luftfeuchtigkeit',
        # ... all other keys
    }
}
```

The dropdown will be updated automatically!

### 📊 Comfort Score & Humidex

The application uses the **Humidex** (Humidity Index) for scientific comfort calculation according to Environment Canada standard.

#### Humidex Formula
```
Humidex = T + 0.5555 × (e - 10)
```
where:
- T = temperature in °C
- e = vapor pressure saturation in hPa (calculated via dew point)

#### Comfort classification based on Humidex:

- **< 20**: Too cold - Score 0 🥶
- **20-27**: Comfortably cool - Score 4 🙂
- **27-30**: Comfortable - Score 5 😊
- **30-35**: Optimally comfortable - Score 6 ✨
- **35-40**: Some discomfort - Score 3 😓
- **40-46**: Great discomfort, avoid physical exertion - Score 2 😟
- **46-54**: Dangerous, heat cramps possible - Score 1 🔥
- **> 54**: Heat stroke imminent - Score 0 ⚠️

### 📐 Mollier Diagram (Psychrometric Chart)

The application displays an interactive **psychrometric chart** at the bottom of the page with:

- **Saturation line**: 100% relative humidity curve
- **RH lines**: 10%, 20%, ..., 90% relative humidity
- **Comfort zone**: Marked area (20-26°C, 30-60% RH)
- **Live indicator**: Real-time position of current climate condition (red star ⭐)
- **Humidity ratio**: Y-axis shows absolute humidity in g water / kg dry air

This diagram helps to see at a glance whether the climate condition is within the comfort zone and how it relates to saturation limits.

### 📈 Database Schema

The SQLite database stores all measurements:

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

### 🛠️ Development

#### Generating requirements.txt
```bash
pip freeze > requirements.txt
```

#### Code structure
- **app.py**: Modbus communication, database operations, Dash callbacks
- **layout.py**: UI components and styling
- **translations.py**: Translation system

### 🐛 Troubleshooting

#### Modbus connection problems
- Check if the serial port is correct (`MODBUS_PORT` in `.env`)
- Verify the baudrate and other serial settings
- Check the register numbers in the device documentation

#### Database errors
- Ensure the `src/` folder exists
- Check write permissions in the project folder

#### Port already in use
- Change `APP_PORT` in `.env` to another port

### 📜 License

This project is open source and available under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2025 XY-MD02 WebApp Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

