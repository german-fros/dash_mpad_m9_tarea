from dash import html, dcc
import dash_bootstrap_components as dbc
import sys
import os
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Manejo de errores en importaciones
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logger.info("Path configurado correctamente")
except Exception as e:
    logger.error(f"Error configurando path: {str(e)}")

def create_login_layout():
    """Crear layout simple de login con manejo de errores"""
    try:
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H2("Login", className="text-center mb-4"),
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Input(
                                id="username", 
                                placeholder="Usuario", 
                                type="text", 
                                className="mb-2"
                            ),
                            dbc.Input(
                                id="password", 
                                placeholder="Contraseña", 
                                type="password", 
                                className="mb-2"
                            ),
                            dbc.Button(
                                "Entrar", 
                                id="login-button", 
                                color="primary", 
                                className="mb-2 w-100"
                            ),
                            html.Div(id="login-output")
                        ])
                    ])
                ], width=12, md=6, lg=4)
            ], justify="center", className="mt-5")
        ], fluid=True)
        
    except Exception as e:
        logger.error(f"Error creando layout: {str(e)}")
        return dbc.Container([
            dbc.Alert("Error cargando página de login", color="danger"),
            html.P("Por favor, recarga la página")
        ])

# Crear layout con manejo de errores
try:
    layout = create_login_layout()
    
    # Validación básica
    if not layout or not hasattr(layout, 'children'):
        raise ValueError("Layout inválido")
    
    logger.info("Layout de login creado correctamente")
    
except Exception as e:
    logger.error(f"Error crítico: {str(e)}")
    # Layout de emergencia
    layout = html.Div([
        html.H2("Error del Sistema"),
        html.P("No se pudo cargar la página de login"),
        html.Button("Recargar", onClick="window.location.reload()")
    ], style={"text-align": "center", "padding": "50px"})

def validate_layout():
    """Validar layout"""
    try:
        required_ids = ['username', 'password', 'login-button', 'login-output']
        layout_str = str(layout)
        
        for id_name in required_ids:
            if id_name not in layout_str:
                logger.warning(f"ID {id_name} no encontrado")
                return False
        
        return True
    except Exception as e:
        logger.error(f"Error validando: {str(e)}")
        return False

# Validar al cargar
try:
    if validate_layout():
        logger.info("Validación exitosa")
    else:
        logger.warning("Validación falló")
except Exception as e:
    logger.error(f"Error en validación: {str(e)}")