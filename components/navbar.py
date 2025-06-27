from dash import html, dcc
import dash_bootstrap_components as dbc

def create_navbar():
    return dbc.NavbarSimple(
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