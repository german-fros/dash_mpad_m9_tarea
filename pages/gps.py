from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Dashboard de Performance", className="mb-4"),
            html.P("Análisis de rendimiento deportivo y métricas competitivas"),
            
            # Placeholder para gráficos
            dbc.Card([
                dbc.CardBody([
                    html.H4("Gráficos de Performance"),
                    html.P("Aquí irán los gráficos interactivos de rendimiento")
                ])
            ])
        ])
    ])
], fluid=True)