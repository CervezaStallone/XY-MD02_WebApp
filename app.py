import minimalmodbus
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, callback_context, no_update
from dash.dependencies import Input, Output, State
from datetime import datetime, timedelta
import threading
import sqlite3
import pandas as pd
import math
import os
import numpy as np
from dotenv import load_dotenv

# Import externe modules
from translations import TRANSLATIONS
from layout import create_layout, HTML_TEMPLATE

# Laad environment variabelen
load_dotenv()

# Database configuratie
DB_FILE = os.getenv('DATABASE_FILE', 'src/modbus_sensor_data.db')
DATA_RETENTION_DAYS = int(os.getenv('DATA_RETENTION_DAYS', '0'))  # 0 = oneindig, anders aantal dagen

if DATA_RETENTION_DAYS < 0:
    print(f"Waarschuwing: DATA_RETENTION_DAYS kan niet negatief zijn ({DATA_RETENTION_DAYS}), gebruik 0 voor oneindig")
    DATA_RETENTION_DAYS = 0

def init_database():
    """Initialiseer database met measurements tabel"""
    try:
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
        print(f"Database geïnitialiseerd: {DB_FILE}")
        if DATA_RETENTION_DAYS > 0:
            print(f"Data retentie actief: {DATA_RETENTION_DAYS} dagen")
        else:
            print("Data retentie: oneindig (alle data wordt bewaard)")
    except Exception as e:
        print(f"FOUT: Kan database niet initialiseren: {e}")
        print("Controleer schrijfrechten en of het bestand niet corrupt is.")
        raise

def cleanup_old_data():
    """Verwijder oude data op basis van retention policy"""
    if DATA_RETENTION_DAYS == 0:
        return  # Geen cleanup als retentie oneindig is
    
    try:
        cutoff_date = datetime.now() - timedelta(days=DATA_RETENTION_DAYS)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Tel hoeveel records verwijderd worden
        cursor.execute('SELECT COUNT(*) FROM measurements WHERE timestamp < ?', (cutoff_date.isoformat(),))
        count_to_delete = cursor.fetchone()[0]
        
        if count_to_delete > 0:
            cursor.execute('DELETE FROM measurements WHERE timestamp < ?', (cutoff_date.isoformat(),))
            conn.commit()
            print(f"Data cleanup: {count_to_delete} oude metingen verwijderd (ouder dan {DATA_RETENTION_DAYS} dagen)")
        
        conn.close()
    except Exception as e:
        print(f"Waarschuwing: Data cleanup gefaald: {e}")

init_database()

# Modbus configuratie uit environment met validatie
try:
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
    
    # Valideer configuratie
    if MODBUS_SLAVE_ID < 1 or MODBUS_SLAVE_ID > 247:
        raise ValueError(f"MODBUS_SLAVE_ID moet tussen 1-247 zijn, kreeg: {MODBUS_SLAVE_ID}")
    if MODBUS_BAUDRATE not in [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]:
        print(f"Waarschuwing: Ongebruikelijke baudrate: {MODBUS_BAUDRATE}")
    if MODBUS_PARITY not in ['N', 'E', 'O']:
        raise ValueError(f"MODBUS_PARITY moet N, E of O zijn, kreeg: {MODBUS_PARITY}")
    if MODBUS_TIMEOUT < 0:
        raise ValueError(f"MODBUS_TIMEOUT moet positief zijn, kreeg: {MODBUS_TIMEOUT}")
except ValueError as e:
    print(f"FOUT in .env configuratie: {e}")
    raise

# Configuratie van Modbus RTU apparaat
# Mapping voor parity settings
PARITY_MAP = {
    'N': minimalmodbus.serial.PARITY_NONE,
    'E': minimalmodbus.serial.PARITY_EVEN,
    'O': minimalmodbus.serial.PARITY_ODD
}

instrument = minimalmodbus.Instrument(MODBUS_PORT, MODBUS_SLAVE_ID)
instrument.serial.baudrate = MODBUS_BAUDRATE
instrument.serial.bytesize = MODBUS_BYTESIZE
instrument.serial.parity = PARITY_MAP.get(MODBUS_PARITY, minimalmodbus.serial.PARITY_NONE)
instrument.serial.stopbits = MODBUS_STOPBITS
instrument.serial.timeout = MODBUS_TIMEOUT

