# 🌡️ XY-MD02 WebApp

[🇳🇱 Nederlands](#-nederlands) | [🇬🇧 English](#-english)

---

## 🇳🇱 Nederlands

Een professionele real-time klimaatmonitoring dashboard applicatie voor de XY-MD02 sensor die Modbus RTU data inleest, visualiseert en analyseert.

### ✨ Features

- **Real-time monitoring**: Live grafieken met automatische updates (1 seconde interval)
- **Historische data**: Persistente opslag in SQLite database met tijdsfilters (1 min tot 6 maanden)
- **Meerdere metingen**:
  - Temperatuur (°C)
  - Luchtvochtigheid (%)
  - Dauwpunt (berekend)
  - Absolute vochtigheid (g/m³)
  - Behagelijkheidscore (0-6)
- **Meertalig**: Nederlands en Engels, eenvoudig uitbreidbaar
- **Professionele UI**: Modern dashboard met gradient header en card-based layout
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

### 📊 Behagelijkheidsscore

De applicatie berekent een behagelijkheidsscore (0-6) op basis van temperatuur en luchtvochtigheid:

- **6 - Optimaal**: Ideale omstandigheden (20-22°C, 40-50% RH)
- **5 - Comfortabel**: Behaaglijke omstandigheden
- **4 - Comfortabel laag**: Nog steeds comfortabel
- **3 - Licht onaangenaam**: Merkbaar oncomfortabel
- **2 - Onaangenaam**: Duidelijk oncomfortabel
- **1 - Ongezond**: Gezondheidsrisico's mogelijk
- **0 - Ongezond (risico)**: Ernstige gezondheidsrisico's

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
- **Multiple measurements**:
  - Temperature (°C)
  - Humidity (%)
  - Dew Point (calculated)
  - Absolute Humidity (g/m³)
  - Comfort Score (0-6)
- **Multilingual**: Dutch and English, easily expandable
- **Professional UI**: Modern dashboard with gradient header and card-based layout
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

### 📊 Comfort Score

The application calculates a comfort score (0-6) based on temperature and humidity:

- **6 - Optimal**: Ideal conditions (20-22°C, 40-50% RH)
- **5 - Comfortable**: Pleasant conditions
- **4 - Comfortable Low**: Still comfortable
- **3 - Slightly Uncomfortable**: Noticeably uncomfortable
- **2 - Uncomfortable**: Clearly uncomfortable
- **1 - Unhealthy**: Possible health risks
- **0 - Unhealthy (Risk)**: Serious health risks

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

