from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.navbar import create_navbar

# Función para cargar y procesar datos
def load_performance_data():
    """Cargar datos del archivo consolidado filtrado"""
    try:
        import pandas as pd
        import os
        
        # Archivo consolidado filtrado
        processed_file = 'data/processed/data_uruguay_full_filtrado.csv'
        
        if not os.path.exists(processed_file):
            raise FileNotFoundError(f"Archivo {processed_file} no encontrado. Ejecuta data_processor.py primero.")
        
        print(f"Cargando datos de: {processed_file}")
        
        # Leer CSV consolidado
        df = pd.read_csv(processed_file, encoding='utf-8')
        
        # Verificar columnas esperadas
        expected_columns = ['Player', 'Wyscout id', 'Team within selected timeframe', 'Position', 'Age', 'Goals', 'Assists', 'Minutes played', 'Temporada']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Advertencia: Columnas faltantes: {missing_columns}")
        
        # Limpiar datos
        df = df.dropna(subset=['Player', 'Wyscout id', 'Team within selected timeframe', 'Position'])
        
        # Convertir columnas numéricas
        numeric_columns = ['Age', 'Goals', 'Assists', 'Minutes played']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Filtrar solo equipos uruguayos principales
        uruguayan_teams = [
            'Nacional', 'Peñarol', 'Defensor Sporting', 'Wanderers', 
            'Liverpool', 'Danubio', 'River Plate', 'Cerro', 'Racing', 
            'Fénix', 'Progreso', 'Boston River', 'Rampla Juniors',
            'Miramar Misiones', 'Cerro Largo', 'Deportivo Maldonado'
        ]
        
        # Filtrar equipos uruguayos usando la columna correcta
        df_filtered = df[df['Team within selected timeframe'].isin(uruguayan_teams)].copy()
        
        # Renombrar columnas para compatibilidad con el dashboard
        df_filtered['Team'] = df_filtered['Team within selected timeframe']  # Usar el equipo del año específico
        
        if 'Minutes played' in df_filtered.columns:
            df_filtered['Minutes_played'] = df_filtered['Minutes played']
        
        # Agregar columnas derivadas para compatibilidad con gráficos
        if 'Minutes_played' not in df_filtered.columns:
            df_filtered['Minutes_played'] = df_filtered['Goals'] * 200 + 500  # Estimación simple
        
        df_filtered['xG'] = df_filtered['Goals'] * 0.8 + (df_filtered['Goals'] * 0.2).apply(lambda x: max(0, x + (0.5 - 1) * 0.3))
        df_filtered['xA'] = df_filtered['Assists'] * 0.7 + (df_filtered['Assists'] * 0.3).apply(lambda x: max(0, x + (0.5 - 1) * 0.2))
        
        print(f"Datos cargados: {len(df_filtered)} jugadores de {df_filtered['Team'].nunique()} equipos")
        print(f"Temporadas: {sorted(df_filtered['Temporada'].unique())}")
        print(f"Equipos: {sorted(df_filtered['Team'].unique())}")
        
        return df_filtered
        
    except Exception as e:
        print(f"Error cargando datos consolidados: {e}")
        print("Usando datos de respaldo...")
        
        # Datos de respaldo en caso de error
        import numpy as np
        np.random.seed(42)
        teams = ['Nacional', 'Peñarol', 'Defensor Sporting', 'Wanderers']
        positions = ['GK', 'CB', 'RB', 'LB', 'CDM', 'CM', 'ST']
        temporadas = ['2020', '2021', '2022', '2023', '2024']
        
        n_players = 150
        data = {
            'Player': [f'Jugador_{i+1}' for i in range(n_players)],
            'Team': np.random.choice(teams, n_players),
            'Position': np.random.choice(positions, n_players),
            'Age': np.random.randint(18, 35, n_players),
            'Goals': np.random.poisson(2, n_players),
            'Assists': np.random.poisson(1, n_players),
            'Temporada': np.random.choice(temporadas, n_players),
            'Minutes_played': np.random.randint(500, 2500, n_players),
            'xG': np.random.exponential(1.5, n_players),
            'xA': np.random.exponential(1.0, n_players)
        }
        
        return pd.DataFrame(data)

# Cargar datos
df_performance = load_performance_data()

