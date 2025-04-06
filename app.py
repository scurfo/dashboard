import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime
from NavigationDashboard import create_navigation_dashboard
from MetricPage import create_metric_page

# Add custom CSS for animations
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True,
    assets_folder='assets',
    index_string='''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                @keyframes slideIn {
                    from { transform: translateX(-100px); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                
                .page-content {
                    animation: fadeIn 0.5s ease-out;
                }
                
                .nav-circle {
                    transition: all 0.3s ease !important;
                    transform-origin: center !important;
                }
                
                .nav-circle:hover {
                    transform: scale(1.08) !important;
                    box-shadow: 0 0 30px rgba(0, 188, 212, 0.4), 0 0 50px rgba(0, 188, 212, 0.3), 0 0 70px rgba(0, 188, 212, 0.2) !important;
                    z-index: 1000 !important;
                }
                
                .home-button {
                    transition: all 0.3s ease !important;
                    transform-origin: center !important;
                }
                
                .home-button:hover {
                    transform: scale(1.08) !important;
                    box-shadow: 0 0 30px rgba(0, 188, 212, 0.4), 0 0 50px rgba(0, 188, 212, 0.3), 0 0 70px rgba(0, 188, 212, 0.2) !important;
                    z-index: 1000 !important;
                }

                /* Add a smooth transition for the dropdowns */
                .Select-control {
                    transition: all 0.3s ease !important;
                }

                .Select-control:hover {
                    transform: scale(1.03) !important;
                    box-shadow: 0 0 35px rgba(0, 188, 212, 0.21), 0 0 25px rgba(0, 188, 212, 0.14), 0 0 15px rgba(0, 188, 212, 0.105) !important;
                }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''
)

server = app.server  # This is needed for production deployment

# Define the layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', className='page-content')
])

# Callback to handle routing
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if not pathname:
        pathname = '/'
        
    if pathname == '/':
        return create_navigation_dashboard(pathname)
    elif pathname == '/capacity':
        return create_metric_page("Capacity / Motor Control", "capacity")
    elif pathname == '/strength':
        return create_metric_page("Strength / Hypertrophy", "strength")
    elif pathname == '/power':
        return create_metric_page("Power / RFD", "power")
    elif pathname == '/reactive':
        return create_metric_page("Reactive Strength", "reactive")
    elif pathname == '/linear':
        return create_metric_page("Linear Running", "linear")
    elif pathname == '/direction':
        return create_metric_page("Change of Direction", "direction")
    else:
        return create_navigation_dashboard(pathname)

if __name__ == '__main__':
    # Development settings
    app.run(debug=False, host='0.0.0.0', port=8050)
else:
    # Production settings
    server = app.server  # This is for WSGI servers like gunicorn 