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
                html.H1("Bienvenido al Dashboard Deportivo", className="text-center mb-4"),
                html.P("Sistema de análisis y visualización de datos deportivos", 
                       className="text-center text-muted mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Dashboard de Performance", className="card-title"),
                                html.P("Análisis de rendimiento deportivo y métricas competitivas"),
                                dbc.Button("Acceder", color="primary", href="/performance")
                            ])
                        ])
                    ], md=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H4("Dashboard Administrativo", className="card-title"),
                                html.P("Análisis de contratos y gestión financiera de jugadores"),
                                dbc.Button("Acceder", color="success", href="/administrativo")
                            ])
                        ])
                    ], md=6)
                ])
            ])
        ])
    ], fluid=True, className="main-container fade-in")
])