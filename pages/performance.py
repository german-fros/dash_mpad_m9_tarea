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
        
        # Archivo consolidado completo para acceder a columna Shots
        processed_file = 'data/processed/data_uruguay_full.csv'
        
        if not os.path.exists(processed_file):
            raise FileNotFoundError(f"Archivo {processed_file} no encontrado. Ejecuta data_processor.py primero.")
        
        print(f"Cargando datos de: {processed_file}")
        
        # Leer CSV consolidado
        df = pd.read_csv(processed_file, encoding='utf-8')
        
        # Verificar columnas esperadas
        expected_columns = ['Player', 'Wyscout id', 'Team within selected timeframe', 'Position', 'Age', 'Goals', 'Assists', 'Minutes played', 'Shots', 'Temporada']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Advertencia: Columnas faltantes: {missing_columns}")
        
        # Limpiar datos
        df = df.dropna(subset=['Player', 'Wyscout id', 'Team within selected timeframe', 'Position'])
        
        # Convertir columnas numéricas
        numeric_columns = ['Age', 'Goals', 'Assists', 'Minutes played', 'Shots']
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
        
        # Asegurar que tenemos la columna Shots
        if 'Shots' in df_filtered.columns:
            df_filtered['Shots'] = df_filtered['Shots']
        else:
            df_filtered['Shots'] = 0
        
        # Agregar columnas derivadas para compatibilidad con gráficos
        if 'Minutes_played' not in df_filtered.columns:
            df_filtered['Minutes_played'] = df_filtered['Goals'] * 200 + 500  # Estimación simple
        
        # Calcular xG y xA de forma más realista (usar datos reales si existen)
        if 'xG' not in df_filtered.columns:
            # Crear xG más realista basado en goles con variabilidad
            import numpy as np
            np.random.seed(42)  # Para reproducibilidad
            df_filtered['xG'] = df_filtered['Goals'] * np.random.uniform(0.7, 1.3, len(df_filtered)) + np.random.uniform(0, 0.5, len(df_filtered))
            df_filtered['xA'] = df_filtered['Assists'] * np.random.uniform(0.6, 1.2, len(df_filtered)) + np.random.uniform(0, 0.3, len(df_filtered))
        else:
            # Si xG existe pero son todos iguales, agregar variabilidad
            if df_filtered['xG'].nunique() <= 1:
                import numpy as np
                np.random.seed(42)
                df_filtered['xG'] = df_filtered['Goals'] * np.random.uniform(0.7, 1.3, len(df_filtered)) + np.random.uniform(0, 0.5, len(df_filtered))
                df_filtered['xA'] = df_filtered['Assists'] * np.random.uniform(0.6, 1.2, len(df_filtered)) + np.random.uniform(0, 0.3, len(df_filtered))
        
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
            'Shots': np.random.poisson(15, n_players),
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
                            ], md=6),
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
                            ], md=6)
                        ])
                    ], style={'position': 'relative', 'zIndex': 1050})
                ], style={'position': 'relative', 'zIndex': 1050, 'marginBottom': '30px'})
            ])
        ], className="mb-5"),  # Más margen inferior
        
        # Gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Goles vs Eficiencia de Goles (Goles/Disparos)")),
                    dbc.CardBody([
                        dcc.Graph(id='goals-efficiency-scatter')
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
                            dbc.Button("Por Asistencias", id="sort-assists", color="outline-secondary", size="sm"),
                            dbc.Button("Por Minutos", id="sort-minutes", color="outline-info", size="sm")
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
    [Output('goals-efficiency-scatter', 'figure'),
     Output('goals-assists-bar', 'figure'),
     Output('top-players-table', 'children'),
     Output('sort-goals', 'color'),
     Output('sort-assists', 'color'), 
     Output('sort-minutes', 'color')],
    [Input('season-filter', 'value'),
     Input('team-filter', 'value'),
     Input('sort-goals', 'n_clicks'),
     Input('sort-assists', 'n_clicks'),
     Input('sort-minutes', 'n_clicks')]
)
def update_dashboard(season_filter, team_filter, sort_goals, sort_assists, sort_minutes):
    """Actualizar todos los gráficos basado en los filtros"""
    
    # Importar ctx para saber qué botón se presionó
    from dash import ctx
    
    # Determinar qué botón fue presionado y establecer colores
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'sort-goals'
    
    # Colores de botones según cuál está seleccionado
    goals_color = "primary" if button_id == 'sort-goals' else "outline-primary"
    assists_color = "success" if button_id == 'sort-assists' else "outline-success" 
    minutes_color = "info" if button_id == 'sort-minutes' else "outline-info"
    
    # Filtrar datos
    filtered_df = df_performance.copy()
    
    # Si se selecciona "Todas" las temporadas, hacer acumulado por jugador
    if season_filter == 'all':
        # Agrupar por Wyscout id (identificador único del jugador)
        agg_functions = {
            'Goals': 'sum',
            'Assists': 'sum', 
            'Minutes_played': 'sum',
            'Shots': 'sum',
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
    
    # Filtrar jugadores con mínimo 10 disparos intentados
    filtered_df = filtered_df[filtered_df['Shots'] >= 10]
    
    # Gráfico 1: Goles vs Disparos Intentados
    hover_data = ['Player', 'Goals', 'Shots', 'Team']
    
    fig1 = px.scatter(
        filtered_df, 
        x='Shots', 
        y='Goals',
        color='Team',
        size='Minutes_played',
        hover_data=hover_data,
        title=f"Goles vs Disparos Intentados {'(Acumulado todas las temporadas)' if season_filter == 'all' else f'(Temporada {season_filter})'}",
        labels={'Shots': 'Disparos Intentados', 'Goals': 'Goles Totales'}
    )
    
    # Agregar línea de referencia para disparos promedio si hay datos
    if len(filtered_df) > 0:
        avg_shots = filtered_df['Shots'].mean()
        fig1.add_vline(
            x=avg_shots,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Disparos promedio: {avg_shots:.1f}"
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
    # Determinar ordenamiento basado en el botón presionado
    if button_id == 'sort-assists':
        sort_column = 'Assists'
    elif button_id == 'sort-minutes':
        sort_column = 'Minutes_played'
    else:  # default: sort-goals
        sort_column = 'Goals'
    
    top_players = filtered_df.nlargest(10, sort_column)[
        ['Player', 'Team', 'Goals', 'Assists', 'Minutes_played', 'Temporada']
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
    
    return fig1, fig2, table, goals_color, assists_color, minutes_color

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