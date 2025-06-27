from dash import Dash, dcc, html, page_container
import dash_bootstrap_components as dbc
from flask import Flask
from flask_login import LoginManager

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

# Dash app
app = Dash(
    __name__,
    server=server,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Layout base (provisorio, sin autenticación aún)
app.layout = dbc.Container(
    [
        dcc.Location(id='url'),
        page_container
    ],
    fluid=True
)

if __name__ == "__main__":
    app.run_server(debug=True)