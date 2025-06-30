from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.navbar import create_navbar

# Función para cargar y procesar datos de contratos
def load_contracts_data():
    """Cargar y procesar datos de contratos con posiciones simplificadas"""
    try:
        # Cargar el dataset
        contracts_file = 'data/raw/contratos_uruguay.csv'
        
        if not os.path.exists(contracts_file):
            raise FileNotFoundError(f"Archivo {contracts_file} no encontrado.")
        
        print(f"Cargando datos de contratos de: {contracts_file}")
        
        # Leer CSV
        df = pd.read_csv(contracts_file, encoding='utf-8')
        
        # Mapear columna Equipo a Club para compatibilidad
        if 'Equipo' in df.columns:
            df['Club'] = df['Equipo']
        
        # Procesar fechas
        df['Fecha_inicio'] = pd.to_datetime(df['Fecha_inicio'], errors='coerce')
        df['Fecha_fin'] = pd.to_datetime(df['Fecha_fin'], errors='coerce')
        
        # Crear función para simplificar posiciones
        def simplify_position(position):
            """Simplifica las posiciones a 4 categorías principales"""
            if pd.isna(position):
                return 'Desconocido'
            
            position = str(position).upper()
            
            # Primero verificar si ya es una posición simplificada
            if 'PORTERO' in position:
                return 'Portero'
            elif 'DEFENSA' in position:
                return 'Defensa'
            elif 'MEDIOCAMPISTA' in position:
                return 'Mediocampo'
            elif 'DELANTERO' in position:
                return 'Delantero'
            # Luego verificar códigos tradicionales
            elif 'GK' in position:
                return 'Portero'
            elif any(def_pos in position for def_pos in ['CB', 'LB', 'RB', 'LCB', 'RCB', 'WB', 'LWB', 'RWB']):
                return 'Defensa'
            elif any(mid_pos in position for mid_pos in ['MF', 'DMF', 'CMF', 'AMF', 'LCMF', 'RCMF', 'LDMF', 'RDMF']):
                return 'Mediocampo'
            elif any(fwd_pos in position for fwd_pos in ['CF', 'ST', 'LW', 'RW', 'LAMF', 'RAMF']):
                return 'Delantero'
            else:
                # Para posiciones mixtas, tomar la primera parte
                first_pos = position.split(',')[0].strip()
                return simplify_position(first_pos)
        
        # Aplicar simplificación de posiciones
        df['Posicion_Simplificada'] = df['Posición'].apply(simplify_position)
        
        # Calcular duración de contrato en días
        df['Duracion_Contrato'] = (df['Fecha_fin'] - df['Fecha_inicio']).dt.days
        
        # Determinar si el contrato está activo y filtrar solo activos
        today = datetime.now()
        df['Contrato_Activo'] = (df['Fecha_inicio'] <= today) & (df['Fecha_fin'] >= today)
        
        # Filtrar solo contratos activos
        df = df[df['Contrato_Activo'] == True].copy()
        
        # Extraer año de inicio para análisis temporal
        df['Año_Inicio'] = df['Fecha_inicio'].dt.year
        
        # Limpiar datos numéricos
        df['Salario_mensual_usd'] = pd.to_numeric(df['Salario_mensual_usd'], errors='coerce').fillna(0)
        df['Cláusula_rescisión_usd'] = pd.to_numeric(df['Cláusula_rescisión_usd'], errors='coerce').fillna(0)
        
        print(f"Datos procesados: {len(df)} contratos")
        print(f"Posiciones simplificadas: {df['Posicion_Simplificada'].value_counts()}")
        print(f"Contratos activos: {df['Contrato_Activo'].sum()}")
        
        return df
        
    except Exception as e:
        print(f"Error cargando datos de contratos: {e}")
        # Datos de respaldo
        import numpy as np
        np.random.seed(42)
        
        clubs = ['Nacional', 'Peñarol', 'Defensor Sporting', 'Wanderers', 'Liverpool', 'Danubio']
        positions = ['Portero', 'Defensa', 'Mediocampo', 'Delantero']
        
        # Nombres reales de ejemplo para datos de respaldo
        sample_names = [
            'L. Suárez', 'E. Cavani', 'D. Godín', 'J. Giménez', 'R. Bentancur', 'F. Muslera',
            'M. Cáceres', 'N. Nández', 'G. Varela', 'F. Torres', 'D. Núñez', 'S. Coates',
            'J. Rodríguez', 'M. Arambarri', 'G. Pereiro', 'C. Stuani', 'A. Gómez', 'L. Olaza',
            'B. Rodríguez', 'F. Pellistri', 'M. Olivera', 'R. Agirre', 'D. López', 'C. Vega'
        ]
        
        n_contracts = 50  # Reducir número para evitar repetición
        # Asegurar contratos activos para datos de respaldo
        start_dates = pd.date_range('2022-01-01', '2024-06-30', periods=n_contracts)
        end_dates = pd.date_range('2025-01-01', '2027-12-31', periods=n_contracts)
        
        data = {
            'Jugador': np.random.choice(sample_names, n_contracts),
            'Posición': np.random.choice(['GK', 'CB', 'DMF', 'CF'], n_contracts),
            'Posicion_Simplificada': np.random.choice(positions, n_contracts),
            'Club': np.random.choice(clubs, n_contracts),
            'Fecha_inicio': start_dates,
            'Fecha_fin': end_dates,
            'Salario_mensual_usd': np.random.randint(8000, 25000, n_contracts),
            'Cláusula_rescisión_usd': np.random.randint(200000, 1000000, n_contracts),
            'Contrato_Activo': [True] * n_contracts,  # Todos activos
            'Año_Inicio': start_dates.year
        }
        
        return pd.DataFrame(data)

