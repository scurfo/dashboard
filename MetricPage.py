import dash
from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from datetime import datetime
import os
from NavigationDashboard import create_nav_circle

# Define Healthia Performance colors
COLORS = {
    'primary': '#455A64',      # Dark slate
    'secondary': '#00BCD4',    # Bright cyan/turquoise
    'background': '#FFFFFF',   # White
    'text': '#455A64',         # Dark slate
}

def create_donut_graph(value_left, value_right, title_left, title_right):
    return {
        'data': [
            {
                'values': [value_left, 100-value_left],
                'type': 'pie',
                'hole': .7,
                'name': title_left,
                'marker': {'colors': [COLORS['secondary'], '#E0E0E0']},
                'domain': {'x': [0, 0.48]},
                'textinfo': 'none',
                'hoverinfo': 'none'
            },
            {
                'values': [value_right, 100-value_right],
                'type': 'pie',
                'hole': .7,
                'name': title_right,
                'marker': {'colors': [COLORS['primary'], '#E0E0E0']},
                'domain': {'x': [0.52, 1]},
                'textinfo': 'none',
                'hoverinfo': 'none'
            }
        ],
        'layout': {
            'annotations': [
                # Left percentage
                {
                    'text': f'{value_left}%',
                    'x': 0.24,
                    'y': 0.5,
                    'font': {'size': 48, 'color': COLORS['secondary']},
                    'showarrow': False,
                    'xanchor': 'center',
                    'yanchor': 'middle'
                },
                # Right percentage
                {
                    'text': f'{value_right}%',
                    'x': 0.76,
                    'y': 0.5,
                    'font': {'size': 48, 'color': COLORS['primary']},
                    'showarrow': False,
                    'xanchor': 'center',
                    'yanchor': 'middle'
                }
            ],
            'showlegend': False,
            'margin': {'t': 30, 'b': 30, 'l': 30, 'r': 30},
            'height': 350
        }
    }