def read_modbus_data():
    """Thread functie om Modbus data te lezen en op te slaan"""
    last_cleanup = datetime.now()
    
    while True:
        try:
            # Voer cleanup uit elke 24 uur
            if DATA_RETENTION_DAYS > 0 and (datetime.now() - last_cleanup).total_seconds() >= 86400:
                cleanup_old_data()
                last_cleanup = datetime.now()
            
            register_temp = instrument.read_register(MODBUS_REGISTER_TEMP, 0, MODBUS_FUNCTION_CODE)
            register_humidity = instrument.read_register(MODBUS_REGISTER_HUMIDITY, 0, MODBUS_FUNCTION_CODE)
            
            temperature = register_temp / 10
            humidity = register_humidity / 10
            
            # Valideer sensor data
            if not (-50 <= temperature <= 100):
                print(f"Waarschuwing: Ongeldige temperatuur {temperature}°C - meting overgeslagen")
                time.sleep(1)
                continue
            
            if not (0 <= humidity <= 100):
                print(f"Waarschuwing: Ongeldige luchtvochtigheid {humidity}% - meting overgeslagen")
                time.sleep(1)
                continue
            
            # Bereken dauwpunt
            dewpoint = temperature - ((100 - humidity) / 5.0)
            
            # Bereken absolute vochtigheid (g/m³)
            # Formule: AH = (6.112 × e^((17.67 × T)/(T+243.5)) × RH × 2.1674) / (273.15+T)
            absolute_humidity = (6.112 * math.exp((17.67 * temperature) / (temperature + 243.5)) * humidity * 2.1674) / (273.15 + temperature)
            
            # Bereken Humidex
            # Formule: Humidex = T + 0.5555 × (e - 10)
            # waarbij e = 6.11 × e^(5417.7530 × (1/273.16 - 1/(273.15+Td)))
            # en Td = dauwpunt in Kelvin
            dewpoint_kelvin = dewpoint + 273.15
            e = 6.11 * math.exp(5417.7530 * ((1/273.16) - (1/dewpoint_kelvin)))
            humidex = temperature + 0.5555 * (e - 10)
            
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

