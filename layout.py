# layout.py
# HTML Layout en styling voor de Modbus Climate Monitor applicatie

from dash import dcc, html
from translations import LANGUAGE_NAMES

# Custom HTML template met CSS
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .tooltip-container {
                position: relative;
                cursor: help;
            }
            .tooltip-container .tooltip-text {
                visibility: hidden;
                width: 280px;
                background-color: #2c3e50;
                color: #fff;
                text-align: left;
                border-radius: 8px;
                padding: 12px;
                position: absolute;
                z-index: 1000;
                top: 110%;
                left: 50%;
                margin-left: -140px;
                opacity: 0;
                transition: opacity 0.3s;
                font-size: 13px;
                line-height: 1.6;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            .tooltip-container .tooltip-text::after {
                content: "";
                position: absolute;
                bottom: 100%;
                left: 50%;
                margin-left: -8px;
                border-width: 8px;
                border-style: solid;
                border-color: transparent transparent #2c3e50 transparent;
            }
            .tooltip-container:hover .tooltip-text {
                visibility: visible;
                opacity: 1;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

def create_layout():
    """Creëert de hoofdlayout van de applicatie"""
    return html.Div([
        # Store voor geselecteerde taal
        dcc.Store(id='selected-language', data='nl'),
        
        # Header met taalkeuze
        html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='language-selector',
                        options=[{'label': LANGUAGE_NAMES[lang], 'value': lang} for lang in LANGUAGE_NAMES.keys()],
                        value='nl',
                        clearable=False,
                        style={
                            'width': '80px',
                            'fontSize': '14px',
                            'fontWeight': 'bold'
                        }
                    )
                ], style={'display': 'inline-block', 'width': '10%', 'textAlign': 'left', 'verticalAlign': 'middle'}),
                html.H1(id='page-title', children='🌡️ Modbus Klimaat Monitor', style={
                    'textAlign': 'center',
                    'color': '#2c3e50',
                    'marginBottom': '0px',
                    'fontFamily': 'Arial, sans-serif',
                    'display': 'inline-block',
                    'width': '90%'
                })
            ])
        ], style={
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'padding': '20px',
            'borderRadius': '10px',
            'marginBottom': '20px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }),
        
        # Huidige waarden - alle 5 cards in een rij
        html.Div([
            # Temperatuur
            html.Div([
                html.Div([
                    html.Div("🌡️", style={'fontSize': '35px', 'marginBottom': '8px'}),
                    html.Div(id='label-temperature', children="Temperatuur", style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '5px'}),
                    html.Div(id='current-temp', style={
                        'fontSize': '28px',
                        'fontWeight': 'bold',
                        'color': '#3498db'
                    })
                ], style={
                    'background': 'white',
                    'padding': '20px',
                    'borderRadius': '15px',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                    'textAlign': 'center',
                    'border': '2px solid #3498db',
                    'height': '140px'
                })
            ], style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),
            
            # Luchtvochtigheid
            html.Div([
                html.Div([
                    html.Div("💧", style={'fontSize': '35px', 'marginBottom': '8px'}),
                    html.Div(id='label-humidity', children="Luchtvochtigheid", style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '5px'}),
                    html.Div(id='current-humidity', style={
                        'fontSize': '28px',
                        'fontWeight': 'bold',
                        'color': '#e74c3c'
                    })
                ], style={
                    'background': 'white',
                    'padding': '20px',
                    'borderRadius': '15px',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                    'textAlign': 'center',
                    'border': '2px solid #e74c3c',
                    'height': '140px'
                })
            ], style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),
            
            # Dauwpunt
            html.Div([
                html.Div([
                    html.Div("💦", style={'fontSize': '35px', 'marginBottom': '8px'}),
                    html.Div(id='label-dewpoint', children="Dauwpunt", style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '5px'}),
                    html.Div(id='current-dewpoint', style={
                        'fontSize': '28px',
                        'fontWeight': 'bold',
                        'color': '#9b59b6'
                    })
                ], style={
                    'background': 'white',
                    'padding': '20px',
                    'borderRadius': '15px',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                    'textAlign': 'center',
                    'border': '2px solid #9b59b6',
                    'height': '140px'
                })
            ], style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),
            
            # Absolute Vochtigheid
            html.Div([
                html.Div([
                    html.Div("🌫️", style={'fontSize': '35px', 'marginBottom': '8px'}),
                    html.Div(id='label-abs-humidity', children="Abs. Vochtigheid", style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '5px'}),
                    html.Div(id='current-abs-humidity', style={
                        'fontSize': '28px',
                        'fontWeight': 'bold',
                        'color': '#16a085'
                    })
                ], style={
                    'background': 'white',
                    'padding': '20px',
                    'borderRadius': '15px',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                    'textAlign': 'center',
                    'border': '2px solid #16a085',
                    'height': '140px'
                })
            ], style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),
            
            # Behagelijkheid
            html.Div([
                html.Div([
                    html.Div("☀️", id='comfort-icon', style={'fontSize': '35px', 'marginBottom': '8px'}),
                    html.Div(id='label-comfort', children="Behagelijkheid", style={'fontSize': '14px', 'color': '#7f8c8d', 'marginBottom': '5px'}),
                    html.Div(id='comfort-level', style={
                        'fontSize': '14px',
                        'fontWeight': 'bold',
                        'color': '#2c3e50',
                        'lineHeight': '1.2',
                        'marginBottom': '5px'
                    }),
                    html.Div([
                        html.Span(id='label-score', children="Score: ", style={'fontSize': '14px', 'color': '#7f8c8d'}),
                        html.Span(id='comfort-score', style={'fontSize': '20px', 'fontWeight': 'bold', 'color': '#2c3e50'})
                    ]),
                    html.Div(id='tooltip-content', children=[], className='tooltip-text')
                ], className='tooltip-container', style={
                    'background': 'white',
                    'padding': '20px',
                    'borderRadius': '15px',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                    'textAlign': 'center',
                    'border': '2px solid #f39c12',
                    'height': '140px',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'justifyContent': 'center',
                    'position': 'relative'
                })
            ], style={'width': '19%', 'display': 'inline-block', 'verticalAlign': 'top'})
        ], style={'marginBottom': '30px'}),
        
        # Grafiek
        html.Div([
            dcc.Graph(id='live-graph', style={'borderRadius': '10px'})
        ], style={
            'background': 'white',
            'padding': '20px',
            'borderRadius': '15px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }),
        
        # Update interval
        dcc.Interval(
            id='graph-update',
            interval=1000,
            n_intervals=0
        ),
        
        # Controls
        html.Div([
            html.Div([
                html.Label(id='label-time-period', children="📅 Tijdsperiode:", style={
                    'fontSize': '16px',
                    'fontWeight': 'bold',
                    'color': '#2c3e50',
                    'marginBottom': '10px',
                    'display': 'block'
                }),
                dcc.Dropdown(
                    id='time-range-dropdown',
                    options=[
                        {'label': '⏱️ Laatste 1 minuut', 'value': 1},
                        {'label': '⏱️ Laatste 5 minuten', 'value': 5},
                        {'label': '⏱️ Laatste 15 minuten', 'value': 15},
                        {'label': '⏱️ Laatste 30 minuten', 'value': 30},
                        {'label': '🕐 Laatste 1 uur', 'value': 60},
                        {'label': '🕐 Laatste 6 uur', 'value': 360},
                        {'label': '📆 Laatste 24 uur', 'value': 1440},
                        {'label': '📆 Laatste 7 dagen', 'value': 10080},
                        {'label': '📊 Alle data', 'value': -1}
                    ],
                    value=5,
                    clearable=False,
                    style={'borderRadius': '8px'}
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.Label(id='label-database', children="📊 Database:", style={
                    'fontSize': '16px',
                    'fontWeight': 'bold',
                    'color': '#2c3e50',
                    'marginBottom': '10px',
                    'display': 'block'
                }),
                html.Div(id='data-count', style={
                    'fontSize': '24px',
                    'fontWeight': 'bold',
                    'color': '#27ae60'
                })
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right', 'textAlign': 'right'})
        ], style={
            'marginTop': '30px',
            'padding': '20px',
            'background': 'white',
            'borderRadius': '15px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        })
    ], style={
        'maxWidth': '1400px',
        'margin': '0 auto',
        'padding': '20px',
        'background': '#ecf0f1',
        'fontFamily': 'Arial, sans-serif'
    })