def create_metric_page(title, active_page):
    # Return the capacity page if active_page is "capacity"
    if active_page == "capacity":
        return create_capacity_page(active_page)

    # Sample data for other metric types
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='ME')
    data = pd.DataFrame({
        'Date': dates,
        'Left': np.random.normal(100, 10, len(dates)),
        'Right': np.random.normal(100, 10, len(dates))
    })
    
    # Create line graphs with glow effect
    def create_line_graph(title, yaxis_title, target=None):
        # Get the most recent test date
        latest_date = data['Date'].max()
        test_date = latest_date.strftime('%d/%m/%Y')
        
        # Create line graph
        fig_line = go.Figure()
        
        # Add glow effect for left
        for i in range(5, 0, -1):
            fig_line.add_trace(go.Scatter(
                x=data['Date'],
                y=data['Left'],
                name='',
                line=dict(color=COLORS['secondary'], width=2*i),
                opacity=0.1,
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add main left trace
        fig_line.add_trace(go.Scatter(
            x=data['Date'],
            y=data['Left'],
            name='Left',
            line=dict(color=COLORS['secondary'], width=2),
            hovertemplate='%{y:.1f}'
        ))
        
        # Add glow effect for right
        for i in range(5, 0, -1):
            fig_line.add_trace(go.Scatter(
                x=data['Date'],
                y=data['Right'],
                name='',
                line=dict(color=COLORS['primary'], width=2*i),
                opacity=0.1,
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add main right trace
        fig_line.add_trace(go.Scatter(
            x=data['Date'],
            y=data['Right'],
            name='Right',
            line=dict(color=COLORS['primary'], width=2),
            hovertemplate='%{y:.1f}'
        ))
        
        fig_line.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title=yaxis_title,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=40, r=40, t=40, b=40),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Helvetica, Arial, sans-serif"),
            # Add responsive sizing
            autosize=True,
            # Improve touch interaction
            dragmode='pan'
        )
        
        if target:
            fig_line.add_hline(y=target, line_width=2, line_color=COLORS['primary'], opacity=0.5)
        
        # Create donut charts for target achievement if target is specified
        donut_charts = []
        if target:
            # Calculate percentages for left and right
            left_percent = min(100, (data['Left'].iloc[-1] / target) * 100)
            right_percent = min(100, (data['Right'].iloc[-1] / target) * 100)
            
            # Create left donut
            fig_left = go.Figure()
            fig_left.add_trace(go.Pie(
                values=[left_percent, 100-left_percent],
                hole=0.7,
                marker_colors=[COLORS['secondary'], 'rgba(0, 188, 212, 0.2)'],
                showlegend=False,
                textinfo='none',
                hoverinfo='none'
            ))
            fig_left.update_layout(
                title="Left",
                showlegend=False,
                margin=dict(t=30, b=30, l=30, r=30),
                height=200,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Helvetica, Arial, sans-serif"),
                # Add responsive sizing
                autosize=True,
                # Improve touch interaction
                dragmode='pan'
            )
            fig_left.add_annotation(
                text=f"{left_percent:.0f}%",
                x=0.5,
                y=0.5,
                font=dict(size=36, color=COLORS['secondary']),
                showarrow=False
            )
            
            # Create right donut
            fig_right = go.Figure()
            fig_right.add_trace(go.Pie(
                values=[right_percent, 100-right_percent],
                hole=0.7,
                marker_colors=[COLORS['primary'], 'rgba(69, 90, 100, 0.2)'],
                showlegend=False,
                textinfo='none',
                hoverinfo='none'
            ))
            fig_right.update_layout(
                title="Right",
                showlegend=False,
                margin=dict(t=30, b=30, l=30, r=30),
                height=200,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Helvetica, Arial, sans-serif"),
                # Add responsive sizing
                autosize=True,
                # Improve touch interaction
                dragmode='pan'
            )
            fig_right.add_annotation(
                text=f"{right_percent:.0f}%",
                x=0.5,
                y=0.5,
                font=dict(size=36, color=COLORS['primary']),
                showarrow=False
            )
            
            donut_charts = [
                dcc.Graph(
                    id=f'donut-left-{title.lower().replace(" ", "-")}',
                    figure=fig_left,
                    style={'height': '200px', 'marginBottom': '10px'},
                    config={'responsive': True, 'displayModeBar': False}
                ),
                dcc.Graph(
                    id=f'donut-right-{title.lower().replace(" ", "-")}',
                    figure=fig_right,
                    style={'height': '200px', 'marginBottom': '10px'},
                    config={'responsive': True, 'displayModeBar': False}
                )
            ]
        
        return html.Div([
            html.Div([
                dcc.Graph(
                    id=f'graph-{title.lower().replace(" ", "-")}',
                    figure=fig_line,
                    style={'height': '400px', 'marginBottom': '10px'},
                    config={'responsive': True, 'displayModeBar': False}
                ),
                html.Div(f"Last tested: {test_date}", style={
                    'textAlign': 'center',
                    'color': COLORS['text'],
                    'fontSize': '14px',
                    'marginBottom': '20px',
                    'fontFamily': 'Helvetica, Arial, sans-serif',
                    'fontWeight': 'normal',
                    'opacity': '0.8'
                })
            ], style={
                'width': '70%',
                'display': 'inline-block',
                '@media (max-width: 768px)': {
                    'width': '100%'
                }
            }),
            html.Div(donut_charts, style={
                'width': '30%',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'paddingTop': '40px',
                '@media (max-width: 768px)': {
                    'width': '100%',
                    'display': 'flex',
                    'flexDirection': 'row',
                    'justifyContent': 'space-around',
                    'paddingTop': '20px'
                }
            })
        ], style={
            'display': 'flex',
            'flexWrap': 'wrap',
            '@media (max-width: 768px)': {
                'flexDirection': 'column'
            }
        })

    # Create donut charts for power and reactive strength
    def create_donut_chart(title, value_left, value_right):
        # Get the most recent test date
        latest_date = data['Date'].max()
        test_date = latest_date.strftime('%d/%m/%Y')
        
        fig = go.Figure()
        
        # Add left donut
        fig.add_trace(go.Pie(
            values=[value_left, 100-value_left],
            hole=0.7,
            marker_colors=[COLORS['secondary'], 'rgba(0, 188, 212, 0.2)'],
            showlegend=False,
            textinfo='none',
            hoverinfo='none',
            domain={'x': [0, 0.48]}
        ))
        
        # Add right donut
        fig.add_trace(go.Pie(
            values=[value_right, 100-value_right],
            hole=0.7,
            marker_colors=[COLORS['primary'], 'rgba(69, 90, 100, 0.2)'],
            showlegend=False,
            textinfo='none',
            hoverinfo='none',
            domain={'x': [0.52, 1]}
        ))
        
        # Add annotations for percentages
        fig.add_annotation(
            text=f"{value_left}%",
            x=0.24,
            y=0.5,
            font=dict(size=48, color=COLORS['secondary']),
            showarrow=False
        )
        
        fig.add_annotation(
            text=f"{value_right}%",
            x=0.76,
            y=0.5,
            font=dict(size=48, color=COLORS['primary']),
            showarrow=False
        )
        
        fig.update_layout(
            title=title,
            showlegend=False,
            margin=dict(t=30, b=30, l=30, r=30),
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Helvetica, Arial, sans-serif")
        )
        
        return html.Div([
            dcc.Graph(
                id=f'donut-{title.lower().replace(" ", "-")}',
                figure=fig,
                style={'height': '400px', 'marginBottom': '10px'}
            ),
            html.Div(f"Last tested: {test_date}", style={
                'textAlign': 'center',
                'color': COLORS['text'],
                'fontSize': '14px',
                'marginBottom': '20px',
                'fontFamily': 'Helvetica, Arial, sans-serif',
                'fontWeight': 'normal',
                'opacity': '0.8'
            })
        ])

    # Create appropriate graphs based on metric type
    if active_page == "strength":
        graphs = [
            create_line_graph("Isometric Knee Extension Strength", "N.m.kg⁻¹", target=3.3),
            create_line_graph("Eccentric Knee Flexion Strength [Nordic]", "N.m.kg⁻¹", target=2.0),
            create_line_graph("Seated Plantarflexion Strength", "% BW", target=200)
        ]
    elif active_page == "power":
        graphs = [
            create_donut_chart("Vertical Jump", 85, 90),
            create_donut_chart("Broad Jump", 88, 92),
            create_donut_chart("Medicine Ball Throw", 82, 87)
        ]
    elif active_page == "reactive":
        graphs = [
            create_donut_chart("Drop Jump", 87, 89),
            create_donut_chart("Reactive Strength Index", 90, 88),
            create_donut_chart("Contact Time", 85, 86)
        ]
    elif active_page == "linear":
        graphs = [
            create_line_graph("10m Sprint", "Time (s)"),
            create_line_graph("20m Sprint", "Time (s)"),
            create_line_graph("40m Sprint", "Time (s)")
        ]
    elif active_page == "direction":
        graphs = [
            create_line_graph("505 Test", "Time (s)"),
            create_line_graph("T-Test", "Time (s)"),
            create_line_graph("Illinois Test", "Time (s)")
        ]
    else:
        graphs = []

    # Return the layout instead of creating a new app
    return html.Div([
        # Header with logo, home button, and selection dropdowns
        html.Div([
            # Left side: Logo
            html.Div([
                html.A(
                    html.Img(
                        src="/assets/healthia_performance_logo.png",
                        style={
                            "height": "220px",
                            "marginRight": "20px",
                            "@media (max-width: 768px)": {
                                "height": "150px"
                            }
                        }
                    ),
                    href="/",
                    style={"textDecoration": "none"}
                )
            ], style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "flex-start",
                "flex": "1",
                "@media (max-width: 768px)": {
                    "justifyContent": "center"
                }
            }),

            # Center: Home Button
            html.Div([
                html.A(
                    html.Button("Home", style={
                        "backgroundColor": COLORS['secondary'],
                        "color": "white",
                        "border": "none",
                        "padding": "12px 24px",
                        "borderRadius": "8px",
                        "fontSize": "16px",
                        "fontWeight": "bold",
                        "cursor": "pointer",
                        "fontFamily": "Helvetica, Arial, sans-serif",
                        "boxShadow": "0 0 35px rgba(0, 188, 212, 0.21), 0 0 25px rgba(0, 188, 212, 0.14), 0 0 15px rgba(0, 188, 212, 0.105)",
                        "@media (max-width: 768px)": {
                            "padding": "8px 16px",
                            "fontSize": "14px"
                        }
                    }, className="home-button"),
                    href="/",
                    style={"textDecoration": "none"}
                )
            ], style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "position": "absolute",
                "left": "50%",
                "transform": "translateX(-50%)",
                "@media (max-width: 768px)": {
                    "position": "static",
                    "transform": "none",
                    "margin": "10px 0"
                }
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
                            "transition": "all 0.3s ease",
                            "@media (max-width: 768px)": {
                                "width": "150px",
                                "marginRight": "10px"
                            }
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
                            "transition": "all 0.3s ease",
                            "@media (max-width: 768px)": {
                                "width": "150px"
                            }
                        }
                    )
                ], style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "flex-end",
                    "@media (max-width: 768px)": {
                        "justifyContent": "center"
                    }
                })
            ], style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "flex-end",
                "flex": "1",
                "@media (max-width: 768px)": {
                    "justifyContent": "center"
                }
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
            "position": "relative",
            "@media (max-width: 768px)": {
                "flexDirection": "column",
                "alignItems": "center"
            }
        }),

        # Navigation Circles - Single Row
        html.Div([
            create_nav_circle("Capacity / Motor Control", "/capacity", active_page == "capacity"),
            create_nav_circle("Strength / Hypertrophy", "/strength", active_page == "strength"),
            create_nav_circle("Power / RFD (Slow SSC)", "/power", active_page == "power"),
            create_nav_circle("Reactive Strength (Fast SSC)", "/reactive", active_page == "reactive"),
            create_nav_circle("Linear Running", "/linear", active_page == "linear"),
            create_nav_circle("Change of Direction", "/direction", active_page == "direction")
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
            "borderRadius": "12px",
            "-webkit-overflow-scrolling": "touch",  # Smooth scrolling on iOS
            "@media (max-width: 768px)": {
                "gap": "10px",
                "padding": "10px"
            }
        }),

        # Graphs Container
        html.Div([
            html.Div([
                graph
            ], style={
                'width': '100%',
                'backgroundColor': 'white',
                'padding': '20px',
                'borderRadius': '12px',
                'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                'marginBottom': '20px',
                '@media (max-width: 768px)': {
                    'padding': '10px'
                }
            }) for graph in graphs
        ], style={
            'maxWidth': '1200px',
            'margin': '0 auto',
            'padding': '20px',
            '@media (max-width: 768px)': {
                'padding': '10px'
            }
        })
    ], style={
        "backgroundColor": "#f5f5f5",
        "minHeight": "100vh",
        "padding": "40px 20px",
        "@media (max-width: 768px)": {
            "padding": "20px 10px"
        }
    })

