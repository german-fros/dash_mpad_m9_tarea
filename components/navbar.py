from dash import html, dcc
import dash_bootstrap_components as dbc
import logging

# Configurar logging específico para navbar
logger = logging.getLogger(__name__)

def create_navbar():
    """Crear navbar con manejo robusto de errores"""
    try:
        # Intentar crear navbar completo
        navbar = dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
                dbc.NavItem(dbc.NavLink("Performance", href="/performance", active="exact")),
                dbc.NavItem(dbc.NavLink("GPS", href="/gps", active="exact")),
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("Perfil", header=True),
                        dbc.DropdownMenuItem(divider=True),
                        dbc.DropdownMenuItem("Cerrar Sesión", id="navbar-logout", n_clicks=0),
                    ],
                    nav=True,
                    in_navbar=True,
                    label="Usuario",
                ),
            ],
            brand="Dashboard Deportivo",
            brand_href="/",
            color="primary",
            dark=True,
            className="mb-4"
        )
        
        # Validar que el navbar se creó correctamente
        if not navbar or not hasattr(navbar, 'children'):
            raise ValueError("Navbar no se creó correctamente")
        
        logger.info("Navbar completo creado exitosamente")
        return navbar
        
    except Exception as e:
        logger.error(f"Error creando navbar completo: {str(e)}")
        return create_fallback_navbar()

def create_fallback_navbar():
    """Crear navbar simplificado como fallback"""
    try:
        navbar = dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="/")),
                dbc.NavItem(dbc.NavLink("Performance", href="/performance")),
                dbc.NavItem(dbc.NavLink("GPS", href="/gps")),
                dbc.NavItem(dbc.NavLink("Logout", href="/login")),
            ],
            brand="Dashboard Deportivo",
            brand_href="/",
            color="primary",
            dark=True,
            className="mb-4"
        )
        
        logger.warning("Usando navbar de fallback (sin dropdown)")
        return navbar
        
    except Exception as e:
        logger.error(f"Error creando navbar de fallback: {str(e)}")
        return create_minimal_navbar()

def create_minimal_navbar():
    """Crear navbar mínimo como último recurso"""
    try:
        navbar = html.Div([
            html.Nav([
                html.Div([
                    html.A("Dashboard Deportivo", href="/", 
                          style={"color": "white", "text-decoration": "none", "font-weight": "bold"}),
                    html.Div([
                        html.A("Home", href="/", style={"color": "white", "margin": "0 10px"}),
                        html.A("Performance", href="/performance", style={"color": "white", "margin": "0 10px"}),
                        html.A("GPS", href="/gps", style={"color": "white", "margin": "0 10px"}),
                        html.A("Logout", href="/login", style={"color": "white", "margin": "0 10px"}),
                    ], style={"display": "flex"})
                ], style={
                    "display": "flex", 
                    "justify-content": "space-between", 
                    "align-items": "center",
                    "padding": "10px 20px"
                })
            ], style={
                "background-color": "#007bff", 
                "margin-bottom": "20px"
            })
        ])
        
        logger.warning("Usando navbar mínimo (HTML básico)")
        return navbar
        
    except Exception as e:
        logger.critical(f"Error crítico creando navbar mínimo: {str(e)}")
        return create_emergency_navbar()

def create_emergency_navbar():
    """Navbar de emergencia - último recurso absoluto"""
    try:
        return html.Div([
            html.Div([
                html.H3("Dashboard Deportivo", style={"color": "white", "margin": "0"}),
                html.P("Navegación: ", style={"color": "white", "margin": "5px 0"}),
                html.A("Home", href="/", style={"color": "lightblue", "margin-right": "10px"}),
                html.A("Performance", href="/performance", style={"color": "lightblue", "margin-right": "10px"}),
                html.A("GPS", href="/gps", style={"color": "lightblue", "margin-right": "10px"}),
                html.A("Login", href="/login", style={"color": "lightblue"})
            ], style={
                "background-color": "#dc3545",
                "padding": "15px",
                "margin-bottom": "20px",
                "text-align": "center"
            })
        ])
    except Exception as e:
        logger.critical(f"Error crítico en navbar de emergencia: {str(e)}")
        # Último recurso absoluto
        return html.Div([
            html.P("Error del sistema de navegación"),
            html.A("Ir a Home", href="/")
        ], style={"padding": "10px", "background-color": "red", "color": "white"})

