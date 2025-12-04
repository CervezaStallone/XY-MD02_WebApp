import minimalmodbus
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html
from dash.dependencies import Input, Output, State
from datetime import datetime, timedelta
import threading
import sqlite3
import pandas as pd
import math
import os
from dotenv import load_dotenv

# Import externe modules
from translations import TRANSLATIONS
from layout import create_layout, HTML_TEMPLATE

# Laad environment variabelen
load_dotenv()

# Database configuratie
DB_FILE = os.getenv('DATABASE_FILE', 'src/modbus_sensor_data.db')

def init_database():
    """Initialiseer database met measurements tabel"""
    # Zorg dat de src directory bestaat
    db_dir = os.path.dirname(DB_FILE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            dewpoint REAL,
            absolute_humidity REAL
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON measurements(timestamp)')
    conn.commit()
    conn.close()

init_database()

# Modbus configuratie uit environment
MODBUS_PORT = os.getenv('MODBUS_PORT', 'COM11')
MODBUS_SLAVE_ID = int(os.getenv('MODBUS_SLAVE_ID', '1'))
MODBUS_BAUDRATE = int(os.getenv('MODBUS_BAUDRATE', '9600'))
MODBUS_BYTESIZE = int(os.getenv('MODBUS_BYTESIZE', '8'))
MODBUS_PARITY = os.getenv('MODBUS_PARITY', 'N')
MODBUS_STOPBITS = int(os.getenv('MODBUS_STOPBITS', '1'))
MODBUS_TIMEOUT = int(os.getenv('MODBUS_TIMEOUT', '1'))
MODBUS_FUNCTION_CODE = int(os.getenv('MODBUS_FUNCTION_CODE', '4'))
MODBUS_REGISTER_TEMP = int(os.getenv('MODBUS_REGISTER_TEMP', '1'))
MODBUS_REGISTER_HUMIDITY = int(os.getenv('MODBUS_REGISTER_HUMIDITY', '2'))

# Configuratie van Modbus RTU apparaat
instrument = minimalmodbus.Instrument(MODBUS_PORT, MODBUS_SLAVE_ID)
instrument.serial.baudrate = MODBUS_BAUDRATE
instrument.serial.bytesize = MODBUS_BYTESIZE
instrument.serial.parity = minimalmodbus.serial.PARITY_NONE if MODBUS_PARITY == 'N' else MODBUS_PARITY
instrument.serial.stopbits = MODBUS_STOPBITS
instrument.serial.timeout = MODBUS_TIMEOUT

def read_modbus_data():
    """Thread functie om Modbus data te lezen en op te slaan"""
    while True:
        try:
            register_temp = instrument.read_register(MODBUS_REGISTER_TEMP, 0, MODBUS_FUNCTION_CODE)
            register_humidity = instrument.read_register(MODBUS_REGISTER_HUMIDITY, 0, MODBUS_FUNCTION_CODE)
            
            temperature = register_temp / 10
            humidity = register_humidity / 10
            
            # Bereken dauwpunt
            dewpoint = temperature - ((100 - humidity) / 5.0)
            
            # Bereken absolute vochtigheid (g/m³)
            # Formule: AH = (6.112 × e^((17.67 × T)/(T+243.5)) × RH × 2.1674) / (273.15+T)
            absolute_humidity = (6.112 * math.exp((17.67 * temperature) / (temperature + 243.5)) * humidity * 2.1674) / (273.15 + temperature)
            
            # Opslaan in database
            timestamp = datetime.now()
            timestamp_str = timestamp.isoformat()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO measurements (timestamp, temperature, humidity, dewpoint, absolute_humidity) VALUES (?, ?, ?, ?, ?)',
                (timestamp_str, temperature, humidity, dewpoint, absolute_humidity)
            )
            conn.commit()
            conn.close()
            
            print(f"{timestamp.strftime('%H:%M:%S')} - Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%, Dewpoint: {dewpoint:.1f}°C, Absolute Humidity: {absolute_humidity:.1f}g/m³")
            
            time.sleep(1)
        except Exception as e:
            print(f"Modbus fout: {e}")
            time.sleep(5)