def create_psychrometric_chart(current_temp, current_rh, lang='nl'):
    """Genereer een psychrometrisch (Mollier) diagram met huidige conditie"""
    t = TRANSLATIONS[lang]
    
    # Temperatuur range voor het diagram (0-40°C)
    temp_range = np.linspace(0, 40, 200)
    
    # Creëer figure
    fig = go.Figure()
    
    # Teken verzadigingslijn (100% RH)
    sat_humidity_ratio = []
    for temp in temp_range:
        # Verzadigde dampdrukverzadiging (Pa) - August-Roche-Magnus formule
        pws = 611.2 * np.exp(17.62 * temp / (243.12 + temp))
        # Vochtigheidsratio bij verzadiging (kg water / kg dry air)
        ws = 0.622 * pws / (101325 - pws)
        sat_humidity_ratio.append(ws * 1000)  # Converteer naar g/kg
    
    fig.add_trace(go.Scatter(
        x=temp_range,
        y=sat_humidity_ratio,
        mode='lines',
        name='100% RH',
        line=dict(color='#3498db', width=3),
        showlegend=True
    ))
    
    # Teken RH lijnen (10%, 20%, ..., 90%)
    rh_levels = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    colors = ['#ecf0f1', '#d5dbdb', '#bdc3c7', '#95a5a6', '#7f8c8d', '#5d6d7e', '#34495e', '#2c3e50', '#1c2833']
    
    for rh, color in zip(rh_levels, colors):
        humidity_ratio = []
        for temp in temp_range:
            pws = 611.2 * np.exp(17.62 * temp / (243.12 + temp))
            pw = pws * (rh / 100.0)
            if pw >= 101325:  # Voorkom onmogelijke waarden
                humidity_ratio.append(None)
            else:
                w = 0.622 * pw / (101325 - pw)
                humidity_ratio.append(w * 1000)
        
        fig.add_trace(go.Scatter(
            x=temp_range,
            y=humidity_ratio,
            mode='lines',
            name=f'{rh}% RH',
            line=dict(color=color, width=1, dash='dash'),
            showlegend=False,
            hovertemplate=f'{rh}% RH<br>T: %{{x:.1f}}°C<br>ω: %{{y:.1f}} g/kg<extra></extra>'
        ))
    
    # Comfortzone (typisch 20-26°C en 30-60% RH)
    comfort_temp_range = np.linspace(20, 26, 50)
    
    # Ondergrens comfortzone (30% RH)
    comfort_lower = []
    for temp in comfort_temp_range:
        pws = 611.2 * np.exp(17.62 * temp / (243.12 + temp))
        pw = pws * 0.30
        w = 0.622 * pw / (101325 - pw)
        comfort_lower.append(w * 1000)
    
    # Bovengrens comfortzone (60% RH)
    comfort_upper = []
    for temp in comfort_temp_range:
        pws = 611.2 * np.exp(17.62 * temp / (243.12 + temp))
        pw = pws * 0.60
        w = 0.622 * pw / (101325 - pw)
        comfort_upper.append(w * 1000)
    
    # Vul comfortzone
    fig.add_trace(go.Scatter(
        x=list(comfort_temp_range) + list(comfort_temp_range[::-1]),
        y=comfort_lower + comfort_upper[::-1],
        fill='toself',
        fillcolor='rgba(46, 204, 113, 0.2)',
        line=dict(width=0),
        name=t['comfort_zone'],
        showlegend=True,
        hoverinfo='skip'
    ))
    
    # Bereken huidige vochtigheidsratio
    if current_temp is not None and current_rh is not None:
        pws_current = 611.2 * np.exp(17.62 * current_temp / (243.12 + current_temp))
        pw_current = pws_current * (current_rh / 100.0)
        w_current = 0.622 * pw_current / (101325 - pw_current)
        w_current_g_kg = w_current * 1000
        
        # Markeer huidige conditie
        fig.add_trace(go.Scatter(
            x=[current_temp],
            y=[w_current_g_kg],
            mode='markers+text',
            name=t['current_condition'],
            marker=dict(
                size=15,
                color='#e74c3c',
                symbol='star',
                line=dict(width=2, color='white')
            ),
            text=[f"{current_temp:.1f}°C<br>{current_rh:.0f}%"],
            textposition='top center',
            textfont=dict(size=12, color='#e74c3c', family='Arial Black'),
            showlegend=True,
            hovertemplate=f'{t["current_condition"]}<br>T: {current_temp:.1f}°C<br>RH: {current_rh:.0f}%<br>ω: {w_current_g_kg:.1f} g/kg<extra></extra>'
        ))
    
    # Layout
    fig.update_layout(
        title={
            'text': f"📊 {t['psychrometric_chart']}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50', 'family': 'Arial Black'}
        },
        xaxis_title=t['dry_bulb_temp'],
        yaxis_title='Vochtigheidsratio ω (g water / kg droge lucht)',
        xaxis=dict(
            range=[0, 40],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            dtick=5
        ),
        yaxis=dict(
            range=[0, 25],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            dtick=5
        ),
        height=600,
        plot_bgcolor='rgba(255,255,255,1)',
        paper_bgcolor='white',
        hovermode='closest',
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#2c3e50',
            borderwidth=1
        )
    )
    
    return fig

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
     Output('time-range-dropdown', 'options'),
     Output('label-psychrometric-chart', 'children'),
     Output('label-time-position', 'children')],
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
        dropdown_options,
        f"📐 {t['psychrometric_chart']}",
        t['time_position']
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
     Output('comfort-icon', 'children'),
     Output('graph-relayout-data', 'data')],
    [Input('graph-update', 'n_intervals'),
     Input('time-range-dropdown', 'value'),
     Input('live-graph', 'relayoutData')],
    [State('selected-language', 'data'),
     State('graph-relayout-data', 'data')]
)
def update_graph(n, time_range_minutes, relayout_data, lang, stored_relayout):
    """Update grafieken en metingen op basis van tijdsbereik"""
    if lang is None:
        lang = 'nl'
    
    t = TRANSLATIONS[lang]
    
    def get_comfort_level(temp, humidity):
        """Bepaal comfort level op basis van Humidex"""
        # Bereken Humidex
        # Eerst dauwpunt berekenen
        dewpoint = temp - ((100 - humidity) / 5.0)
        dewpoint_kelvin = dewpoint + 273.15
        
        # Dampdrukverzadiging bij dauwpunt
        e = 6.11 * math.exp(5417.7530 * ((1/273.16) - (1/dewpoint_kelvin)))
        
        # Humidex formule
        humidex = temp + 0.5555 * (e - 10)
        
        # Comfort classificatie op basis van Humidex ranges
        # Bron: Environment Canada Humidex schaal
        if humidex < 20:
            return t['comfort_0'], 0, "🥶", humidex  # Te koud
        elif humidex < 27:
            return t['comfort_4'], 4, "🙂", humidex  # Comfortabel koel
        elif humidex < 30:
            return t['comfort_5'], 5, "😊", humidex  # Comfortabel
        elif humidex < 35:
            return t['comfort_6'], 6, "✨", humidex  # Optimaal comfortabel
        elif humidex < 40:
            return t['comfort_3'], 3, "😓", humidex  # Enig ongemak
        elif humidex < 46:
            return t['comfort_2'], 2, "😟", humidex  # Veel ongemak, vermijd fysieke inspanning
        elif humidex < 54:
            return t['comfort_1'], 1, "🔥", humidex  # Gevaarlijk - hittekrampen mogelijk
        else:
            return t['comfort_0'], 0, "⚠️", humidex  # Heatstroke dreigend
    
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
    
    # Update stored relayout data als er nieuwe zoom/pan data is
    if relayout_data and isinstance(relayout_data, dict) and any(key.startswith(('xaxis', 'yaxis')) for key in relayout_data.keys()):
        stored_relayout = relayout_data
    
    if df.empty:
        return go.Figure(), f"{total_count} {t['measurements']}", "-- °C", "-- %", "-- °C", "-- g/m³", t['no_data'], "--", "❓", stored_relayout
    
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
    except Exception:
        # Fallback voor andere timestamp formaten
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
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
        # Correcte formule voor absolute vochtigheid
        abs_hum_data = (6.112 * df['temperature'].apply(lambda temp: math.exp((17.67 * temp) / (temp + 243.5))) * df['humidity'] * 2.1674) / (273.15 + df['temperature'])
    
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
    
    # Bereken dynamische Y-axis ranges met padding
    temp_min, temp_max = df['temperature'].min(), df['temperature'].max()
    temp_range = [max(0, temp_min - 5), temp_max + 5]
    
    hum_range = [0, 100]  # Humidity blijft altijd 0-100%
    
    dewpoint_data = df['dewpoint'] if 'dewpoint' in df.columns else df['temperature'] - ((100 - df['humidity']) / 5.0)
    dew_min, dew_max = dewpoint_data.min(), dewpoint_data.max()
    dew_range = [max(0, dew_min - 5), dew_max + 5]
    
    abs_min, abs_max = abs_hum_data.min(), abs_hum_data.max()
    abs_range = [max(0, abs_min - 2), abs_max + 2]
    
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
        range=temp_range
    )
    fig.update_yaxes(
        title_text=f"{t['humidity']} (%)", 
        row=2, col=1,
        showgrid=True,
        gridcolor='rgba(0,0,0,0.05)',
        range=hum_range
    )
    fig.update_yaxes(
        title_text=f"{t['dewpoint']} (°C)", 
        row=3, col=1,
        showgrid=True,
        gridcolor='rgba(0,0,0,0.05)',
        range=dew_range
    )
    fig.update_yaxes(
        title_text=f"{t['abs_humidity']} (g/m³)", 
        row=4, col=1,
        showgrid=True,
        gridcolor='rgba(0,0,0,0.05)',
        range=abs_range
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
        ),
        uirevision='constant'  # Behoud UI state (zoom/pan) tussen updates
    )
    
    # Bepaal comfort level (retourneert nu ook humidex)
    comfort_text, comfort_score, comfort_icon, humidex = get_comfort_level(latest_temp, latest_humidity)
    
    return fig, f"📊 {total_count} {t['measurements']}", f"{latest_temp:.1f} °C", f"{latest_humidity:.1f} %", f"{latest_dewpoint:.1f} °C", f"{latest_abs_humidity:.1f} g/m³", comfort_text, str(comfort_score), comfort_icon, stored_relayout

