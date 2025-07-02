from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from flask import Flask
from flask_login import LoginManager, login_user, logout_user, current_user
import logging
import traceback

from login_manager import get_user, authenticate_user

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask base
server = Flask(__name__)
server.secret_key = 'super-secret-key'

# Login manager con manejo de errores
login_manager = LoginManager()
try:
    login_manager.init_app(server)
    logger.info("Login manager inicializado correctamente")
except Exception as e:
    logger.error(f"Error inicializando login manager: {str(e)}")
    raise

@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario con manejo de errores"""
    try:
        user = get_user(user_id)
        if user:
            logger.info(f"Usuario {user_id} cargado correctamente")
        return user
    except Exception as e:
        logger.error(f"Error cargando usuario {user_id}: {str(e)}")
        return None

# Dash app
try:
    app = Dash(
        __name__,
        server=server,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )
    logger.info("Aplicación Dash inicializada correctamente")
except Exception as e:
    logger.error(f"Error inicializando aplicación Dash: {str(e)}")
    raise

# Importar páginas con manejo de errores
try:
    from pages.login import layout as login_layout
    from pages.home import layout as home_layout  
    from pages.performance import layout as performance_layout
    from pages.adm import layout as adm_layout

    # Crear objetos página simples
    class SimplePage:
        def __init__(self, layout):
            self.layout = layout

    login = SimplePage(login_layout)
    home = SimplePage(home_layout)
    performance = SimplePage(performance_layout)
    adm = SimplePage(adm_layout)
    
    logger.info("Páginas importadas correctamente")
except ImportError as e:
    logger.error(f"Error importando páginas: {str(e)}")
    # Crear layouts de fallback
    class FallbackPage:
        layout = html.Div([
            dbc.Alert("Error cargando página", color="danger"),
            html.P("Por favor, recarga la aplicación")
        ])
    
    login = home = performance = adm = FallbackPage()

# Layout principal con manejo de errores
try:
    app.layout = dbc.Container([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])
    logger.info("Layout principal configurado correctamente")
except Exception as e:
    logger.error(f"Error configurando layout: {str(e)}")
    app.layout = html.Div("Error de configuración")

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    prevent_initial_call=False
)
def display_page(pathname):
    """Routing con manejo de errores"""
    try:
        # Validar pathname
        if pathname is None:
            pathname = '/'
        
        logger.info(f"Navegando a: {pathname}")
        
        if pathname == '/login':
            return login.layout
        elif pathname == '/' or pathname == '':
            # Verificar autenticación
            try:
                if current_user.is_authenticated:
                    return home.layout
                else:
                    logger.info("Usuario no autenticado, redirigiendo a login")
                    return dcc.Location(href="/login", id="redirect-to-login")
            except Exception as auth_error:
                logger.error(f"Error verificando autenticación: {str(auth_error)}")
                return dcc.Location(href="/login", id="redirect-to-login")
                
        elif pathname == '/performance':
            try:
                if current_user.is_authenticated:
                    return performance.layout
                else:
                    return dcc.Location(href="/login", id="redirect-to-login")
            except Exception as auth_error:
                logger.error(f"Error en página performance: {str(auth_error)}")
                return dbc.Alert("Error cargando página de performance", color="danger")
                
        elif pathname == '/administrativo':
            try:
                if current_user.is_authenticated:
                    return adm.layout
                else:
                    return dcc.Location(href="/login", id="redirect-to-login")
            except Exception as auth_error:
                logger.error(f"Error en página administrativa: {str(auth_error)}")
                return dbc.Alert("Error cargando página administrativa", color="danger")
        else:
            logger.warning(f"Página no encontrada: {pathname}")
            return html.Div([
                dbc.Alert("404 - Página no encontrada", color="warning"),
                dbc.Button("Ir a Home", href="/", color="primary")
            ])
            
    except Exception as e:
        logger.error(f"Error en display_page: {str(e)}\n{traceback.format_exc()}")
        return dbc.Alert([
            html.H4("Error de navegación"),
            html.P(f"Ha ocurrido un error: {str(e)}"),
            dbc.Button("Ir a Login", href="/login", color="primary")
        ], color="danger")

@app.callback(
    Output("login-output", "children"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def login_callback(n_clicks, username, password):
    """Login con manejo de errores"""
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