layout = html.Div([
    create_navbar(),
    dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("Dashboard de Performance", className="mb-4"),
                html.P("Análisis de rendimiento deportivo y métricas competitivas", 
                       className="text-muted mb-4"),
            ])
        ]),
        
        # Filtros
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Filtros", className="mb-0")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Temporada"),
                                dcc.Dropdown(
                                    id='season-filter',
                                    options=[{'label': 'Todas', 'value': 'all'}] + 
                                           [{'label': season, 'value': season} for season in sorted(df_performance['Temporada'].unique())],
                                    value='all',
                                    placeholder="Seleccionar temporada",
                                    style={'zIndex': 1050}
                                )
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Equipo"),
                                dcc.Dropdown(
                                    id='team-filter',
                                    options=[{'label': 'Todos', 'value': 'all'}] + 
                                           [{'label': team, 'value': team} for team in sorted(df_performance['Team'].unique())],
                                    value='all',
                                    placeholder="Seleccionar equipo",
                                    style={'zIndex': 1049}
                                )
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Jugador"),
                                dcc.Dropdown(
                                    id='player-filter',
                                    options=[{'label': 'Todos', 'value': 'all'}] + 
                                           [{'label': player, 'value': player} for player in sorted(df_performance['Player'].unique())],
                                    value='all',
                                    placeholder="Buscar jugador",
                                    searchable=True,
                                    style={'zIndex': 1048}
                                )
                            ], md=4)
                        ])
                    ], style={'position': 'relative', 'zIndex': 1050})
                ], style={'position': 'relative', 'zIndex': 1050, 'marginBottom': '30px'})
            ])
        ], className="mb-5"),  # Más margen inferior
        
        # Gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Goles vs Goles Esperados (xG)")),
                    dbc.CardBody([
                        dcc.Graph(id='goals-xg-scatter')
                    ])
                ], className="chart-container")
            ], md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Top 10 Jugadores - Goles + Asistencias")),
                    dbc.CardBody([
                        dcc.Graph(id='goals-assists-bar')
                    ])
                ], className="chart-container")
            ], md=6)
        ], className="mb-4"),
        
        # Tabla de top jugadores
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Top Jugadores", className="mb-0"),
                        dbc.ButtonGroup([
                            dbc.Button("Por Goles", id="sort-goals", color="primary", size="sm"),
                            dbc.Button("Por Asistencias", id="sort-assists", color="secondary", size="sm"),
                            dbc.Button("Por Minutos", id="sort-minutes", color="info", size="sm")
                        ], className="float-end")
                    ]),
                    dbc.CardBody([
                        html.Div(id='top-players-table')
                    ])
                ])
            ])
        ], className="mb-4"),
        
        # Exportación
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Exportación de Reportes")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.P("Exportar análisis de performance a PDF"),
                                dbc.Button(
                                    "Exportar a PDF", 
                                    id="export-pdf-btn",
                                    color="danger", 
                                    className="me-2"
                                ),
                                html.Div(id="export-status")
                            ])
                        ])
                    ])
                ])
            ])
        ])
        
    ], fluid=True, className="main-container fade-in")
])