def create_pictogram_chart(title, left_reps, right_reps):
    # Determine max reps based on exercise type
    if "Calf" in title:
        max_reps = 30
    else:  # For bridges and sit to stand
        max_reps = 25

    # Create a list of icons (filled or unfilled) based on repetitions
    def create_icon_row(reps, side):
        # Calculate remaining capacity (only show if under max)
        remaining = max(0, max_reps - reps)
        
        # Create all dots (filled + remaining capacity)
        all_dots = []
        for i in range(reps + remaining):
            # Use secondary (cyan) for left and primary (dark slate) for right
            fill_color = COLORS['secondary'] if side == "Left" else COLORS['primary']
            icon_color = fill_color if i < reps else 'rgba(0, 188, 212, 0.2)' if side == "Left" else 'rgba(69, 90, 100, 0.2)'
            all_dots.append(
                html.Div("●", style={
                    "color": icon_color,
                    "fontSize": "22.8px",
                    "display": "inline-block",
                    "marginRight": "4px",
                    "lineHeight": "1"
                })
            )
        
        # Split dots into rows of 10
        rows = []
        for i in range(0, len(all_dots), 10):
            row_dots = all_dots[i:i+10]
            rows.append(
                html.Div(row_dots, style={
                    "display": "flex",
                    "flexWrap": "nowrap",
                    "gap": "2px",
                    "marginBottom": "8px"
                })
            )

        return html.Div([
            html.Div(f"{side}: {reps}", style={
                "fontSize": "19px",
                "fontWeight": "bold",
                "marginBottom": "8px",
                "color": fill_color
            }),
            html.Div(rows)
        ])

    return html.Div([
        html.H3(title, style={
            "textAlign": "center",
            "color": COLORS['text'],
            "fontSize": "22.8px",
            "marginBottom": "19px"
        }),
        create_icon_row(left_reps, "Left"),
        create_icon_row(right_reps, "Right")
    ], style={
        "backgroundColor": "white",
        "padding": "19px",
        "borderRadius": "12px",
        "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
        "margin": "19px 0",
        "width": "95%",
        "maxWidth": "95%"
    })

