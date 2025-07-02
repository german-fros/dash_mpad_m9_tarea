"""
Dashboard Deportivo - Aplicación Principal
==========================================

Este módulo contiene la aplicación principal del Dashboard Deportivo, una aplicación web
desarrollada con Dash/Flask que proporciona análisis de rendimiento deportivo y gestión
administrativa de contratos de jugadores.

Arquitectura:
- Flask como servidor backend con autenticación Flask-Login
- Dash para la interfaz interactiva y visualizaciones
- Sistema de routing multi-página
- Manejo robusto de errores con múltiples niveles de fallback
- Logging comprehensivo para debugging y monitoreo

Autor: Dashboard Deportivo Team
Fecha: 2024
"""

from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from flask import Flask
from flask_login import LoginManager, login_user, logout_user, current_user
import logging
import traceback

from login_manager import get_user, authenticate_user

# ========================================
# CONFIGURACIÓN DE LOGGING Y SERVIDOR
# ========================================

# Configurar sistema de logging para debugging y monitoreo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),  # Log a archivo para persistencia
        logging.StreamHandler()          # Log a consola para desarrollo
    ]
)
logger = logging.getLogger(__name__)

# ========================================
# SERVIDOR FLASK Y AUTENTICACIÓN
# ========================================

# Crear servidor Flask base para integración con Dash
server = Flask(__name__)
server.secret_key = 'super-secret-key'  # TODO: Mover a variable de entorno en producción

# Configurar Flask-Login para manejo de sesiones de usuario
login_manager = LoginManager()
try:
    login_manager.init_app(server)
    logger.info("Login manager inicializado correctamente")
except Exception as e:
    logger.error(f"Error inicializando login manager: {str(e)}")
    raise

@login_manager.user_loader
def load_user(user_id):
    """
    Callback requerido por Flask-Login para cargar usuario desde ID de sesión.
    
    Args:
        user_id (str): ID único del usuario almacenado en sesión
        
    Returns:
        User object o None si usuario no encontrado
        
    Note:
        Incluye manejo de errores para prevenir crashes por usuarios inválidos
    """
    try:
        user = get_user(user_id)
        if user:
            logger.info(f"Usuario {user_id} cargado correctamente")
        return user
    except Exception as e:
        logger.error(f"Error cargando usuario {user_id}: {str(e)}")
        return None

# ========================================
# APLICACIÓN DASH
# ========================================

# Crear aplicación Dash integrada con Flask server
try:
    app = Dash(
        __name__,
        server=server,                                    # Usar Flask server existente
        external_stylesheets=[dbc.themes.BOOTSTRAP],     # Bootstrap para styling
        suppress_callback_exceptions=True                # Permitir callbacks dinámicos
    )
    logger.info("Aplicación Dash inicializada correctamente")
except Exception as e:
    logger.error(f"Error inicializando aplicación Dash: {str(e)}")
    raise

# ========================================
# IMPORTACIÓN DE PÁGINAS Y LAYOUTS
# ========================================

# Importar layouts de todas las páginas con manejo robusto de errores
try:
    from pages.login import layout as login_layout
    from pages.home import layout as home_layout  
    from pages.performance import layout as performance_layout
    from pages.adm import layout as adm_layout

    # Wrapper simple para layouts - facilita manejo uniforme
    class SimplePage:
        """Contenedor simple para layouts de página"""
        def __init__(self, layout):
            self.layout = layout

    # Crear objetos página para cada sección de la aplicación
    login = SimplePage(login_layout)          # Página de autenticación
    home = SimplePage(home_layout)            # Dashboard principal  
    performance = SimplePage(performance_layout)  # Análisis de rendimiento
    adm = SimplePage(adm_layout)              # Panel administrativo
    
    logger.info("Páginas importadas correctamente")
except ImportError as e:
    logger.error(f"Error importando páginas: {str(e)}")
    
    # Sistema de fallback: crear layouts de emergencia si falla importación
    class FallbackPage:
        """Página de fallback cuando falla carga de layouts principales"""
        layout = html.Div([
            dbc.Alert("Error cargando página", color="danger"),
            html.P("Por favor, recarga la aplicación")
        ])
    
    # Usar páginas de fallback para todas las secciones
    login = home = performance = adm = FallbackPage()

