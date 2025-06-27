# pages/login.py
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from flask_login import login_user

from login_manager import get_user

dash.register_page(__name__, path="/login", name="Login")

layout = dbc.Container([
    html.H2("Login"),
    dbc.Input(id="username", placeholder="Usuario", type="text", className="mb-2"),
    dbc.Input(id="password", placeholder="Contraseña", type="password", className="mb-2"),
    dbc.Button("Entrar", id="login-button", color="primary", className="mb-2"),
    html.Div(id="login-output")
])

@dash.callback(
    Output("login-output", "children"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def login(n_clicks, username, password):
    user = get_user(username)
    if user and password == user.password:
        login_user(user)
        return dcc.Location(href="/", id="redirect")
    return dbc.Alert("Credenciales incorrectas", color="danger")