# Callback voor psychrometric chart
@app.callback(
    Output('psychrometric-chart', 'figure'),
    [Input('graph-update', 'n_intervals')],
    [State('selected-language', 'data')]
)
def update_psychrometric_chart(n, lang):
    """Update psychrometrisch diagram met actuele meetwaarden"""
    if lang is None:
        lang = 'nl'
    
    # Haal laatste meting op uit database
    try:
        conn = sqlite3.connect(DB_FILE)
        query = 'SELECT temperature, humidity FROM measurements ORDER BY timestamp DESC LIMIT 1'
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            current_temp = df['temperature'].iloc[0]
            current_rh = df['humidity'].iloc[0]
            return create_psychrometric_chart(current_temp, current_rh, lang)
        else:
            # Geen data beschikbaar - toon leeg diagram
            return create_psychrometric_chart(None, None, lang)
    except Exception as e:
        print(f"Fout bij updaten psychrometric chart: {e}")
        return create_psychrometric_chart(None, None, lang)

# Callback voor modal open/close
@app.callback(
    Output('range-modal', 'style'),
    [Input('open-range-modal-btn', 'n_clicks'),
     Input('close-range-modal-btn', 'n_clicks'),
     Input('apply-custom-range-btn', 'n_clicks')],
    [State('range-modal', 'style')],
    prevent_initial_call=True
)
def toggle_modal(open_clicks, close_clicks, apply_clicks, current_style):
    """Toggle modal visibility"""
    ctx = callback_context
    if not ctx.triggered:
        return current_style
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'open-range-modal-btn':
        return {
            'display': 'block',
            'position': 'fixed',
            'zIndex': '1000',
            'left': '0',
            'top': '0',
            'width': '100%',
            'height': '100%',
            'background': 'rgba(0,0,0,0.5)',
            'overflow': 'auto'
        }
    else:  # close of apply
        return {'display': 'none'}