# ========================================
# LAYOUT PRINCIPAL Y ROUTING
# ========================================

# Configurar layout principal de la aplicación (estructura SPA)
try:
    app.layout = dbc.Container([
        dcc.Location(id='url', refresh=False),  # Componente de routing sin refresh
        html.Div(id='page-content')             # Contenedor dinámico para páginas
    ])
    logger.info("Layout principal configurado correctamente")
except Exception as e:
    logger.error(f"Error configurando layout: {str(e)}")
    app.layout = html.Div("Error de configuración")

# ========================================
# CALLBACKS DE ROUTING Y NAVEGACIÓN
# ========================================

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    prevent_initial_call=False
)
def display_page(pathname):
    """
    Callback principal de routing - determina qué página mostrar según URL.
    
    Maneja la navegación entre diferentes secciones de la aplicación y
    verifica autenticación para páginas protegidas.
    
    Args:
        pathname (str): Ruta URL actual (ej: '/', '/performance', '/login')
        
    Returns:
        dash.html.Div: Layout de la página correspondiente o redirección
        
    Rutas disponibles:
        - '/' o '': Dashboard principal (requiere autenticación)
        - '/login': Página de login
        - '/performance': Análisis de rendimiento (requiere autenticación)
        - '/administrativo': Panel administrativo (requiere autenticación)
    """
    try:
        # Normalizar pathname para manejo consistente
        if pathname is None:
            pathname = '/'
        
        logger.info(f"Navegando a: {pathname}")
        
        # === PÁGINA DE LOGIN (Pública) ===
        if pathname == '/login':
            return login.layout
            
        # === PÁGINA PRINCIPAL (Protegida) ===
        elif pathname == '/' or pathname == '':
            try:
                # Verificar si usuario está autenticado antes de mostrar dashboard
                if current_user.is_authenticated:
                    return home.layout
                else:
                    logger.info("Usuario no autenticado, redirigiendo a login")
                    return dcc.Location(href="/login", id="redirect-to-login")
            except Exception as auth_error:
                logger.error(f"Error verificando autenticación: {str(auth_error)}")
                return dcc.Location(href="/login", id="redirect-to-login")
                
        # === PÁGINA DE PERFORMANCE (Protegida) ===
        elif pathname == '/performance':
            try:
                if current_user.is_authenticated:
                    return performance.layout
                else:
                    return dcc.Location(href="/login", id="redirect-to-login")
            except Exception as auth_error:
                logger.error(f"Error en página performance: {str(auth_error)}")
                return dbc.Alert("Error cargando página de performance", color="danger")
                
        # === PÁGINA ADMINISTRATIVA (Protegida) ===
        elif pathname == '/administrativo':
            try:
                if current_user.is_authenticated:
                    return adm.layout
                else:
                    return dcc.Location(href="/login", id="redirect-to-login")
            except Exception as auth_error:
                logger.error(f"Error en página administrativa: {str(auth_error)}")
                return dbc.Alert("Error cargando página administrativa", color="danger")
                
        # === PÁGINA NO ENCONTRADA (404) ===
        else:
            logger.warning(f"Página no encontrada: {pathname}")
            return html.Div([
                dbc.Alert("404 - Página no encontrada", color="warning"),
                dbc.Button("Ir a Home", href="/", color="primary")
            ])
            
    except Exception as e:
        # Capturar cualquier error no manejado en routing
        logger.error(f"Error en display_page: {str(e)}\n{traceback.format_exc()}")
        return dbc.Alert([
            html.H4("Error de navegación"),
            html.P(f"Ha ocurrido un error: {str(e)}"),
            dbc.Button("Ir a Login", href="/login", color="primary")
        ], color="danger")

# ========================================
# CALLBACKS DE AUTENTICACIÓN
# ========================================

