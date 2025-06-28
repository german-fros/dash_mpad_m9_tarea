# login_manager.py
from flask_login import UserMixin
import logging
import hashlib
import secrets
from typing import Optional, Dict, Any

# Configurar logging específico para autenticación
logger = logging.getLogger(__name__)

class User(UserMixin):
    """Clase User con validación y manejo de errores"""
    
    def __init__(self, id: str, name: str = None, password: str = None):
        try:
            # Validar parámetros obligatorios
            if not id or not isinstance(id, str) or len(id.strip()) == 0:
                raise ValueError("ID de usuario no puede estar vacío")
            
            self.id = id.strip()
            self.name = name or id
            self.password = password
            self.is_active = True
            
            logger.info(f"Usuario {self.id} creado correctamente")
            
        except Exception as e:
            logger.error(f"Error creando usuario: {str(e)}")
            raise ValueError(f"Error inicializando usuario: {str(e)}")

    def get_id(self) -> str:
        """Obtener ID del usuario con validación"""
        try:
            if not hasattr(self, 'id') or not self.id:
                raise AttributeError("Usuario no tiene ID válido")
            return str(self.id)
        except Exception as e:
            logger.error(f"Error obteniendo ID de usuario: {str(e)}")
            return None

    def is_authenticated(self) -> bool:
        """Verificar si el usuario está autenticado"""
        try:
            return self.is_active and hasattr(self, 'id') and self.id is not None
        except Exception as e:
            logger.error(f"Error verificando autenticación: {str(e)}")
            return False

    def is_anonymous(self) -> bool:
        """Verificar si el usuario es anónimo"""
        return False

    def get_active(self) -> bool:
        """Verificar si el usuario está activo"""
        try:
            return getattr(self, 'is_active', False)
        except Exception as e:
            logger.error(f"Error verificando estado activo: {str(e)}")
            return False

    def validate_password(self, password: str) -> bool:
        """Validar contraseña con manejo de errores"""
        try:
            if not password or not isinstance(password, str):
                logger.warning(f"Intento de validación con contraseña inválida para usuario {self.id}")
                return False
            
            if not hasattr(self, 'password') or not self.password:
                logger.error(f"Usuario {self.id} no tiene contraseña configurada")
                return False
            
            # Comparación segura de contraseñas
            is_valid = secrets.compare_digest(password.strip(), self.password)
            
            if is_valid:
                logger.info(f"Validación de contraseña exitosa para usuario {self.id}")
            else:
                logger.warning(f"Validación de contraseña fallida para usuario {self.id}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validando contraseña para usuario {self.id}: {str(e)}")
            return False

    def __repr__(self) -> str:
        """Representación segura del usuario (sin mostrar contraseña)"""
        try:
            return f"<User {self.id}>"
        except Exception:
            return "<User [Error]>"

class UserManager:
    """Gestor de usuarios con manejo de errores y seguridad"""
    
    def __init__(self):
        try:
            self.users: Dict[str, User] = {}
            self._initialize_default_users()
            logger.info("UserManager inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando UserManager: {str(e)}")
            self.users = {}

    def _initialize_default_users(self):
        """Inicializar usuarios por defecto con manejo de errores"""
        try:
            # Usuario admin por defecto (requerido por la tarea)
            admin_user = User(id="admin", name="Administrador", password="admin")
            self.users["admin"] = admin_user
            
            logger.info("Usuarios por defecto inicializados")
            
        except Exception as e:
            logger.error(f"Error inicializando usuarios por defecto: {str(e)}")
            # Crear usuario admin básico como fallback
            try:
                fallback_user = User("admin")
                fallback_user.password = "admin"
                self.users["admin"] = fallback_user
                logger.info("Usuario admin fallback creado")
            except Exception as fallback_error:
                logger.critical(f"Error crítico creando usuario fallback: {str(fallback_error)}")

    def get_user(self, username: str) -> Optional[User]:
        """Obtener usuario con validación y manejo de errores"""
        try:
            # Validar input
            if not username or not isinstance(username, str):
                logger.warning("Intento de obtener usuario con username inválido")
                return None
            
            username = username.strip().lower()
            
            if len(username) == 0:
                logger.warning("Intento de obtener usuario con username vacío")
                return None
            
            # Buscar usuario
            user = self.users.get(username)
            
            if user:
                logger.info(f"Usuario {username} encontrado")
                # Verificar que el usuario esté en estado válido
                if not hasattr(user, 'id') or not user.id:
                    logger.error(f"Usuario {username} en estado inválido")
                    return None
            else:
                logger.warning(f"Usuario {username} no encontrado")
            
            return user
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario {username}: {str(e)}")
            return None

    def add_user(self, username: str, password: str, name: str = None) -> bool:
        """Agregar nuevo usuario con validación"""
        try:
            # Validar parámetros
            if not username or not password:
                logger.warning("Intento de agregar usuario con datos incompletos")
                return False
            
            username = username.strip().lower()
            
            if username in self.users:
                logger.warning(f"Intento de agregar usuario existente: {username}")
                return False
            
            # Crear usuario
            new_user = User(id=username, name=name, password=password.strip())
            self.users[username] = new_user
            
            logger.info(f"Usuario {username} agregado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error agregando usuario {username}: {str(e)}")
            return False

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Autenticar usuario con validación completa"""
        try:
            # Obtener usuario
            user = self.get_user(username)
            if not user:
                return None
            
            # Validar contraseña
            if user.validate_password(password):
                logger.info(f"Autenticación exitosa para {username}")
                return user
            else:
                logger.warning(f"Autenticación fallida para {username}")
                return None
                
        except Exception as e:
            logger.error(f"Error en autenticación para {username}: {str(e)}")
            return None

    def get_user_count(self) -> int:
        """Obtener número de usuarios registrados"""
        try:
            return len(self.users)
        except Exception as e:
            logger.error(f"Error obteniendo conteo de usuarios: {str(e)}")
            return 0

# Instancia global del gestor de usuarios
try:
    user_manager = UserManager()
    logger.info("Gestor de usuarios global inicializado")
except Exception as e:
    logger.critical(f"Error crítico inicializando gestor de usuarios: {str(e)}")
    # Crear instancia de emergencia
    user_manager = None

def get_user(username: str) -> Optional[User]:
    """Función de compatibilidad con manejo de errores"""
    try:
        if user_manager is None:
            logger.error("Gestor de usuarios no disponible")
            return None
        
        return user_manager.get_user(username)
        
    except Exception as e:
        logger.error(f"Error en get_user para {username}: {str(e)}")
        return None

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Función de autenticación con manejo de errores"""
    try:
        if user_manager is None:
            logger.error("Gestor de usuarios no disponible para autenticación")
            return None
        
        return user_manager.authenticate_user(username, password)
        
    except Exception as e:
        logger.error(f"Error en authenticate_user para {username}: {str(e)}")
        return None

# Función de verificación del sistema
def verify_system() -> bool:
    """Verificar que el sistema de autenticación esté funcionando"""
    try:
        # Verificar que el gestor esté disponible
        if user_manager is None:
            logger.error("Sistema de autenticación no disponible")
            return False
        
        # Verificar usuario admin
        admin = get_user("admin")
        if not admin:
            logger.error("Usuario admin no disponible")
            return False
        
        # Verificar autenticación admin
        auth_test = authenticate_user("admin", "admin")
        if not auth_test:
            logger.error("Autenticación admin falló")
            return False
        
        logger.info("Verificación del sistema de autenticación exitosa")
        return True
        
    except Exception as e:
        logger.error(f"Error en verificación del sistema: {str(e)}")
        return False