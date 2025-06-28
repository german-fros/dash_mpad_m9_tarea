from dash import html
import dash_bootstrap_components as dbc
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.navbar import create_navbar

layout = html.Div([
    create_navbar(),
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Dashboard GPS", className="mb-4"),
                html.P("Análisis de datos de tracking y movimiento GPS"),
                
                # Placeholder para gráficos
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Análisis de Movimiento GPS"),
                        html.P("Aquí irán los gráficos de tracking GPS y métricas de movimiento")
                    ])
                ])
            ])
        ])
    ], fluid=True, className="main-container fade-in")
])