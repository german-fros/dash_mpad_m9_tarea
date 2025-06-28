from dash import html
import dash_bootstrap_components as dbc
import sys
import os
import logging

# Configurar logging específico para página home
logger = logging.getLogger(__name__)

# Manejo de errores en configuración de path
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logger.info("Path configurado correctamente para home")
except Exception as e:
    logger.error(f"Error configurando path en home: {str(e)}")

# Importar navbar con manejo de errores
navbar_component = None
try:
    from components.navbar import create_navbar
    navbar_component = create_navbar()
    logger.info("Navbar importado y creado correctamente")
except ImportError as e:
    logger.error(f"Error importando navbar: {str(e)}")
    # Crear navbar de fallback
    navbar_component = dbc.NavbarSimple(
        brand="Dashboard Deportivo",
        brand_href="/",
        color="primary",
        dark=True,
        className="mb-4"
    )
    logger.warning("Usando navbar de fallback")
except Exception as e:
    logger.error(f"Error general con navbar: {str(e)}")
    navbar_component = html.Div()  # Navbar vacío como último recurso

def create_home_layout():
    """Crear layout de home con manejo de errores"""
    try:
        # Validar que el navbar existe
        if navbar_component is None:
            logger.warning("Navbar no disponible, creando layout sin navbar")
            navbar_section = html.Div()
        else:
            navbar_section = navbar_component

        # Crear layout principal
        main_content = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Bienvenido al Dashboard Deportivo", 
                           className="text-center mb-4 fade-in"),
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
                            ], className="h-100")
                        ], md=6, className="mb-3"),
                        
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("Dashboard GPS", className="card-title"),
                                    html.P("Análisis de datos de tracking y movimiento GPS"),
                                    dbc.Button("Acceder", color="success", href="/gps")
                                ])
                            ], className="h-100")
                        ], md=6, className="mb-3")
                    ], className="g-3")
                ])
            ])
        ], fluid=True, className="main-container fade-in")

        # Combinar navbar y contenido
        return html.Div([
            navbar_section,
            main_content
        ])

    except Exception as e:
        logger.error(f"Error creando layout principal de home: {str(e)}")
        # Layout de fallback para errores críticos
        return create_fallback_layout()

def create_fallback_layout():
    """Layout de emergencia para home"""
    try:
        return dbc.Container([
            dbc.Alert([
                html.H4("Error cargando página principal"),
                html.P("Ha ocurrido un error al cargar la página de inicio."),
                html.Hr(),
                dbc.Button("Ir a Login", href="/login", color="primary"),
                html.P("Si el problema persiste, contacte al administrador.", 
                       className="mt-3 mb-0 text-muted")
            ], color="danger", className="mt-5")
        ], className="mt-5")
    except Exception as e:
        logger.critical(f"Error crítico en fallback layout: {str(e)}")
        # Último recurso absoluto
        return html.Div([
            html.H1("Error del Sistema", style={"color": "red", "text-align": "center"}),
            html.P("Por favor, recarga la página", style={"text-align": "center"}),
            html.A("Ir a Login", href="/login", style={"display": "block", "text-align": "center"})
        ], style={"padding": "50px"})

def create_minimal_layout():
    """Layout mínimo sin navbar para casos de error"""
    try:
        return dbc.Container([
            html.Div([
                html.H1("Dashboard Deportivo", className="text-center mb-4"),
                html.P("Modo de recuperación - funcionalidad limitada", 
                       className="text-center text-warning mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Performance", href="/performance", color="primary", 
                                 className="w-100 mb-2")
                    ], md=6),
                    dbc.Col([
                        dbc.Button("GPS", href="/gps", color="success", 
                                 className="w-100 mb-2")
                    ], md=6)
                ]),
                
                html.Hr(),
                html.P("Algunas funcionalidades pueden no estar disponibles", 
                       className="text-center text-muted")
            ])
        ], className="mt-5")
    except Exception as e:
        logger.error(f"Error en layout mínimo: {str(e)}")
        return html.Div("Error crítico del sistema")

# Crear layout principal con manejo de errores
try:
    layout = create_home_layout()
    
    # Validar que el layout se creó correctamente
    if not layout or not hasattr(layout, 'children'):
        raise ValueError("Layout de home inválido")
    
    logger.info("Layout de home creado correctamente")
    
except Exception as e:
    logger.error(f"Error crítico creando layout de home: {str(e)}")
    try:
        # Intentar layout de fallback
        layout = create_fallback_layout()
        logger.warning("Usando layout de fallback para home")
    except Exception as fallback_error:
        logger.critical(f"Error en layout de fallback: {str(fallback_error)}")
        try:
            # Último intento con layout mínimo
            layout = create_minimal_layout()
            logger.warning("Usando layout mínimo para home")
        except Exception as minimal_error:
            logger.critical(f"Error crítico en layout mínimo: {str(minimal_error)}")
            # Último recurso absoluto
            layout = html.Div([
                html.H1("Error del Sistema"),
                html.P("No se pudo cargar la página principal"),
                html.A("Ir a Login", href="/login")
            ], style={"padding": "50px", "text-align": "center"})

def validate_layout():
    """Validar que el layout de home funciona correctamente"""
    try:
        if not layout:
            logger.error("Layout de home es None")
            return False
        
        if not hasattr(layout, 'children'):
            logger.error("Layout de home no tiene children")
            return False
        
        # Verificar elementos críticos
        layout_str = str(layout)
        critical_elements = ['Dashboard', 'Performance', 'GPS']
        
        for element in critical_elements:
            if element not in layout_str:
                logger.warning(f"Elemento crítico '{element}' no encontrado en home")
                return False
        
        logger.info("Validación de layout de home exitosa")
        return True
        
    except Exception as e:
        logger.error(f"Error validando layout de home: {str(e)}")
        return False

def get_layout_info():
    """Información de debugging del layout de home"""
    try:
        info = {
            "layout_type": type(layout).__name__,
            "has_children": hasattr(layout, 'children'),
            "navbar_available": navbar_component is not None,
            "is_valid": validate_layout()
        }
        logger.info(f"Info layout home: {info}")
        return info
    except Exception as e:
        logger.error(f"Error obteniendo info de layout: {str(e)}")
        return {"error": str(e)}

# Ejecutar validaciones al cargar
try:
    validation_result = validate_layout()
    if not validation_result:
        logger.warning("Layout de home no pasó validación inicial")
    
    layout_info = get_layout_info()
    logger.info(f"Página home cargada correctamente. Info: {layout_info}")
    
except Exception as e:
    logger.error(f"Error en validaciones iniciales de home: {str(e)}")

# Función de recuperación para home
def recover_home_layout():
    """Intentar recuperar el layout de home"""
    global layout
    try:
        logger.info("Intentando recuperar layout de home...")
        layout = create_home_layout()
        
        if validate_layout():
            logger.info("Layout de home recuperado exitosamente")
            return True
        else:
            logger.warning("Layout recuperado pero falló validación")
            layout = create_fallback_layout()
            return False
            
    except Exception as e:
        logger.error(f"Error en recuperación de layout de home: {str(e)}")
        layout = create_minimal_layout()
        return False