def create_capacity_page(active_page):
    # Define historical data for each exercise
    historical_data = {
        'Single Leg Bridge': {
            '2023-01-01': {'left': 12, 'right': 10},
            '2023-02-01': {'left': 14, 'right': 12},
            '2023-03-01': {'left': 16, 'right': 14},
            '2023-04-01': {'left': 18, 'right': 16},
            '2023-05-01': {'left': 20, 'right': 18},
            '2023-06-01': {'left': 22, 'right': 20},
            '2023-07-01': {'left': 24, 'right': 22},
            '2023-08-01': {'left': 26, 'right': 24},
            '2023-09-01': {'left': 28, 'right': 26},
            '2023-10-01': {'left': 28, 'right': 26},
            '2023-11-01': {'left': 28, 'right': 26},
            '2023-12-01': {'left': 28, 'right': 26}
        },
        'Single Leg Squat': {
            '2023-01-01': {'left': 8, 'right': 6},
            '2023-02-01': {'left': 10, 'right': 8},
            '2023-03-01': {'left': 12, 'right': 10},
            '2023-04-01': {'left': 14, 'right': 12},
            '2023-05-01': {'left': 16, 'right': 14},
            '2023-06-01': {'left': 18, 'right': 16},
            '2023-07-01': {'left': 20, 'right': 18},
            '2023-08-01': {'left': 22, 'right': 20},
            '2023-09-01': {'left': 24, 'right': 22},
            '2023-10-01': {'left': 24, 'right': 22},
            '2023-11-01': {'left': 24, 'right': 22},
            '2023-12-01': {'left': 24, 'right': 22}
        },
        'Single Leg Calf Raises': {
            '2023-01-01': {'left': 15, 'right': 13},
            '2023-02-01': {'left': 17, 'right': 15},
            '2023-03-01': {'left': 19, 'right': 17},
            '2023-04-01': {'left': 21, 'right': 19},
            '2023-05-01': {'left': 23, 'right': 21},
            '2023-06-01': {'left': 25, 'right': 23},
            '2023-07-01': {'left': 27, 'right': 25},
            '2023-08-01': {'left': 28, 'right': 26},
            '2023-09-01': {'left': 28, 'right': 26},
            '2023-10-01': {'left': 28, 'right': 26},
            '2023-11-01': {'left': 28, 'right': 26},
            '2023-12-01': {'left': 28, 'right': 26}
        }
    }

    # Create list of all unique dates from historical data
    all_dates = sorted(set(date for exercise_data in historical_data.values() for date in exercise_data.keys()))
    dates = [pd.to_datetime(date) for date in all_dates]

    # Function to get the latest data based on selected date
    def get_latest_data(exercise, selected_date):
        # Convert selected_date to string format if it's a datetime
        if isinstance(selected_date, pd.Timestamp):
            selected_date = selected_date.strftime('%Y-%m-%d')
        
        # Get all dates for this exercise
        exercise_dates = sorted(historical_data[exercise].keys())
        
        # Find the most recent date that's not after the selected date
        latest_valid_date = None
        for date in exercise_dates:
            if date <= selected_date:
                latest_valid_date = date
            else:
                break
        
        # Return the data from the most recent valid date, or the earliest date if none found
        if latest_valid_date:
            return historical_data[exercise][latest_valid_date]
        return historical_data[exercise][exercise_dates[0]]

    # Create pictogram charts for each exercise
    def create_charts(selected_date):
        charts = []
        for exercise in ['Single Leg Bridge', 'Single Leg Squat', 'Single Leg Calf Raises']:
            latest_data = get_latest_data(exercise, selected_date)
            # Get the test date for display below the chart
            test_date = None
            for date in sorted(historical_data[exercise].keys(), reverse=True):
                if date <= selected_date:
                    test_date = pd.to_datetime(date).strftime('%d/%m/%Y')
                    break
            charts.append(
                html.Div([
                    create_pictogram_chart(
                        exercise,
                        latest_data['left'],
                        latest_data['right']
                    ),
                    html.Div(f"Last tested: {test_date}", style={
                        'textAlign': 'center',
                        'color': COLORS['text'],
                        'fontSize': '14px',
                        'marginTop': '10px',
                        'fontFamily': 'Helvetica, Arial, sans-serif',
                        'fontWeight': 'normal',
                        'opacity': '0.8'
                    })
                ])
            )
        return charts

    # Default to the most recent date
    default_date = dates[-1]
    charts = create_charts(default_date.strftime('%Y-%m-%d'))

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
                html.H1("Capacity Metrics", style={
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
                        value=default_date,
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
            create_nav_circle("Capacity / Motor Control", "/capacity", active_page == "capacity"),
            create_nav_circle("Strength / Hypertrophy", "/strength", active_page == "strength"),
            create_nav_circle("Power / RFD (Slow SSC)", "/power", active_page == "power"),
            create_nav_circle("Reactive Strength (Fast SSC)", "/reactive", active_page == "reactive"),
            create_nav_circle("Linear Running", "/linear", active_page == "linear"),
            create_nav_circle("Change of Direction", "/direction", active_page == "direction")
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
        }),

        # Pictogram Charts Container
        html.Div(charts, style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "flexWrap": "nowrap",
            "gap": "20px",
            "maxWidth": "100%",
            "margin": "20px auto",
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