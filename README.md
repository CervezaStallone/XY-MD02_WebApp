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
- **Psychrometrisch diagram**: Volledig Mollier diagram met verzadigingslijn, RH curves, comfortzone en live indicator
- **Historische data replay**: Tijdreizen door data met preset knoppen (5min-1maand) of custom datum/tijd selectie
- **Interactieve slider**: Live updates tijdens slepen voor vloeiende historische data navigatie
- **Wetenschappelijke analyse**: Humidex formule volgens Environment Canada standaard met August-Roche-Magnus vergelijking
- **Meertalig**: Nederlands en Engels, eenvoudig uitbreidbaar
- **Professionele UI**: Modern dashboard met gradient header en card-based layout
- **Zoom behoud**: Inzoomen op grafieken blijft behouden tijdens live updates
- **Robuust**: Uitgebreide input validatie en error handling
- **Configureerbaar**: Alle settings via `.env` bestand

### 📸 Screenshots

#### Live Grafieken
![Live Grafieken](img/graph.png)
*Real-time monitoring van temperatuur, luchtvochtigheid, dauwpunt en absolute vochtigheid met automatische updates*

#### Psychrometrisch Diagram (Mollier)
![Mollier Diagram](img/mollier_diagram.png)
*Interactief Mollier diagram met verzadigingslijn, RH curves, comfortzone en live indicator*

#### Historische Data Selectie
![Date Picker](img/date_picker.png)
*Modal met preset knoppen en custom datum/tijd selectie voor historische data analyse*

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
waarby:
- T = temperatuur in °C
- e = dampdrukverzadiging in hPa (berekend via August-Roche-Magnus vergelijking)

**August-Roche-Magnus vergelijking voor dampdruk:**
```
e = 6.11 × exp(5417.7530 × ((1/273.16) - (1/Td_kelvin)))
```
waar Td_kelvin = dauwpunt in Kelvin

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

De applicatie toont een interactief **psychrometrisch diagram** (Mollier diagram) met:

- **Verzadigingslijn**: 100% relatieve vochtigheid curve (zwarte lijn)
- **RH lijnen**: 10%, 20%, ..., 90% relatieve vochtigheid (grijze lijnen)
- **Comfortzone**: Groen gemarkeerd gebied (20-26°C, 30-60% RH)
- **Live indicator**: Real-time positie van huidige klimaatconditie (rode ster ⭐)
- **Historische positie**: Oranje marker (🔶) bij gebruik van historische data replay
- **Vochtigheidsratio**: Y-as toont absolute vochtigheid in g water / kg droge lucht
- **Zoom & Pan**: Volledige Plotly interactiviteit voor gedetailleerde analyse

Dit diagram helpt om in één oogopslag te zien of de klimaatconditie binnen de comfortzone valt en hoe deze zich verhoudt tot verzadigingsgrenzen. Bij gebruik van de historische slider toont de oranje marker de positie op het geselecteerde tijdstip.

### ⏮️ Historische Data Replay

De applicatie biedt geavanceerde historische data analyse met twee invoermethoden:

#### **Preset Knoppen** (Snelle selectie)
Klik op **"Kies bereik voor historische analyse"** om de modal te openen met 11 preset knoppen:
- **5 min** - Laatste 5 minuten
- **10 min** - Laatste 10 minuten
- **30 min** - Laatste 30 minuten
- **1 uur** - Laatste uur
- **2 uur** - Laatste 2 uur
- **6 uur** - Laatste 6 uur
- **12 uur** - Laatste 12 uur
- **24 uur** - Laatste dag
- **2 dagen** - Laatste 2 dagen
- **Week** - Laatste week
- **Maand** - Laatste maand

#### **Custom Range** (Precisie selectie)
- Klik in de modal op **"Custom..."** om een aangepaste periode in te stellen
- Kies start datum en tijd met uur:minuut precisie
- Kies eind datum en tijd met uur:minuut precisie
- Ondersteunt dezelfde dag selectie voor start en eind
- Uur selectie: 00-23
- Minuut selectie: 00-59
- Validatie: start tijd moet vóór eind tijd liggen

#### **Interactieve Tijdlijn Slider**
- Na selectie van een periode verschijnt een **live-updating slider**
- Sleep de slider om terug te "reizen" door de tijd
- **Live updates tijdens slepen**: Het diagram updatet direct zonder de muis los te laten
- Het **psychrometrisch diagram** toont de positie van de klimaatconditie op dat moment (oranje marker 🔶)
- Timestamp wordt live weergegeven in DD-MM HH:MM formaat
- Vloeiende navigatie door historische data voor gedetailleerde analyse

#### **Gescheiden Live & Historische Data**
- **Live grafieken** (temperatuur, vochtigheid) blijven altijd real-time updates tonen
- **Mollier diagram** schakelt tussen live mode (rode ster ⭐) en historische mode (oranje marker 🔶)
- Geen interferentie tussen live monitoring en historische analyse