# Cargar datos
df_contracts = load_contracts_data()

layout = html.Div([
    create_navbar(),
    dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("Dashboard Administrativo", className="mb-4"),
                html.P("Análisis de contratos y gestión financiera de jugadores", 
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
                                dbc.Label("Club"),
                                dcc.Dropdown(
                                    id='club-filter-adm',
                                    options=[{'label': club, 'value': club} for club in sorted(df_contracts['Club'].unique())],
                                    value=sorted(df_contracts['Club'].unique())[0],
                                    placeholder="Seleccionar club",
                                    style={'zIndex': 1050}
                                )
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Posición"),
                                dcc.Dropdown(
                                    id='position-filter-adm',
                                    options=[{'label': 'Todas', 'value': 'all'}] + 
                                           [{'label': pos, 'value': pos} for pos in sorted(df_contracts['Posicion_Simplificada'].unique())],
                                    value='all',
                                    placeholder="Seleccionar posición",
                                    style={'zIndex': 1049}
                                )
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Rango Salarial (USD)"),
                                dcc.RangeSlider(
                                    id='salary-range-adm',
                                    min=df_contracts['Salario_mensual_usd'].min(),
                                    max=df_contracts['Salario_mensual_usd'].max(),
                                    step=1000,
                                    marks={
                                        int(df_contracts['Salario_mensual_usd'].min()): f"${int(df_contracts['Salario_mensual_usd'].min()/1000)}k",
                                        int(df_contracts['Salario_mensual_usd'].max()): f"${int(df_contracts['Salario_mensual_usd'].max()/1000)}k"
                                    },
                                    value=[df_contracts['Salario_mensual_usd'].min(), df_contracts['Salario_mensual_usd'].max()],
                                    tooltip={"placement": "bottom", "always_visible": True}
                                )
                            ], md=4)
                        ])
                    ], style={'position': 'relative', 'zIndex': 1050})
                ], style={'position': 'relative', 'zIndex': 1050, 'marginBottom': '30px'})
            ])
        ], className="mb-5"),
        
        # Gráficos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Salarios Promedio por Posición")),
                    dbc.CardBody([
                        dcc.Graph(id='salary-position-chart')
                    ])
                ])
            ], md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Contratos que Vencen por Semestre")),
                    dbc.CardBody([
                        dcc.Graph(id='contracts-timeline-chart')
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        # Tabla de contratos
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Contratos Activos", className="mb-0"),
                        dbc.ButtonGroup([
                            dbc.Button("Por Fecha Fin", id="sort-date", color="primary", size="sm"),
                            dbc.Button("Por Posición", id="sort-position", color="outline-secondary", size="sm"),
                            dbc.Button("Por Salario", id="sort-salary", color="outline-info", size="sm")
                        ], className="float-end")
                    ]),
                    dbc.CardBody([
                        html.Div(id='contracts-table')
                    ])
                ])
            ])
        ])
        
    ], fluid=True, className="main-container fade-in")
])