# Callback voor preset buttons en custom range - sluit ook modal
@app.callback(
    [Output('selected-range-value', 'data'),
     Output('range-modal', 'style', allow_duplicate=True)],
    [Input('preset-5min', 'n_clicks'),
     Input('preset-10min', 'n_clicks'),
     Input('preset-30min', 'n_clicks'),
     Input('preset-1hour', 'n_clicks'),
     Input('preset-2hours', 'n_clicks'),
     Input('preset-6hours', 'n_clicks'),
     Input('preset-12hours', 'n_clicks'),
     Input('preset-24hours', 'n_clicks'),
     Input('preset-2days', 'n_clicks'),
     Input('preset-week', 'n_clicks'),
     Input('preset-month', 'n_clicks'),
     Input('apply-custom-range-btn', 'n_clicks')],
    [State('custom-start-date', 'date'),
     State('custom-start-hour', 'value'),
     State('custom-start-minute', 'value'),
     State('custom-end-date', 'date'),
     State('custom-end-hour', 'value'),
     State('custom-end-minute', 'value')],
    prevent_initial_call=True
)
def handle_range_selection(btn5, btn10, btn30, btn1h, btn2h, btn6h, btn12h, btn24h, btn2d, btnw, btnm, btncustom,
                           start_date, start_hour, start_minute, end_date, end_hour, end_minute):
    """Handle preset button clicks en custom range"""
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Modal style om te sluiten
    modal_closed = {'display': 'none'}
    
    # Preset button mapping
    preset_map = {
        'preset-5min': 5,
        'preset-10min': 10,
        'preset-30min': 30,
        'preset-1hour': 60,
        'preset-2hours': 120,
        'preset-6hours': 360,
        'preset-12hours': 720,
        'preset-24hours': 1440,
        'preset-2days': 2880,
        'preset-week': 10080,
        'preset-month': 43200
    }
    
    if button_id in preset_map:
        return {'type': 'preset', 'minutes': preset_map[button_id]}, modal_closed
    
    elif button_id == 'apply-custom-range-btn':
        if start_date and end_date:
            # Valideer tijden
            start_hour = start_hour if start_hour is not None else 0
            start_minute = start_minute if start_minute is not None else 0
            end_hour = end_hour if end_hour is not None else 23
            end_minute = end_minute if end_minute is not None else 59
            
            return {
                'type': 'custom',
                'start_date': start_date,
                'start_hour': start_hour,
                'start_minute': start_minute,
                'end_date': end_date,
                'end_hour': end_hour,
                'end_minute': end_minute
            }, modal_closed
    
    return no_update, no_update