**Gebruik:**
1. Klik op **"Kies bereik voor historische analyse"** knop onder het Mollier diagram
2. Kies een preset knop voor snelle analyse of "Custom..." voor specifieke datum/tijd
3. Gebruik de **live-updating slider** om vloeiend door de historische data te navigeren
4. Bekijk hoe de klimaatconditie veranderde over tijd in het Mollier diagram
5. Live grafieken bovenaan blijven gewoon real-time data tonen

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

### 📸 Screenshots

#### Live Graphs
![Live Graphs](img/graph.png)
*Real-time monitoring of temperature, humidity, dew point and absolute humidity with automatic updates*

#### Psychrometric Chart (Mollier)
![Mollier Diagram](img/mollier_diagram.png)
*Interactive Mollier diagram with saturation line, RH curves, comfort zone and live indicator*

#### Historical Data Selection
![Date Picker](img/date_picker.png)
*Modal with preset buttons and custom date/time picker for historical data analysis*

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

### ⏮️ Historical Data Replay

The application offers advanced historical data analysis with two input methods:

#### **Preset Buttons** (Quick selection)
- **5 min** - Last 5 minutes
- **10 min** - Last 10 minutes
- **30 min** - Last 30 minutes
- **1 hour** - Last hour
- **2 hours** - Last 2 hours
- **6 hours** - Last 6 hours
- **12 hours** - Last 12 hours
- **24 hours** - Last day
- **2 days** - Last 2 days
- **Week** - Last week
- **Month** - Last month

#### **Custom Range** (Precision selection)
- Click the **"Custom..."** button to open a modal
- Choose start date and time (hour:minute)
- Choose end date and time (hour:minute)
- Supports same day selection for start and end
- Hour selection: 0-23
- Minute selection: 0-59

#### **Timeline Slider**
- After selecting a period, an **interactive slider** appears
- Drag the slider to "travel" back through time
- The **psychrometric chart** shows the climate condition position at that moment
- Timestamp is displayed live in DD-MM HH:MM format

**Usage:**
1. Click a preset button for quick analysis
2. Or click "Custom..." for specific date/time selection
3. Use the slider to navigate through historical data
4. See how the climate condition changed over time in the Mollier diagram

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

### 🧪 Testing

De applicatie bevat een geautomatiseerde test suite:

```bash
python test_app.py
```

**Test Coverage:**
- ✅ **Berekeningen**: Dauwpunt, absolute vochtigheid, Humidex formules
- ✅ **Database**: CRUD operaties, queries, schema validatie
- ✅ **Vertalingen**: NL/EN key pariteit en volledigheid
- ✅ **Psychrometrisch diagram**: Chart generatie, meertaligheid
- ✅ **Data validatie**: Temperatuur en vochtigheid ranges
- ✅ **Productie database**: Verificatie van database bestaan en structuur

Alle tests moeten slagen voordat nieuwe features worden gecommit.

### 🛠️ Development

#### Generating requirements.txt
```bash
pip freeze > requirements.txt
```

#### Code structure
- **app.py**: Modbus communication, database operations, Dash callbacks, Humidex & psychrometric calculations
- **layout.py**: UI components, modal system, slider, styling
- **translations.py**: Translation system (NL/EN)
- **test_app.py**: Automated test suite (15 tests)

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

### 📝 Version History

#### v1.1.0 (December 4, 2025)
- ➕ **Humidex calculation**: Scientific comfort index using Environment Canada standard with August-Roche-Magnus equation
- ➕ **Psychrometric chart**: Full Mollier diagram with saturation line, RH curves (10-90%), comfort zone, and live indicator
- ➕ **Historical data replay**: Time-travel through data with modal interface
- ➕ **Preset buttons**: 11 quick selection buttons (5min to 1 month)
- ➕ **Custom date/time picker**: Hour:minute precision for exact historical ranges
- ➕ **Live slider updates**: Real-time chart updates while dragging slider (no mouse release needed)
- ➕ **Layout consolidation**: Mollier diagram section with integrated historical controls
- ➕ **Separated data streams**: Live graphs remain real-time while historical replay operates independently
- ➕ **Automated test suite**: 15 tests covering calculations, database, translations, charts, and validation
- 🔧 **Improved UX**: Modal popup system, better button organization, timestamp display in DD-MM HH:MM format
- 🐛 **Bug fixes**: Fixed callback_context imports, modal opening issues, slider interaction

#### v1.0.0 (Initial Release)
- ✨ Real-time monitoring with live graphs
- ✨ SQLite database with persistent storage
- ✨ Multi-language support (NL/EN)
- ✨ Temperature, humidity, dewpoint, absolute humidity measurements
- ✨ Configurable data retention
- ✨ Professional dashboard UI

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