# Callbacks para interactividad
@callback(
    [Output('salary-position-chart', 'figure'),
     Output('contracts-timeline-chart', 'figure'),
     Output('contracts-table', 'children'),
     Output('sort-date', 'color'),
     Output('sort-position', 'color'),
     Output('sort-salary', 'color')],
    [Input('club-filter-adm', 'value'),
     Input('position-filter-adm', 'value'),
     Input('salary-range-adm', 'value'),
     Input('sort-date', 'n_clicks'),
     Input('sort-position', 'n_clicks'),
     Input('sort-salary', 'n_clicks')]
)
def update_admin_dashboard(club_filter, position_filter, salary_range, sort_date, sort_position, sort_salary):
    """Actualizar dashboard administrativo basado en filtros"""
    
    # Importar ctx para saber qué botón se presionó
    from dash import ctx
    
    # Determinar qué botón fue presionado y establecer colores
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'sort-date'
    
    # Colores de botones según cuál está seleccionado
    date_color = "primary" if button_id == 'sort-date' else "outline-primary"
    position_color = "success" if button_id == 'sort-position' else "outline-success"
    salary_color = "info" if button_id == 'sort-salary' else "outline-info"
    
    # Filtrar datos
    filtered_df = df_contracts.copy()
    
    # Siempre filtrar por el club seleccionado (ya no hay opción 'all')
    filtered_df = filtered_df[filtered_df['Club'] == club_filter]
    
    if position_filter != 'all':
        filtered_df = filtered_df[filtered_df['Posicion_Simplificada'] == position_filter]
    
    # Filtrar por rango salarial
    if salary_range:
        filtered_df = filtered_df[
            (filtered_df['Salario_mensual_usd'] >= salary_range[0]) & 
            (filtered_df['Salario_mensual_usd'] <= salary_range[1])
        ]
    
    # Gráfico 1: Salarios promedio por posición
    salary_by_position = filtered_df.groupby('Posicion_Simplificada')['Salario_mensual_usd'].mean().reset_index()
    
    fig1 = px.bar(
        salary_by_position,
        x='Posicion_Simplificada',
        y='Salario_mensual_usd',
        title="Salario Promedio Mensual por Posición",
        labels={'Posicion_Simplificada': 'Posición', 'Salario_mensual_usd': 'Salario Promedio (USD)'},
        color_discrete_sequence=['#1f77b4']
    )
    fig1.update_layout(height=400, showlegend=False)
    fig1.update_yaxes(tickformat='$,.0f')
    
    # Gráfico 2: Contratos que vencen en los próximos semestres
    from datetime import datetime, timedelta
    
    # Filtrar contratos que vencen en los próximos 3 años (6 semestres)
    today = datetime.now()
    next_three_years = today + timedelta(days=1095)  # 3 años
    
    expiring_contracts = filtered_df[
        (filtered_df['Fecha_fin'] >= today) & 
        (filtered_df['Fecha_fin'] <= next_three_years)
    ].copy()
    
    if len(expiring_contracts) > 0:
        # Calcular semestre de vencimiento
        def get_semester(date):
            year = date.year
            if date.month <= 6:
                return f"{year}-1"  # Primer semestre
            else:
                return f"{year}-2"  # Segundo semestre
        
        expiring_contracts['Semestre_Vencimiento'] = expiring_contracts['Fecha_fin'].apply(get_semester)
        
        # Agrupar por semestre
        contracts_by_semester = expiring_contracts.groupby('Semestre_Vencimiento').size().reset_index(name='Contratos_Vencen')
        contracts_by_semester = contracts_by_semester.sort_values('Semestre_Vencimiento')
        
        fig2 = px.bar(
            contracts_by_semester,
            x='Semestre_Vencimiento',
            y='Contratos_Vencen',
            title="Contratos que Vencen en los Próximos Semestres",
            labels={'Semestre_Vencimiento': 'Semestre', 'Contratos_Vencen': 'Número de Contratos'},
            color_discrete_sequence=['#ff7f0e']
        )
    else:
        # Si no hay contratos que vencen, mostrar gráfico vacío
        fig2 = px.bar(
            pd.DataFrame({'Semestre': ['Sin datos'], 'Contratos': [0]}),
            x='Semestre',
            y='Contratos',
            title="Contratos que Vencen en los Próximos Semestres",
            labels={'Semestre': 'Semestre', 'Contratos': 'Número de Contratos'}
        )
    
    fig2.update_layout(height=400)
    
    # Tabla de contratos ordenada según botón seleccionado
    table_data = filtered_df[[
        'Jugador', 'Posicion_Simplificada', 'Club', 'Fecha_inicio', 'Fecha_fin', 
        'Salario_mensual_usd', 'Cláusula_rescisión_usd'
    ]].copy()
    
    # Determinar ordenamiento basado en el botón presionado
    if button_id == 'sort-position':
        table_data = table_data.sort_values('Posicion_Simplificada')
    elif button_id == 'sort-salary':
        table_data = table_data.sort_values('Salario_mensual_usd', ascending=False)
    else:  # default: sort-date
        table_data = table_data.sort_values('Fecha_fin')
    
    # Tomar los primeros 15 registros después del ordenamiento
    table_data = table_data.head(15)
    
    # Formatear fechas y monedas para la tabla
    table_data['Fecha_inicio'] = table_data['Fecha_inicio'].dt.strftime('%d/%m/%Y')
    table_data['Fecha_fin'] = table_data['Fecha_fin'].dt.strftime('%d/%m/%Y')
    table_data['Salario_mensual_usd'] = table_data['Salario_mensual_usd'].apply(lambda x: f"${x:,.0f}")
    table_data['Cláusula_rescisión_usd'] = table_data['Cláusula_rescisión_usd'].apply(lambda x: f"${x:,.0f}")
    
    # Renombrar columnas para la tabla
    table_data.columns = ['Jugador', 'Posición', 'Club', 'F. Inicio', 'F. Fin', 'Salario Mensual', 'Cláusula']
    
    table = dash_table.DataTable(
        data=table_data.to_dict('records'),
        columns=[{"name": col, "id": col} for col in table_data.columns],
        style_cell={'textAlign': 'left', 'padding': '10px', 'fontSize': '12px'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_data_conditional=[
            {
                'if': {'row_index': 0},
                'backgroundColor': '#d4edda',
                'color': 'black',
            }
        ],
        page_size=15,
        style_table={'overflowX': 'auto'}
    )
    
    return fig1, fig2, table, date_color, position_color, salary_color