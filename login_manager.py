# login_manager.py
from flask_login import UserMixin
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "admin"
        self.password = "admin"

    def get_id(self):
        return self.id

# Diccionario simple de usuarios
users = {
    "admin": User(id="admin")
}

def get_user(username):
    """Obtener usuario del diccionario"""
    try:
        if not username:
            logger.warning("Username vacío")
            return None
        
        user = users.get(username.strip())
        
        if user:
            logger.info(f"Usuario {username} encontrado")
        else:
            logger.warning(f"Usuario {username} no encontrado")
        
        return user
    except Exception as e:
        logger.error(f"Error obteniendo usuario {username}: {str(e)}")
        return None

def authenticate_user(username, password):
    """Función de compatibilidad"""
    try:
        user = get_user(username)
        if user and password == user.password:
            return user
        return None
    except Exception as e:
        logger.error(f"Error en authenticate_user: {str(e)}")
        return None