# Callback voor ophalen historische data bij range selectie
@app.callback(
    [Output('historical-data-store', 'data'),
     Output('historical-time-slider', 'min'),
     Output('historical-time-slider', 'max'),
     Output('historical-time-slider', 'value'),
     Output('historical-time-slider', 'marks'),
     Output('slider-container', 'style')],
    [Input('selected-range-value', 'data')],
    [State('selected-language', 'data')]
)
def load_historical_data(range_value, lang):
    """Laad historische data voor geselecteerde periode (preset of custom)"""
    if lang is None:
        lang = 'nl'
    
    t = TRANSLATIONS[lang]
    
    # Als geen range geselecteerd, verberg slider
    if range_value is None:
        return None, 0, 100, 0, {}, {'display': 'none'}
    
    try:
        # Bepaal start en eind tijden op basis van type
        if range_value.get('type') == 'preset':
            # Preset: gebruik minuten
            minutes = range_value['minutes']
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(minutes=minutes)
        
        elif range_value.get('type') == 'custom':
            # Custom: gebruik specifieke datums en tijden
            start_date = pd.to_datetime(range_value['start_date'])
            start_dt = start_date.replace(
                hour=range_value['start_hour'],
                minute=range_value['start_minute'],
                second=0
            )
            
            end_date = pd.to_datetime(range_value['end_date'])
            end_dt = end_date.replace(
                hour=range_value['end_hour'],
                minute=range_value['end_minute'],
                second=59
            )
        else:
            return None, 0, 100, 0, {}, {'display': 'none'}
        
        # Haal data op uit database
        conn = sqlite3.connect(DB_FILE)
        query = '''
            SELECT timestamp, temperature, humidity 
            FROM measurements 
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
        '''
        df = pd.read_sql_query(query, conn, params=(start_dt.isoformat(), end_dt.isoformat()))
        conn.close()
        
        if df.empty:
            return None, 0, 100, 0, {}, {'display': 'none'}
        
        # Converteer timestamp kolom
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Bepaal tijdsverschil in minuten
        time_diff_minutes = (end_dt - start_dt).total_seconds() / 60
        
        # Als range > 1 minuut, sample per minuut (anders per seconde)
        if time_diff_minutes > 1:
            # Resample naar 1 minuut intervals (gebruik mean voor aggregatie)
            df = df.set_index('timestamp').resample('1min').mean().reset_index()
            df = df.dropna()  # Verwijder lege minuten
        
        if df.empty:
            return None, 0, 100, 0, {}, {'display': 'none'}
        
        n_points = len(df)
        
        # Maak slider marks met intelligente tijd labels
        if time_diff_minutes <= 60:  # <= 1 uur: toon HH:MM
            label_format = '%H:%M'
            mark_count = min(10, n_points)
        elif time_diff_minutes <= 1440:  # <= 1 dag: toon HH:MM
            label_format = '%H:%M'
            mark_count = min(12, n_points)
        elif time_diff_minutes <= 10080:  # <= 1 week: toon DD-MM HH:MM
            label_format = '%d-%m %H:%M'
            mark_count = min(10, n_points)
        else:  # > 1 week: toon DD-MM
            label_format = '%d-%m'
            mark_count = min(10, n_points)
        
        # Bereken mark indices
        if n_points <= mark_count:
            mark_indices = list(range(n_points))
        else:
            mark_indices = [int(i * (n_points - 1) / (mark_count - 1)) for i in range(mark_count)]
        
        marks = {}
        for idx in mark_indices:
            if idx < n_points:
                marks[idx] = df['timestamp'].iloc[idx].strftime(label_format)
        
        # Sla data op in store (converteer naar dict voor JSON serialization)
        data_dict = {
            'timestamps': df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'temperatures': df['temperature'].tolist(),
            'humidities': df['humidity'].tolist(),
            'sampling_mode': 'minute' if time_diff_minutes > 1 else 'second'
        }
        
        return data_dict, 0, n_points - 1, 0, marks, {'display': 'block'}
        
    except Exception as e:
        print(f"Fout bij laden historische data: {e}")
        return None, 0, 100, 0, {}, {'display': 'none'}