# Start Modbus thread
modbus_thread = threading.Thread(target=read_modbus_data, daemon=True)
modbus_thread.start()

# Dash applicatie
app = Dash(__name__)
app.index_string = HTML_TEMPLATE
app.layout = create_layout()

# Callback voor taalwijziging
@app.callback(
    [Output('selected-language', 'data'),
     Output('page-title', 'children'),
     Output('label-temperature', 'children'),
     Output('label-humidity', 'children'),
     Output('label-dewpoint', 'children'),
     Output('label-abs-humidity', 'children'),
     Output('label-comfort', 'children'),
     Output('label-score', 'children'),
     Output('label-time-period', 'children'),
     Output('label-database', 'children'),
     Output('tooltip-content', 'children'),
     Output('time-range-dropdown', 'options')],
    [Input('language-selector', 'value')]
)
def update_language(lang):
    """Update alle labels op basis van geselecteerde taal"""
    t = TRANSLATIONS[lang]
    
    # Tooltip content met vertalingen
    tooltip_content = [
        t['score_explanation'] + ":",
        html.Br(),
        f"0 = {t['comfort_0']}",
        html.Br(),
        f"1 = {t['comfort_1']}",
        html.Br(),
        f"2 = {t['comfort_2']}",
        html.Br(),
        f"3 = {t['comfort_3']}",
        html.Br(),
        f"4 = {t['comfort_4']}",
        html.Br(),
        f"5 = {t['comfort_5']}",
        html.Br(),
        f"6 = {t['comfort_6']}"
    ]
    
    # Dropdown opties met vertalingen
    dropdown_options = [
        {'label': t['last_1min'], 'value': 1},
        {'label': t['last_5min'], 'value': 5},
        {'label': t['last_15min'], 'value': 15},
        {'label': t['last_30min'], 'value': 30},
        {'label': t['last_1hour'], 'value': 60},
        {'label': t['last_6hours'], 'value': 360},
        {'label': t['last_24hours'], 'value': 1440},
        {'label': t['last_7days'], 'value': 10080},
        {'label': t['last_14days'], 'value': 20160},
        {'label': t['last_1month'], 'value': 43200},
        {'label': t['last_3months'], 'value': 129600},
        {'label': t['last_6months'], 'value': 259200},
        {'label': t['all_data'], 'value': -1}
    ]
    
    return (
        lang,
        t['title'],
        t['temperature'],
        t['humidity'],
        t['dewpoint'],
        t['abs_humidity'],
        t['comfort'],
        t['score'] + ': ',
        t['time_period'],
        t['database'],
        tooltip_content,
        dropdown_options
    )

