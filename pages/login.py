import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from flask_login import login_user
import sys
import os

# Agregar la ruta raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from login_manager import get_user

layout = dbc.Container([
    html.H2("Login"),
    dbc.Input(id="username", placeholder="Usuario", type="text", className="mb-2"),
    dbc.Input(id="password", placeholder="Contraseña", type="password", className="mb-2"),
    dbc.Button("Entrar", id="login-button", color="primary", className="mb-2"),
    html.Div(id="login-output")
])