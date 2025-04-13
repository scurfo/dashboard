import dash
from dash import dcc, html, Input, Output

# Import page functions from your files
from DashboardBase import create_metric_page
from NavigationDashboard import create_navigation_dashboard

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Main layout with routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Page router
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname in ["/capacity", "/strength", "/power", "/reactive", "/linear", "/direction"]:
        return create_metric_page(title=pathname.strip("/"), active_page=pathname.strip("/"))
    else:
        return create_navigation_dashboard(pathname)

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