# Callback voor het updaten van timestamp display en psychrometric chart bij slider beweging
@app.callback(
    [Output('slider-timestamp-display', 'children'),
     Output('psychrometric-chart', 'figure', allow_duplicate=True)],
    [Input('historical-time-slider', 'value'),
     Input('historical-time-slider', 'drag_value')],
    [State('historical-data-store', 'data'),
     State('selected-language', 'data')],
    prevent_initial_call=True
)
def update_historical_view(slider_value, drag_value, stored_data, lang):
    """Update psychrometric chart met historische data punt - live tijdens slepen"""
    # Gebruik drag_value tijdens het slepen, anders value
    current_value = drag_value if drag_value is not None else slider_value
    if lang is None:
        lang = 'nl'
    
    t = TRANSLATIONS[lang]
    
    # Check of er data is
    if stored_data is None or current_value is None:
        return t['no_data_in_range'], create_psychrometric_chart(None, None, lang)
    
    try:
        # Haal data op uit store
        timestamps = stored_data['timestamps']
        temperatures = stored_data['temperatures']
        humidities = stored_data['humidities']
        
        # Valideer slider waarde
        if current_value < 0 or current_value >= len(timestamps):
            return t['no_data_in_range'], create_psychrometric_chart(None, None, lang)
        
        # Haal geselecteerd datapunt op
        selected_timestamp = timestamps[current_value]
        selected_temp = temperatures[current_value]
        selected_humidity = humidities[current_value]
        
        # Format timestamp voor display
        dt = pd.to_datetime(selected_timestamp)
        timestamp_display = f"📅 {dt.strftime('%d-%m-%Y %H:%M:%S')}"
        
        # Creëer aangepast psychrometric chart met historisch punt
        fig = create_psychrometric_chart_historical(selected_temp, selected_humidity, lang, t['historical_condition'])
        
        return timestamp_display, fig
        
    except Exception as e:
        print(f"Fout bij updaten historische view: {e}")
        return t['no_data_in_range'], create_psychrometric_chart(None, None, lang)