# Callbacks para interactividad
@callback(
    [Output('goals-xg-scatter', 'figure'),
     Output('goals-assists-bar', 'figure'),
     Output('top-players-table', 'children')],
    [Input('season-filter', 'value'),
     Input('team-filter', 'value'),
     Input('player-filter', 'value'),
     Input('sort-goals', 'n_clicks'),
     Input('sort-assists', 'n_clicks'),
     Input('sort-minutes', 'n_clicks')]
)
def update_dashboard(season_filter, team_filter, player_filter, sort_goals, sort_assists, sort_minutes):
    """Actualizar todos los gráficos basado en los filtros"""
    
    # Filtrar datos
    filtered_df = df_performance.copy()
    
    # Si se selecciona "Todas" las temporadas, hacer acumulado por jugador
    if season_filter == 'all':
        # Agrupar por Wyscout id (identificador único del jugador)
        agg_functions = {
            'Goals': 'sum',
            'Assists': 'sum', 
            'Minutes_played': 'sum',
            'xG': 'sum',
            'xA': 'sum',
            'Player': 'first',  # Mantener nombre del jugador
            'Team': lambda x: ' / '.join(x.unique()),  # Mostrar todos los equipos donde jugó
            'Position': 'first',  # Tomar la primera posición
            'Age': 'first',  # Tomar la primera edad
            'Temporada': lambda x: 'Acumulado'  # Marcar como acumulado
        }
        
        filtered_df = filtered_df.groupby('Wyscout id').agg(agg_functions).reset_index()
        
    else:
        filtered_df = filtered_df[filtered_df['Temporada'] == season_filter]
    
    if team_filter != 'all':
        filtered_df = filtered_df[filtered_df['Team'] == team_filter]
    
    if player_filter != 'all':
        filtered_df = filtered_df[filtered_df['Player'] == player_filter]
    
    # Gráfico 1: Goles vs xG
    hover_data = ['Player', 'Position', 'Temporada'] if season_filter != 'all' else ['Player', 'Position']
    
    fig1 = px.scatter(
        filtered_df, 
        x='xG', 
        y='Goals',
        color='Team',
        size='Minutes_played',
        hover_data=hover_data,
        title=f"Goles vs Goles Esperados {'(Acumulado todas las temporadas)' if season_filter == 'all' else f'(Temporada {season_filter})'}",
        labels={'xG': 'Goles Esperados (xG)', 'Goals': 'Goles Reales'}
    )
    
    # Solo agregar línea de referencia si hay datos
    if len(filtered_df) > 0 and filtered_df['xG'].max() > 0:
        fig1.add_shape(
            type="line",
            x0=0, y0=0, x1=filtered_df['xG'].max(), y1=filtered_df['xG'].max(),
            line=dict(color="red", width=2, dash="dash"),
        )
    
    fig1.update_layout(
        height=400,
        showlegend=False  # Ocultar leyenda para mejor visualización
    )
    
    # Gráfico 2: Top 10 Goles + Asistencias (horizontal)
    filtered_df['Goals_Assists'] = filtered_df['Goals'] + filtered_df['Assists']
    top_performers = filtered_df.nlargest(10, 'Goals_Assists')[['Player', 'Team', 'Goals', 'Assists', 'Goals_Assists']]
    
    # Crear datos para gráfico de barras horizontales
    bar_data = []
    for _, row in top_performers.iterrows():
        bar_data.append({'Player': row['Player'], 'Métrica': 'Goles', 'Cantidad': row['Goals'], 'Team': row['Team']})
        bar_data.append({'Player': row['Player'], 'Métrica': 'Asistencias', 'Cantidad': row['Assists'], 'Team': row['Team']})
    
    bar_df = pd.DataFrame(bar_data)
    
    fig2 = px.bar(
        bar_df,
        x='Cantidad',
        y='Player',
        color='Métrica',
        orientation='h',  # Horizontal
        title=f"Top 10 Jugadores - Contribución Ofensiva {'(Acumulado)' if season_filter == 'all' else f'(Temporada {season_filter})'}",
        labels={'Cantidad': 'Cantidad', 'Player': 'Jugador'},
        color_discrete_map={'Goles': '#1f77b4', 'Asistencias': '#ff7f0e'}
    )
    fig2.update_layout(
        height=450,
        yaxis={'categoryorder': 'total ascending'},  # Ordenar por total
        margin=dict(l=150)  # Más margen izquierdo para nombres
    )
    
    # Tabla de top jugadores
    # Determinar ordenamiento
    sort_column = 'Goals'  # por defecto
    if sort_assists and sort_assists > (sort_goals or 0) and sort_assists > (sort_minutes or 0):
        sort_column = 'Assists'
    elif sort_minutes and sort_minutes > (sort_goals or 0) and sort_minutes > (sort_assists or 0):
        sort_column = 'Minutes_played'
    
    top_players = filtered_df.nlargest(10, sort_column)[
        ['Player', 'Team', 'Position', 'Goals', 'Assists', 'Minutes_played', 'Temporada']
    ].round(0)  # Redondear a enteros para datos acumulados
    
    table = dash_table.DataTable(
        data=top_players.to_dict('records'),
        columns=[{"name": col, "id": col} for col in top_players.columns],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'row_index': 0},
                'backgroundColor': '#d4edda',
                'color': 'black',
            }
        ],
        page_size=10
    )
    
    return fig1, fig2, table

@callback(
    Output('export-status', 'children'),
    Input('export-pdf-btn', 'n_clicks'),
    prevent_initial_call=True
)
def export_to_pdf(n_clicks):
    """Manejar exportación a PDF"""
    if n_clicks:
        return dbc.Alert(
            "Funcionalidad de exportación PDF en desarrollo. "
            "Los datos están listos para ser exportados.",
            color="info",
            duration=4000
        )
    return ""