@app.callback(
    [Output('live-graph', 'figure'),
     Output('data-count', 'children'),
     Output('current-temp', 'children'),
     Output('current-humidity', 'children'),
     Output('current-dewpoint', 'children'),
     Output('current-abs-humidity', 'children'),
     Output('comfort-level', 'children'),
     Output('comfort-score', 'children'),
     Output('comfort-icon', 'children')],
    [Input('graph-update', 'n_intervals'),
     Input('time-range-dropdown', 'value')],
    [State('selected-language', 'data')]
)
def update_graph(n, time_range_minutes, lang):
    """Update grafieken en metingen op basis van tijdsbereik"""
    if lang is None:
        lang = 'nl'
    
    t = TRANSLATIONS[lang]
    
    def get_comfort_level(temp, humidity):
        """Bepaal comfort level op basis van temperatuur en luchtvochtigheid"""
        # Definieer de comfort matrix (score en emoji mapping)
        comfort_data = {
            16: {30: (2, "❄️"), 40: (2, "❄️"), 50: (3, "🌧️"), 60: (3, "🌧️"), 70: (2, "❄️")},
            18: {30: (3, "🌧️"), 40: (4, "🙂"), 50: (5, "😊"), 60: (3, "🌧️"), 70: (2, "😟")},
            20: {30: (4, "🙂"), 40: (5, "😊"), 50: (6, "✨"), 60: (5, "😊"), 70: (3, "🌧️")},
            22: {30: (5, "😊"), 40: (6, "✨"), 50: (6, "✨"), 60: (5, "😊"), 70: (3, "😓")},
            24: {30: (4, "🙂"), 40: (5, "😊"), 50: (5, "😊"), 60: (3, "😓"), 70: (2, "😟")},
            26: {30: (3, "😓"), 40: (3, "😓"), 50: (3, "😓"), 60: (2, "😟"), 70: (1, "🔥")},
            28: {30: (2, "😥"), 40: (2, "😥"), 50: (2, "😟"), 60: (1, "🔥"), 70: (0, "⚠️")},
            30: {30: (1, "🔥"), 40: (1, "🔥"), 50: (1, "🔥"), 60: (0, "⚠️"), 70: (0, "⚠️")}
        }
        
        # Vind dichtstbijzijnde temperatuur (afgerond naar 2 graden)
        temp_keys = [16, 18, 20, 22, 24, 26, 28, 30]
        closest_temp = min(temp_keys, key=lambda x: abs(x - temp))
        
        # Vind dichtstbijzijnde luchtvochtigheid (afgerond naar 10%)
        hum_keys = [30, 40, 50, 60, 70]
        closest_hum = min(hum_keys, key=lambda x: abs(x - humidity))
        
        score, emoji = comfort_data.get(closest_temp, {}).get(closest_hum, (3, "❓"))
        comfort_text = t[f'comfort_{score}']
        return comfort_text, score, emoji
    
    conn = sqlite3.connect(DB_FILE)
    
    # Haal totaal aantal metingen op
    total_count = pd.read_sql_query('SELECT COUNT(*) as count FROM measurements', conn)['count'][0]
    
    # Bepaal tijdsfilter
    if time_range_minutes == -1:
        # Alle data
        query = 'SELECT timestamp, temperature, humidity, dewpoint, absolute_humidity FROM measurements ORDER BY timestamp'
        df = pd.read_sql_query(query, conn)
    else:
        # Filter op tijdsbereik
        cutoff_time = datetime.now() - timedelta(minutes=time_range_minutes)
        query = '''
            SELECT timestamp, temperature, humidity, dewpoint, absolute_humidity 
            FROM measurements 
            WHERE timestamp >= ?
            ORDER BY timestamp
        '''
        df = pd.read_sql_query(query, conn, params=(cutoff_time.isoformat(),))
    
    conn.close()
    
    if df.empty:
        return go.Figure(), f"{total_count} {t['measurements']}", "-- °C", "-- %", "-- °C", "-- g/m³", t['no_data'], "--", "❓"
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
    df['timestamp_formatted'] = df['timestamp'].dt.strftime('%d-%m-%Y %H:%M:%S')
    
    # Haal laatste waarden op
    latest_temp = df['temperature'].iloc[-1]
    latest_humidity = df['humidity'].iloc[-1]
    latest_dewpoint = df['dewpoint'].iloc[-1] if 'dewpoint' in df.columns else latest_temp - ((100 - latest_humidity) / 5.0)
    
    # Bereken absolute humidity als die niet in database zit
    if 'absolute_humidity' in df.columns:
        latest_abs_humidity = df['absolute_humidity'].iloc[-1]
    else:
        latest_abs_humidity = (6.112 * math.exp((17.67 * latest_temp) / (latest_temp + 243.5)) * latest_humidity * 2.1674) / (273.15 + latest_temp)
    
    # Maak subplots
    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=(f'🌡️ {t["temperature"]}', f'💧 {t["humidity"]}', f'💦 {t["dewpoint"]}', f'🌫️ {t["abs_humidity"]}'),
        vertical_spacing=0.06
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['temperature'],
            mode='lines',
            name=t['temperature'],
            line=dict(color='#3498db', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.1)',
            hovertemplate='<b>%{y:.1f}°C</b><br>%{customdata}<extra></extra>',
            customdata=df['timestamp_formatted']
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['humidity'], 
            mode='lines',
            name=t['humidity'],
            line=dict(color='#e74c3c', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.1)',
            hovertemplate='<b>%{y:.1f}%</b><br>%{customdata}<extra></extra>',
            customdata=df['timestamp_formatted']
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['dewpoint'] if 'dewpoint' in df.columns else df['temperature'] - ((100 - df['humidity']) / 5.0), 
            mode='lines',
            name=t['dewpoint'],
            line=dict(color='#9b59b6', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(155, 89, 182, 0.1)',
            hovertemplate='<b>%{y:.1f}°C</b><br>%{customdata}<extra></extra>',
            customdata=df['timestamp_formatted']
        ),
        row=3, col=1
    )
    
    # Bereken absolute humidity voor grafiek als niet aanwezig
    if 'absolute_humidity' in df.columns:
        abs_hum_data = df['absolute_humidity']
    else:
        abs_hum_data = (6.112 * (df['temperature'] + 243.5).apply(lambda temp: math.exp((17.67 * (temp - 243.5)) / temp)) * df['humidity'] * 2.1674) / (273.15 + df['temperature'])
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=abs_hum_data,
            mode='lines',
            name=t['abs_humidity'],
            line=dict(color='#16a085', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(22, 160, 133, 0.1)',
            hovertemplate='<b>%{y:.1f}g/m³</b><br>%{customdata}<extra></extra>',
            customdata=df['timestamp_formatted']
        ),
        row=4, col=1
    )
    
    fig.update_xaxes(
        title_text=t['time'], 
        row=4, col=1,
        showgrid=True,
        gridcolor='rgba(0,0,0,0.05)'
    )
    fig.update_yaxes(
        title_text=f"{t['temperature']} (°C)", 
        row=1, col=1,
        showgrid=True,
        gridcolor='rgba(0,0,0,0.05)',
        range=[0, 50]
    )
    fig.update_yaxes(
        title_text=f"{t['humidity']} (%)", 
        row=2, col=1,
        showgrid=True,
        gridcolor='rgba(0,0,0,0.05)',
        range=[0, 100]
    )
    fig.update_yaxes(
        title_text=f"{t['dewpoint']} (°C)", 
        row=3, col=1,
        showgrid=True,
        gridcolor='rgba(0,0,0,0.05)',
        range=[0, 50]
    )
    fig.update_yaxes(
        title_text=f"{t['abs_humidity']} (g/m³)", 
        row=4, col=1,
        showgrid=True,
        gridcolor='rgba(0,0,0,0.05)',
        range=[0, 25]
    )
    
    fig.update_layout(
        height=900,
        showlegend=False,
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0.02)',
        paper_bgcolor='white',
        margin=dict(l=60, r=30, t=50, b=40),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial, sans-serif",
            font_color="#2c3e50",
            bordercolor="#2c3e50",
            align="left"
        )
    )
    
    # Bepaal comfort level
    comfort_text, comfort_score, comfort_icon = get_comfort_level(latest_temp, latest_humidity)
    
    return fig, f"📊 {total_count} {t['measurements']}", f"{latest_temp:.1f} °C", f"{latest_humidity:.1f} %", f"{latest_dewpoint:.1f} °C", f"{latest_abs_humidity:.1f} g/m³", comfort_text, str(comfort_score), comfort_icon

if __name__ == '__main__':
    # Applicatie configuratie uit environment
    APP_HOST = os.getenv('APP_HOST', '127.0.0.1')
    APP_PORT = int(os.getenv('APP_PORT', '8050'))
    APP_DEBUG = os.getenv('APP_DEBUG', 'False').lower() == 'true'
    
    print(f"Dashboard gestart op http://{APP_HOST}:{APP_PORT}/")
    app.run(debug=APP_DEBUG, host=APP_HOST, port=APP_PORT)