def validate_navbar(navbar):
    """Validar que el navbar funciona correctamente"""
    try:
        if not navbar:
            logger.error("Navbar es None")
            return False
        
        # Convertir a string para verificar contenido
        navbar_str = str(navbar)
        
        # Verificar elementos críticos
        required_elements = ["Home", "Performance", "GPS", "Dashboard"]
        for element in required_elements:
            if element not in navbar_str:
                logger.warning(f"Elemento '{element}' no encontrado en navbar")
                return False
        
        # Verificar que tiene estructura válida
        if not hasattr(navbar, 'children') and 'href' not in navbar_str:
            logger.error("Navbar no tiene estructura válida")
            return False
        
        logger.info("Validación de navbar exitosa")
        return True
        
    except Exception as e:
        logger.error(f"Error validando navbar: {str(e)}")
        return False

def get_navbar_info(navbar):
    """Obtener información del navbar para debugging"""
    try:
        info = {
            "navbar_type": type(navbar).__name__,
            "has_children": hasattr(navbar, 'children'),
            "is_valid": validate_navbar(navbar)
        }
        
        # Intentar obtener más detalles
        try:
            navbar_str = str(navbar)
            info["contains_dropdown"] = "DropdownMenu" in navbar_str
            info["contains_brand"] = "Dashboard Deportivo" in navbar_str
            info["length"] = len(navbar_str)
        except Exception:
            info["details_error"] = True
        
        logger.info(f"Info navbar: {info}")
        return info
        
    except Exception as e:
        logger.error(f"Error obteniendo info de navbar: {str(e)}")
        return {"error": str(e)}

def test_navbar_creation():
    """Función de prueba para verificar creación de navbar"""
    try:
        logger.info("=== INICIANDO PRUEBA DE NAVBAR ===")
        
        # Probar creación principal
        navbar = create_navbar()
        navbar_info = get_navbar_info(navbar)
        
        if validate_navbar(navbar):
            logger.info("✓ Navbar principal: OK")
            return navbar, "principal"
        else:
            logger.warning("✗ Navbar principal: FALLO")
            
        # Probar fallback
        navbar_fallback = create_fallback_navbar()
        if validate_navbar(navbar_fallback):
            logger.info("✓ Navbar fallback: OK")
            return navbar_fallback, "fallback"
        else:
            logger.warning("✗ Navbar fallback: FALLO")
            
        # Probar mínimo
        navbar_minimal = create_minimal_navbar()
        if validate_navbar(navbar_minimal):
            logger.info("✓ Navbar mínimo: OK")
            return navbar_minimal, "minimal"
        else:
            logger.warning("✗ Navbar mínimo: FALLO")
            
        # Usar emergencia
        navbar_emergency = create_emergency_navbar()
        logger.warning("Usando navbar de emergencia")
        return navbar_emergency, "emergency"
        
    except Exception as e:
        logger.critical(f"Error crítico en prueba de navbar: {str(e)}")
        return html.Div("Error de navegación"), "error"

def safe_create_navbar():
    """Versión segura que garantiza devolver un navbar funcional"""
    try:
        navbar, navbar_type = test_navbar_creation()
        logger.info(f"Navbar creado exitosamente - Tipo: {navbar_type}")
        return navbar
    except Exception as e:
        logger.critical(f"Error crítico en safe_create_navbar: {str(e)}")
        # Último recurso absoluto
        return html.Div([
            html.H4("Error de Navegación"),
            html.A("Home", href="/", style={"margin": "10px"}),
            html.A("Login", href="/login", style={"margin": "10px"})
        ], style={"padding": "20px", "background-color": "#f8d7da"})

# Función principal exportada
def create_navbar_safe():
    """Función principal que siempre devuelve un navbar válido"""
    return safe_create_navbar()

# Mantener compatibilidad con código existente
def get_navbar():
    """Función de compatibilidad"""
    return create_navbar()

# Función de diagnóstico
def diagnose_navbar():
    """Diagnóstico completo del sistema de navbar"""
    try:
        print("=== DIAGNÓSTICO DE NAVBAR ===")
        
        # Probar cada nivel
        levels = [
            ("Principal", create_navbar),
            ("Fallback", create_fallback_navbar),
            ("Mínimo", create_minimal_navbar),
            ("Emergencia", create_emergency_navbar)
        ]
        
        for level_name, level_func in levels:
            try:
                navbar = level_func()
                is_valid = validate_navbar(navbar)
                status = "✓ OK" if is_valid else "✗ FALLO"
                print(f"{level_name}: {status}")
            except Exception as e:
                print(f"{level_name}: ✗ ERROR - {str(e)}")
        
        print("=== FIN DIAGNÓSTICO ===")
        return True
        
    except Exception as e:
        print(f"Error en diagnóstico: {str(e)}")
        return False