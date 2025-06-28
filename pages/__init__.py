# pages/__init__.py
"""
Módulo de páginas del Dashboard Deportivo
Maneja la importación segura de todas las páginas
"""

import logging

# Configurar logging para el módulo pages
logger = logging.getLogger(__name__)

# Intentar importar todas las páginas con manejo de errores
login = None
home = None
performance = None
gps = None

def create_fallback_page(page_name, error_msg):
    """Crear página de fallback en caso de error"""
    try:
        from dash import html
        import dash_bootstrap_components as dbc
        
        class FallbackPage:
            layout = dbc.Container([
                dbc.Alert([
                    html.H4(f"Error cargando {page_name}"),
                    html.P(f"No se pudo cargar la página {page_name}."),
                    html.Hr(),
                    html.P(f"Error: {error_msg}", className="text-muted"),
                    dbc.Button("Ir a Login", href="/login", color="primary")
                ], color="danger", className="mt-5")
            ])
        
        return FallbackPage()
        
    except Exception as e:
        logger.critical(f"Error crítico creando fallback para {page_name}: {str(e)}")
        
        # Último recurso - página mínima
        class MinimalPage:
            layout = f"Error cargando {page_name}"
        
        return MinimalPage()

# Importar página login
try:
    from . import login
    logger.info("Página login importada correctamente")
except ImportError as e:
    logger.error(f"Error importando login: {str(e)}")
    login = create_fallback_page("Login", str(e))
except Exception as e:
    logger.error(f"Error general importando login: {str(e)}")
    login = create_fallback_page("Login", str(e))

# Importar página home
try:
    from . import home
    logger.info("Página home importada correctamente")
except ImportError as e:
    logger.error(f"Error importando home: {str(e)}")
    home = create_fallback_page("Home", str(e))
except Exception as e:
    logger.error(f"Error general importando home: {str(e)}")
    home = create_fallback_page("Home", str(e))

# Importar página performance
try:
    from . import performance
    logger.info("Página performance importada correctamente")
except ImportError as e:
    logger.error(f"Error importando performance: {str(e)}")
    performance = create_fallback_page("Performance", str(e))
except Exception as e:
    logger.error(f"Error general importando performance: {str(e)}")
    performance = create_fallback_page("Performance", str(e))

# Importar página gps
try:
    from . import gps
    logger.info("Página gps importada correctamente")
except ImportError as e:
    logger.error(f"Error importando gps: {str(e)}")
    gps = create_fallback_page("GPS", str(e))
except Exception as e:
    logger.error(f"Error general importando gps: {str(e)}")
    gps = create_fallback_page("GPS", str(e))

def validate_pages():
    """Validar que todas las páginas se importaron correctamente"""
    try:
        pages = {
            'login': login,
            'home': home,
            'performance': performance,
            'gps': gps
        }
        
        valid_pages = 0
        total_pages = len(pages)
        
        for page_name, page_module in pages.items():
            try:
                if page_module and hasattr(page_module, 'layout'):
                    logger.info(f"✓ Página {page_name}: OK")
                    valid_pages += 1
                else:
                    logger.warning(f"✗ Página {page_name}: Sin layout")
            except Exception as e:
                logger.error(f"✗ Página {page_name}: Error - {str(e)}")
        
        success_rate = (valid_pages / total_pages) * 100
        logger.info(f"Páginas válidas: {valid_pages}/{total_pages} ({success_rate:.1f}%)")
        
        return valid_pages == total_pages
        
    except Exception as e:
        logger.error(f"Error validando páginas: {str(e)}")
        return False

def get_pages_info():
    """Obtener información sobre el estado de las páginas"""
    try:
        info = {
            'login_available': login is not None and hasattr(login, 'layout'),
            'home_available': home is not None and hasattr(home, 'layout'),
            'performance_available': performance is not None and hasattr(performance, 'layout'),
            'gps_available': gps is not None and hasattr(gps, 'layout'),
            'all_pages_valid': validate_pages()
        }
        
        logger.info(f"Estado de páginas: {info}")
        return info
        
    except Exception as e:
        logger.error(f"Error obteniendo info de páginas: {str(e)}")
        return {"error": str(e)}

def recover_failed_pages():
    """Intentar recuperar páginas que fallaron"""
    global login, home, performance, gps
    
    try:
        logger.info("Intentando recuperar páginas fallidas...")
        
        # Lista de páginas a verificar
        pages_to_check = [
            ('login', login),
            ('home', home), 
            ('performance', performance),
            ('gps', gps)
        ]
        
        recovered = 0
        
        for page_name, page_module in pages_to_check:
            if not page_module or not hasattr(page_module, 'layout'):
                try:
                    logger.info(f"Intentando recuperar {page_name}...")
                    
                    if page_name == 'login':
                        from . import login
                        globals()['login'] = login
                    elif page_name == 'home':
                        from . import home
                        globals()['home'] = home
                    elif page_name == 'performance':
                        from . import performance
                        globals()['performance'] = performance
                    elif page_name == 'gps':
                        from . import gps
                        globals()['gps'] = gps
                    
                    logger.info(f"✓ Página {page_name} recuperada")
                    recovered += 1
                    
                except Exception as e:
                    logger.error(f"✗ No se pudo recuperar {page_name}: {str(e)}")
        
        logger.info(f"Páginas recuperadas: {recovered}")
        return recovered > 0
        
    except Exception as e:
        logger.error(f"Error en recuperación de páginas: {str(e)}")
        return False

# Ejecutar validación inicial
try:
    pages_info = get_pages_info()
    if not pages_info.get('all_pages_valid', False):
        logger.warning("No todas las páginas se cargaron correctamente")
        # Intentar recuperación automática
        recover_failed_pages()
    else:
        logger.info("Todas las páginas se cargaron correctamente")
except Exception as e:
    logger.error(f"Error en validación inicial de páginas: {str(e)}")

# Exportar páginas para compatibilidad
__all__ = ['login', 'home', 'performance', 'gps', 'validate_pages', 'get_pages_info', 'recover_failed_pages']