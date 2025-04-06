import dash
from dash import html, dcc
import pandas as pd
from datetime import datetime
from dash.dependencies import Input, Output

# Define Healthia Performance colors
COLORS = {
    'primary': '#00BCD4',      # Cyan (from logo)
    'secondary': '#00BCD4',    # Cyan (from logo)
    'background': '#FFFFFF',   # White
    'text': '#455A64',         # Dark slate
}

# Sample dates for the dropdown
dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='ME')

def create_nav_circle(text, href, is_selected):
    # Split text if it contains parentheses
    if "(" in text:
        main_text, sub_text = text.split("(")
        sub_text = "(" + sub_text
    else:
        main_text = text
        sub_text = ""
    
    return html.A(
        html.Div([
            html.Div(main_text, style={
                "fontSize": "20px",
                "fontWeight": "bold",
                "color": COLORS['text'],
                "marginBottom": "5px",
                "lineHeight": "1.2",
                "textDecoration": "none"
            }),
            html.Div(sub_text, style={
                "fontSize": "16px",
                "color": COLORS['text'],
                "opacity": "0.8",
                "lineHeight": "1.2",
                "textDecoration": "none"
            }) if sub_text else None
        ], style={
            "textAlign": "center",
            "width": "100%",
            "padding": "10px",
            "textDecoration": "none"
        }),
        href=href,
        style={
            "width": "150px",
            "height": "150px",
            "borderRadius": "50%",
            "border": f"12px solid {COLORS['secondary']}",
            "backgroundColor": COLORS['background'],
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "margin": "0 15px",
            "cursor": "pointer",
            "boxShadow": '0 0 60px rgba(0, 188, 212, 0.5), 0 0 90px rgba(0, 188, 212, 0.4), 0 0 120px rgba(0, 188, 212, 0.3)' if is_selected else '0 0 35px rgba(0, 188, 212, 0.21), 0 0 25px rgba(0, 188, 212, 0.14), 0 0 15px rgba(0, 188, 212, 0.105)',
            "transform": "scale(1.08)" if is_selected else "scale(1)",
            "color": COLORS['text'],
            "backgroundImage": "linear-gradient(to bottom, rgba(255,255,255,0.9), rgba(255,255,255,1))",
            "transition": "all 0.3s ease",
            "zIndex": "1000" if is_selected else "1",
            "textDecoration": "none"
        },
        className="nav-circle"
    )

def create_navigation_dashboard(pathname='/'):
    return html.Div([
        # Header with logo and selection dropdowns
        html.Div([
            # Left side: Logo
            html.Div([
                html.Img(
                    src="/assets/healthia_performance_logo.png",
                    style={
                        "height": "220px",
                        "marginRight": "20px"
                    }
                )
            ], style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "flex-start",
                "flex": "1"
            }),

            # Center: Title
            html.Div([
                html.H1("Athlete Dashboard", style={
                    "color": COLORS['text'],
                    "fontSize": "36px",
                    "fontWeight": "bold",
                    "margin": "0",
                    "fontFamily": "Helvetica, Arial, sans-serif",
                    "letterSpacing": "0.5px",
                    "textAlign": "center"
                })
            ], style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "flex": "1",
                "position": "relative",
                "left": "-50px"  # Adjust this value to fine-tune the centering
            }),

            # Right side: Athlete and Date Selection
            html.Div([
                dcc.Store(id='selected-athlete', storage_type='session'),
                dcc.Store(id='selected-date', storage_type='session'),
                html.Div([
                    dcc.Dropdown(
                        id='athlete-dropdown',
                        options=[
                            {'label': 'Athlete 1', 'value': 'athlete1'},
                            {'label': 'Athlete 2', 'value': 'athlete2'},
                            {'label': 'Athlete 3', 'value': 'athlete3'}
                        ],
                        placeholder="Select an Athlete",
                        persistence=True,
                        persistence_type='session',
                        style={
                            "width": "200px",
                            "marginRight": "20px",
                            "fontFamily": "Helvetica, Arial, sans-serif",
                            "borderRadius": "8px",
                            "border": f"2px solid {COLORS['secondary']}",
                            "boxShadow": "0 0 35px rgba(0, 188, 212, 0.21), 0 0 25px rgba(0, 188, 212, 0.14), 0 0 15px rgba(0, 188, 212, 0.105)",
                            "backgroundColor": "white",
                            "backgroundImage": "linear-gradient(to bottom, rgba(255,255,255,0.9), rgba(255,255,255,1))",
                            "transition": "all 0.3s ease"
                        }
                    ),
                    dcc.Dropdown(
                        id='date-dropdown',
                        options=[{'label': date.strftime('%d/%m/%Y'), 'value': date} for date in dates],
                        value=dates[-1],
                        persistence=True,
                        persistence_type='session',
                        style={
                            "width": "200px",
                            "fontFamily": "Helvetica, Arial, sans-serif",
                            "borderRadius": "8px",
                            "border": f"2px solid {COLORS['secondary']}",
                            "boxShadow": "0 0 35px rgba(0, 188, 212, 0.21), 0 0 25px rgba(0, 188, 212, 0.14), 0 0 15px rgba(0, 188, 212, 0.105)",
                            "backgroundColor": "white",
                            "backgroundImage": "linear-gradient(to bottom, rgba(255,255,255,0.9), rgba(255,255,255,1))",
                            "transition": "all 0.3s ease"
                        }
                    )
                ], style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "flex-end"
                })
            ], style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "flex-end",
                "flex": "1"
            })
        ], style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
            "marginBottom": "40px",
            "padding": "20px",
            "backgroundColor": "white",
            "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
            "borderRadius": "12px",
            "position": "relative"
        }),

        # Navigation Circles - Single Row
        html.Div([
            create_nav_circle("Capacity / Motor Control", "/capacity", pathname == "/capacity"),
            create_nav_circle("Strength / Hypertrophy", "/strength", pathname == "/strength"),
            create_nav_circle("Power / RFD (Slow SSC)", "/power", pathname == "/power"),
            create_nav_circle("Reactive Strength (Fast SSC)", "/reactive", pathname == "/reactive"),
            create_nav_circle("Linear Running", "/linear", pathname == "/linear"),
            create_nav_circle("Change of Direction", "/direction", pathname == "/direction")
        ], style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "flexWrap": "nowrap",
            "gap": "20px",
            "maxWidth": "100%",
            "margin": "0 auto",
            "padding": "20px",
            "overflowX": "auto",
            "backgroundColor": "white",
            "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
            "borderRadius": "12px"
        })
    ], style={
        "backgroundColor": "#f5f5f5",
        "minHeight": "100vh",
        "padding": "40px 20px"
    }) 