@app.callback(
    Output("login-output", "children"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def login_callback(n_clicks, username, password):
    """
    Callback para procesar intentos de login del usuario.
    
    Valida credenciales, maneja errores de autenticación y redirige
    al dashboard principal en caso de login exitoso.
    
    Args:
        n_clicks (int): Número de clicks en botón de login
        username (str): Nombre de usuario ingresado
        password (str): Contraseña ingresada
        
    Returns:
        dash component: Mensaje de error o redirección a dashboard
        
    Security Notes:
        - Valida campos vacíos antes de autenticación
        - Logs intentos fallidos para monitoreo de seguridad
        - No expone información sensible en logs
    """
    try:
        # Validar que se hizo click
        if not n_clicks or n_clicks == 0:
            return ""
        
        # Validar inputs
        if not username or not password:
            logger.warning("Intento de login con campos vacíos")
            return dbc.Alert("Por favor complete todos los campos", color="warning")
        
        # Validar longitud
        if len(username.strip()) == 0 or len(password.strip()) == 0:
            return dbc.Alert("Los campos no pueden estar vacíos", color="warning")
        
        # Intentar autenticación
        try:
            user = get_user(username.strip())
            if user and password.strip() == user.password:
                login_user(user)
                logger.info(f"Login exitoso para usuario: {username}")
                return dcc.Location(href="/", id="redirect")
            else:
                logger.warning(f"Intento de login fallido para usuario: {username}")
                return dbc.Alert("Credenciales incorrectas", color="danger")
                
        except Exception as auth_error:
            logger.error(f"Error en autenticación: {str(auth_error)}")
            return dbc.Alert("Error interno de autenticación", color="danger")
            
    except Exception as e:
        logger.error(f"Error en login_callback: {str(e)}\n{traceback.format_exc()}")
        return dbc.Alert("Error interno del sistema", color="danger")

@app.callback(
    Output("logout-output", "children"),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True
)
def logout_callback(n_clicks):
    """Logout con manejo de errores"""
    try:
        if not n_clicks or n_clicks == 0:
            return ""
            
        try:
            if current_user.is_authenticated:
                username = current_user.id
                logout_user()
                logger.info(f"Logout exitoso para usuario: {username}")
            else:
                logger.info("Intento de logout sin usuario autenticado")
                
            return dcc.Location(href="/login", id="redirect-logout")
            
        except Exception as logout_error:
            logger.error(f"Error en logout: {str(logout_error)}")
            # Forzar redirección a login aunque haya error
            return dcc.Location(href="/login", id="redirect-logout")
            
    except Exception as e:
        logger.error(f"Error en logout_callback: {str(e)}\n{traceback.format_exc()}")
        return dcc.Location(href="/login", id="redirect-logout")

# Callback para logout desde navbar (ARREGLADO)
@app.callback(
    Output("url", "pathname"),
    Input("navbar-logout", "n_clicks"),
    prevent_initial_call=True
)
def navbar_logout_callback(n_clicks):
    """Logout desde navbar con manejo de errores"""
    try:
        if not n_clicks or n_clicks == 0:
            return "/"
            
        try:
            if current_user.is_authenticated:
                username = current_user.id
                logout_user()
                logger.info(f"Logout desde navbar exitoso para usuario: {username}")
            
            return "/login"
            
        except Exception as logout_error:
            logger.error(f"Error en logout navbar: {str(logout_error)}")
            return "/login"
            
    except Exception as e:
        logger.error(f"Error en navbar_logout_callback: {str(e)}")
        return "/"

# Callback para navegación desde Home button
@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("navbar-home", "n_clicks"),
    prevent_initial_call=True
)
def navbar_home_callback(n_clicks):
    """Navegación a Home desde navbar"""
    try:
        if not n_clicks or n_clicks == 0:
            return "/"
            
        logger.info("Navegando a Home desde navbar")
        return "/"
        
    except Exception as e:
        logger.error(f"Error en navbar_home_callback: {str(e)}")
        return "/"

# Callback para navegación desde Home button fallback
@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("navbar-home-fallback", "n_clicks"),
    prevent_initial_call=True
)
def navbar_home_fallback_callback(n_clicks):
    """Navegación a Home desde navbar fallback"""
    try:
        if not n_clicks or n_clicks == 0:
            return "/"
            
        logger.info("Navegando a Home desde navbar fallback")
        return "/"
        
    except Exception as e:
        logger.error(f"Error en navbar_home_fallback_callback: {str(e)}")
        return "/"

if __name__ == "__main__":
    try:
        logger.info("Iniciando aplicación...")
        app.run(debug=True, dev_tools_ui=True, dev_tools_hot_reload=True)
    except Exception as e:
        logger.error(f"Error iniciando aplicación: {str(e)}")
        raise