def create_psychrometric_chart_historical(current_temp, current_rh, lang='nl', label='Historische toestand'):
    """Genereer psychrometrisch diagram met aangepaste label voor historisch punt"""
    t = TRANSLATIONS[lang]
    
    # Temperatuur range voor het diagram (0-40°C)
    temp_range = np.linspace(0, 40, 200)
    
    # Creëer figure
    fig = go.Figure()
    
    # Teken verzadigingslijn (100% RH)
    sat_humidity_ratio = []
    for temp in temp_range:
        pws = 611.2 * np.exp(17.62 * temp / (243.12 + temp))
        ws = 0.622 * pws / (101325 - pws)
        sat_humidity_ratio.append(ws * 1000)
    
    fig.add_trace(go.Scatter(
        x=temp_range,
        y=sat_humidity_ratio,
        mode='lines',
        name='100% RH',
        line=dict(color='#3498db', width=3),
        showlegend=True
    ))
    
    # Teken RH lijnen (10%, 20%, ..., 90%)
    rh_levels = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    colors = ['#ecf0f1', '#d5dbdb', '#bdc3c7', '#95a5a6', '#7f8c8d', '#5d6d7e', '#34495e', '#2c3e50', '#1c2833']
    
    for rh, color in zip(rh_levels, colors):
        humidity_ratio = []
        for temp in temp_range:
            pws = 611.2 * np.exp(17.62 * temp / (243.12 + temp))
            pw = pws * (rh / 100.0)
            if pw >= 101325:
                humidity_ratio.append(None)
            else:
                w = 0.622 * pw / (101325 - pw)
                humidity_ratio.append(w * 1000)
        
        fig.add_trace(go.Scatter(
            x=temp_range,
            y=humidity_ratio,
            mode='lines',
            name=f'{rh}% RH',
            line=dict(color=color, width=1, dash='dash'),
            showlegend=False,
            hovertemplate=f'{rh}% RH<br>T: %{{x:.1f}}°C<br>ω: %{{y:.1f}} g/kg<extra></extra>'
        ))
    
    # Comfortzone (typisch 20-26°C en 30-60% RH)
    comfort_temp_range = np.linspace(20, 26, 50)
    
    comfort_lower = []
    for temp in comfort_temp_range:
        pws = 611.2 * np.exp(17.62 * temp / (243.12 + temp))
        pw = pws * 0.30
        w = 0.622 * pw / (101325 - pw)
        comfort_lower.append(w * 1000)
    
    comfort_upper = []
    for temp in comfort_temp_range:
        pws = 611.2 * np.exp(17.62 * temp / (243.12 + temp))
        pw = pws * 0.60
        w = 0.622 * pw / (101325 - pw)
        comfort_upper.append(w * 1000)
    
    fig.add_trace(go.Scatter(
        x=list(comfort_temp_range) + list(comfort_temp_range[::-1]),
        y=comfort_lower + comfort_upper[::-1],
        fill='toself',
        fillcolor='rgba(46, 204, 113, 0.2)',
        line=dict(width=0),
        name=t['comfort_zone'],
        showlegend=True,
        hoverinfo='skip'
    ))
    
    # Bereken en markeer punt
    if current_temp is not None and current_rh is not None:
        pws_current = 611.2 * np.exp(17.62 * current_temp / (243.12 + current_temp))
        pw_current = pws_current * (current_rh / 100.0)
        w_current = 0.622 * pw_current / (101325 - pw_current)
        w_current_g_kg = w_current * 1000
        
        fig.add_trace(go.Scatter(
            x=[current_temp],
            y=[w_current_g_kg],
            mode='markers+text',
            name=label,
            marker=dict(
                size=15,
                color='#e74c3c',
                symbol='star',
                line=dict(width=2, color='white')
            ),
            text=[f"{current_temp:.1f}°C<br>{current_rh:.0f}%"],
            textposition='top center',
            textfont=dict(size=12, color='#e74c3c', family='Arial Black'),
            showlegend=True,
            hovertemplate=f'{label}<br>T: {current_temp:.1f}°C<br>RH: {current_rh:.0f}%<br>ω: {w_current_g_kg:.1f} g/kg<extra></extra>'
        ))
    
    # Layout
    fig.update_layout(
        title={
            'text': f"📊 {t['psychrometric_chart']}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50', 'family': 'Arial Black'}
        },
        xaxis_title=t['dry_bulb_temp'],
        yaxis_title='Vochtigheidsratio ω (g water / kg droge lucht)',
        xaxis=dict(
            range=[0, 40],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            dtick=5
        ),
        yaxis=dict(
            range=[0, 25],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            dtick=5
        ),
        height=600,
        plot_bgcolor='rgba(255,255,255,1)',
        paper_bgcolor='white',
        hovermode='closest',
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#2c3e50',
            borderwidth=1
        )
    )
    
    return fig

if __name__ == '__main__':
    # Applicatie configuratie uit environment
    APP_HOST = os.getenv('APP_HOST', '127.0.0.1')
    APP_PORT = int(os.getenv('APP_PORT', '8050'))
    APP_DEBUG = os.getenv('APP_DEBUG', 'False').lower() == 'true'
    
    # Valideer poort
    if not (1 <= APP_PORT <= 65535):
        print(f"FOUT: APP_PORT moet tussen 1-65535 zijn, kreeg: {APP_PORT}")
        print("Gebruik default poort 8050")
        APP_PORT = 8050
    
    print(f"Dashboard gestart op http://{APP_HOST}:{APP_PORT}/")
    app.run(debug=APP_DEBUG, host=APP_HOST, port=APP_PORT)
