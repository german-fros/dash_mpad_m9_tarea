# login_manager.py
from flask_login import UserMixin

# Usuario único hardcodeado
class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "admin"
        self.password = "admin"

    def get_id(self):
        return self.id

# Diccionario simulado de usuarios
users = {
    "admin": User(id="admin")
}

def get_user(username):
    return users.get(username)
