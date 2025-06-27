from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from flask import Flask
from flask_login import LoginManager, login_user, logout_user, login_required

from login_manager import get_user

# Flask base
server = Flask(__name__)
server.secret_key = 'super-secret-key'

# Login manager
login_manager = LoginManager()
login_manager.init_app(server)

@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)

# Dash app SIN use_pages
app = Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Importar páginas después de crear app
from pages import login

# Layout manual con routing
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/login':
        return login.layout
    else:
        return html.Div([
            html.H1("Página principal"),
            html.P("Bienvenido, estás logueado"),
            dbc.Button("Cerrar Sesión", id="logout-button", color="secondary"),
            html.Div(id="logout-output"),
            dcc.Link("Ir a Login", href="/login")
        ])

# Callback del login
@app.callback(
    Output("login-output", "children"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def login_callback(n_clicks, username, password):
    user = get_user(username)
    if user and password == user.password:
        login_user(user)
        return dcc.Location(href="/", id="redirect")
    return dbc.Alert("Credenciales incorrectas", color="danger")

# Callback del logout
@app.callback(
    Output("logout-output", "children"),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True
)
def logout_callback(n_clicks):
    logout_user()
    return dcc.Location(href="/login", id="redirect-logout")

if __name__ == "__main__":
    app.run(debug=True)

