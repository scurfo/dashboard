import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
from scipy import stats
from datetime import datetime

# Set the default theme to a modern style
pio.templates.default = "plotly_white"

# Define color scheme
COLORS = {
    'primary': '#01ADD8',  # RGB(1, 173, 216)
    'secondary': '#364650',  # RGB(54, 70, 80)
    'white': '#FFFFFF',
    'light_gray': '#ECF0F1',
    'left': '#01ADD8',  # Primary color for left side
    'right': '#364650',  # Secondary color for right side
    'text': '#364650',  # Text color (same as secondary for consistency)
    'background': '#FFFFFF'  # Background color
}

# Define dates for all graphs
DATES = pd.date_range(start='2023-01-01', end='2023-12-31', freq='ME')

# Define tickbox data for each section
tickbox_data = {
    "capacity": {
        "Motor Control & Capacity": [
            "Full active knee extension",
            "Active knee flexion ≥ 120°",
            "Symmetrical squat pattern to mid-calf height",
            "Open chain knee extension: pain-free and no need for NMES"
        ]
    },
    "power": {
        "Power Assessment": [
            "Landing peak force (DLCMJ, SLCMJ): < 10% asymmetry",
            "Concentric and eccentric peak force, RFD and impulse asymmetry <10%"
        ]
    },
    "linear": {
        "Checklist": [
            "Linear running drills completed",
            "70% horizontal velocity achieved drilling over 30m",
            "Banded hip lock switch with no contralateral pelvic drop",
            "5-minute stationary bike maintaining RPM >80 throughout"
        ],
        "Running Gait Analysis": [
            "Video-assessment of upright running and acceleration demonstrates no technical deficits or asymmetries",
            "Peak pelvic tilt ≤ 16°",
            "Peak pelvic excursion ≤ 11°",
            "Peak trunk angle ≤ 11°",
            "Peak pelvic obliquity ≥ 5°",
            "Peak hip adduction ≤ 13°",
            "Peak trunk lateral flexion ≤ 12°"
        ]
    },
    "direction": {
        "Checklist": [
            "COD drill completed",
            "Recommenced linear running",
            "No valgus collapse or pelvic drop during lateral and rotational movement",
            "Full trunk-pelvis-limb coordination during deceleration and redirection tasks"
        ],
        "COD Assessment": [
            "Penultimate foot contact asymmetry <10%, <0.46 seconds",
            "Peak knee flexion 37–59°",
            "Peak hip flexion 22–49°",
            "Peak trunk flexion >5°",
            "Peak pelvic obliquity >17°",
            "Final Assessment"
        ]
    }
}

# Define strength data
strength_data = {
    "Knee Extension Strength": {
        "left": 2.9,
        "right": 3.1,
        "target": 3.3,  # This is the actual target
        "unit": "Nm/kg",
        "test_date": "15/03/2024"
    },
    "Knee Flexion Strength": {
        "left": 1.8,
        "right": 1.7,
        "target": 2.0,
        "unit": "Nm/kg",
        "test_date": "15/03/2024"
    },
    "Seated Plantarflexion Strength": {
        "left": 180,
        "right": 175,
        "target": 200,
        "unit": "% BW",
        "test_date": "15/03/2024"
    },
    "Quadriceps Symmetry": {
        "left": 95,
        "right": 95,
        "target": 100,
        "unit": "%",
        "test_date": "15/03/2024"
    },
    "Hamstring Symmetry": {
        "left": 92,
        "right": 92,
        "target": 100,
        "unit": "%",
        "test_date": "15/03/2024"
    },
    "Front Squat": {
        "left": 100,
        "right": 100,
        "target": 120,
        "unit": "kg",
        "test_date": "15/03/2024"
    },
    "Split Squat": {
        "left": 60,
        "right": 60,
        "target": 80,
        "unit": "kg",
        "test_date": "15/03/2024"
    },
    "Deadlift": {
        "left": 150,
        "right": 150,
        "target": 180,
        "unit": "kg",
        "test_date": "15/03/2024"
    },
    "Bench Press": {
        "left": 80,
        "right": 80,
        "target": 100,
        "unit": "kg",
        "test_date": "15/03/2024"
    },
    "Weighted Pull-Ups": {
        "left": 20,
        "right": 20,
        "target": 30,
        "unit": "kg",
        "test_date": "15/03/2024"
    }
}

# Define power data
power_data = {
    "Countermovement Jump": {
        "left": 28,
        "right": 28,
        "target": 30,
        "unit": "cm"
    },
    "Single-Leg Countermovement Jump": {
        "left": 15.5,
        "right": 16.2,
        "target": 17.0,
        "unit": "cm"
    }
}

# Define reactive data
reactive_data = {
    "Double-Leg Drop Jump RSI": {
        "left": 1.2,
        "right": 1.2,
        "target": 1.3,
        "unit": "RSI"
    },
    "Single-Leg Drop Jump RSI": {
        "left": 0.48,
        "right": 0.50,
        "target": 0.52,
        "unit": "RSI"
    }
}

# Define linear running data
linear_data = {
    "Single-Leg Countermovement Jump": {
        "left": 10.5,
        "right": 11.0,
        "target": 11.9,  # 70% of 17.0 cm from power_data
        "unit": "cm"
    },
    "Knee Extension Strength": {
        "left": 2.1,
        "right": 2.2,
        "target": 2.31,  # 70% of 3.3 Nm/kg from strength_data
        "unit": "Nm/kg"
    },
    "Knee Flexion Strength": {
        "left": 1.3,
        "right": 1.3,
        "target": 1.4,  # 70% of 2.0 Nm/kg from strength_data
        "unit": "Nm/kg"
    },
    "Seated Plantarflexion Strength": {
        "left": 130,
        "right": 135,
        "target": 140,  # 70% of 200% BW from strength_data
        "unit": "% BW"
    },
    "Single-Leg Drop Jump RSI": {
        "left": 0.32,
        "right": 0.33,
        "target": 0.364,  # 70% of 0.52 RSI from reactive_data
        "unit": "RSI"
    }
}

# Define change of direction data
direction_data = {
    "Knee Extension Strength": {
        "left": 2.5,
        "right": 2.6,
        "target": 2.64,  # 80% of 3.3 Nm/kg from strength_data
        "unit": "Nm/kg"
    },
    "Knee Flexion Strength": {
        "left": 1.5,
        "right": 1.55,
        "target": 1.6,  # 80% of 2.0 Nm/kg from strength_data
        "unit": "Nm/kg"
    },
    "Seated Plantarflexion Strength": {
        "left": 150,
        "right": 155,
        "target": 160,  # 80% of 200% BW from strength_data
        "unit": "% BW"
    },
    "Single-Leg Countermovement Jump": {
        "left": 12.8,
        "right": 13.0,
        "target": 13.6,  # 80% of 17.0 cm from power_data
        "unit": "cm"
    },
    "Single-Leg Drop Jump RSI": {
        "left": 0.40,
        "right": 0.41,
        "target": 0.416,  # 80% of 0.52 RSI from reactive_data
        "unit": "RSI"
    }
}

def create_pictogram_chart(title, left_reps, right_reps):
    # Determine max reps based on exercise type
    max_reps = 30 if "Calf" in title else (25 if "Bridge" in title else (20 if "Squat" in title else (25 if "Push" in title else 15)))
    
    def create_icon_row(reps, side):
        # Calculate remaining capacity (only show if under max)
        remaining = max_reps - reps if reps < max_reps else 0
        
        # Calculate number of rows needed (10 dots per row)
        dots_per_row = 10
        num_rows = (max_reps + dots_per_row - 1) // dots_per_row
        
        rows = []
        total_dots_shown = 0
        
        for row in range(num_rows):
            # Calculate how many dots should be in this row
            dots_in_row = min(dots_per_row, max_reps - total_dots_shown)
            if dots_in_row <= 0:
                break
                
            # Calculate filled and unfilled dots for this row
            filled_in_row = min(dots_in_row, max(0, reps - total_dots_shown))
            unfilled_in_row = dots_in_row - filled_in_row
            
            row_dots = []
            
            # Add filled dots
            for _ in range(filled_in_row):
                row_dots.append(html.Div(className="dot", style={
                    "width": "20px",
                    "height": "20px",
                    "borderRadius": "50%",
                    "backgroundColor": COLORS['primary'],
                    "margin": "2px",
                    "display": "inline-block"
                }))
            
            # Add unfilled dots
            for _ in range(unfilled_in_row):
                row_dots.append(html.Div(className="dot", style={
                    "width": "20px",
                    "height": "20px",
                    "borderRadius": "50%",
                    "backgroundColor": COLORS['secondary'],
                    "margin": "2px",
                    "display": "inline-block",
                    "opacity": "0.3"
                }))
            
            rows.append(html.Div(row_dots, style={
                "display": "flex",
                "justifyContent": "flex-start",
                "alignItems": "center",
                "minHeight": "24px",
                "width": "240px"  # Fixed width for 10 dots (20px * 10 + 4px margin * 10)
            }))
            
            total_dots_shown += dots_in_row
        
        return html.Div([
            html.Div(rows, style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "flex-start",
                "margin": "10px"
            }),
            html.Div([
                html.Span(f"{side}: ", style={
                    "color": COLORS['text'],
                    "fontSize": "16px",
                    "fontWeight": "bold"
                }),
                html.Span(f"{reps} reps", style={
                    "color": COLORS['secondary'],
                    "fontSize": "16px",
                    "fontWeight": "bold",
                    "marginLeft": "4px"
                })
            ], style={
                "textAlign": "left",
                "marginTop": "5px"
            })
        ], style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "flex-start"
        })
    
    return html.Div([
        html.H3(title, style={
            "textAlign": "center",
            "color": COLORS['text'],
            "marginBottom": "20px",
            "fontSize": "24px",
            "fontWeight": "bold"
        }),
        html.Div([
            create_icon_row(left_reps, "Left"),
            create_icon_row(right_reps, "Right")
        ], style={
            "display": "flex",
            "flexDirection": "column",
            "gap": "20px",
            "marginBottom": "20px",
            "alignItems": "center"
        })
    ], style={
        "margin": "10px",
        "width": "calc(33.33% - 20px)",
        "minWidth": "300px",
        "flex": "1 1 auto"
    })

def create_strength_chart(title, page_type=None):
    # Get the data for achieved values from original strength_data
    original_data = strength_data[title]
    left_value = original_data['left']
    right_value = original_data['right']
    unit = original_data['unit']
    
    # Get the appropriate target based on page type
    if page_type == "linear":
        target = linear_data[title]['target']  # This is already 70% of original
    elif page_type == "direction":
        target = direction_data[title]['target']  # This is already 80% of original
    else:
        target = original_data['target']
    
    # Determine if this is a bilateral exercise (where left == right)
    is_bilateral = left_value == right_value
    
    if is_bilateral and title != "Split Squat":
        # For bilateral exercises, create a single donut showing percentage of target
        value = left_value  # since left == right, either can be used
        percentage = (value / target) * 100  # Calculate percentage relative to target
        
        # Create the donut chart
        fig = go.Figure()
        
        # Add the donut chart
        fig.add_trace(go.Pie(
            values=[percentage, 100-percentage],
            labels=['Achieved', 'Remaining'],
            hole=0.7,
            marker_colors=[COLORS['secondary'], 'rgba(0, 188, 212, 0.2)'],
            showlegend=False,
            textinfo='none',
            hoverinfo='none'
        ))
        
        # Add percentage in the center
        fig.add_annotation(
            text=f"{percentage:.0f}%",
            x=0.5,
            y=0.65,
            font=dict(size=36, color=COLORS['secondary']),
            showarrow=False
        )
        
        # Add raw value
        fig.add_annotation(
            text=f"{value:.1f} {unit}",
            x=0.5,
            y=0.35,
            font=dict(size=16, color=COLORS['secondary']),
            showarrow=False
        )
        
        # Update layout
        fig.update_layout(
            showlegend=False,
            margin=dict(t=30, b=30, l=30, r=30),
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=270,
            width=270
        )
        
        return html.Div([
            dcc.Graph(figure=fig, config={'displayModeBar': False})
        ])
    
    # Calculate percentages relative to target
    left_percent = (left_value / target) * 100
    right_percent = (right_value / target) * 100
    
    # Calculate asymmetry
    asymmetry = abs(left_value - right_value) / max(left_value, right_value) * 100
    asymmetry_color = (
        '#4CAF50' if asymmetry < 10 else  # Green for <10%
        '#FFC107' if asymmetry < 20 else  # Amber for 10-20%
        '#F44336'  # Red for >20%
    )
    
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
            title=dict(
                text="Left",
                y=0.95,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=24, color=COLORS['text'])
            ),
        showlegend=False,
            margin=dict(t=50, b=30, l=30, r=30),
            height=270,
            width=270,
        plot_bgcolor='white',
            paper_bgcolor='white'
    )
    # Add percentage
    fig_left.add_annotation(
        text=f"{left_percent:.0f}%",
        x=0.5,
        y=0.65,
        font=dict(size=36, color=COLORS['secondary']),
        showarrow=False
    )
    # Add raw value
    fig_left.add_annotation(
            text=f"{left_value:.1f} {unit}",
        x=0.5,
        y=0.35,
        font=dict(size=16, color=COLORS['secondary']),
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
            title=dict(
                text="Right",
                y=0.95,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=24, color=COLORS['text'])
            ),
        showlegend=False,
            margin=dict(t=50, b=30, l=30, r=30),
            height=270,
            width=270,
        plot_bgcolor='white',
            paper_bgcolor='white'
    )
    # Add percentage
    fig_right.add_annotation(
        text=f"{right_percent:.0f}%",
        x=0.5,
        y=0.65,
        font=dict(size=36, color=COLORS['primary']),
        showarrow=False
    )
    # Add raw value
    fig_right.add_annotation(
            text=f"{right_value:.1f} {unit}",
        x=0.5,
        y=0.35,
        font=dict(size=16, color=COLORS['primary']),
        showarrow=False
    )
    
        # Create container for both charts and asymmetry
    return html.Div([
            # Container for charts
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=fig_left,
                    config={'displayModeBar': False}
                    )
                ], style={'width': '50%', 'display': 'inline-block'}),
                html.Div([
                    dcc.Graph(
                        figure=fig_right,
                        config={'displayModeBar': False}
                    )
                ], style={'width': '50%', 'display': 'inline-block'})
            ], style={
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'width': '100%'
            }),
            # Asymmetry indicator
                html.Div([
                    html.Span("Asymmetry: ", style={
                        'color': COLORS['text'],
                    'fontSize': '16px',
                        'fontWeight': 'normal'
                    }),
                    html.Span(f"{asymmetry:.1f}%", style={
                        'color': asymmetry_color,
                    'fontSize': '20px',
                        'fontWeight': 'bold',
                    'marginLeft': '4px'
                    })
                ], style={
                    'textAlign': 'center',
                'marginTop': '10px',
                    'backgroundColor': 'rgba(255, 255, 255, 0.9)',
                'padding': '8px 16px',
                'borderRadius': '8px',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                'display': 'inline-block',
                'position': 'relative',
                'left': '50%',
                'transform': 'translateX(-50%)'
            })
        ])

def create_power_chart(title, page_type=None):
    # Get the data for achieved values from original power_data
    original_data = power_data[title]
    left_value = original_data['left']
    right_value = original_data['right']
    unit = original_data['unit']
    
    # Get the appropriate target based on page type
    if page_type == "linear":
        target = linear_data[title]['target']  # This is already 70% of original
    elif page_type == "direction":
        target = direction_data[title]['target']  # This is already 80% of original
    else:
        target = original_data['target']
    
    # Determine if this is a bilateral exercise (where left == right)
    is_bilateral = left_value == right_value
    
    if is_bilateral:
        # For bilateral exercises, create a single donut showing percentage of target
        value = left_value  # since left == right, either can be used
        percentage = (value / target) * 100  # Calculate percentage relative to target
        
        # Create the donut chart
        fig = go.Figure()
        
        # Add the donut chart
        fig.add_trace(go.Pie(
            values=[percentage, 100-percentage],
            labels=['Achieved', 'Remaining'],
            hole=0.7,
            marker_colors=[COLORS['secondary'], 'rgba(0, 188, 212, 0.2)'],
            showlegend=False,
            textinfo='none',
            hoverinfo='none'
        ))
        
        # Add percentage in the center
        fig.add_annotation(
            text=f"{percentage:.0f}%",
            x=0.5,
            y=0.65,
            font=dict(size=36, color=COLORS['secondary']),
            showarrow=False
        )
        
        # Add raw value
        fig.add_annotation(
            text=f"{value:.1f} {unit}",
            x=0.5,
            y=0.35,
            font=dict(size=16, color=COLORS['secondary']),
            showarrow=False
        )
        
        # Update layout
        fig.update_layout(
            showlegend=False,
            margin=dict(t=30, b=30, l=30, r=30),
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=270,
            width=270
        )
        
        return html.Div([
            dcc.Graph(figure=fig, config={'displayModeBar': False})
        ])
    else:
        # Calculate percentages relative to target
        left_percent = (left_value / target) * 100
        right_percent = (right_value / target) * 100
    
    # Calculate asymmetry
        asymmetry = abs(left_value - right_value) / max(left_value, right_value) * 100
    asymmetry_color = (
        '#4CAF50' if asymmetry < 10 else  # Green for <10%
        '#FFC107' if asymmetry < 20 else  # Amber for 10-20%
        '#F44336'  # Red for >20%
    )
    
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
            title=dict(
                text="Left",
                y=0.95,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=24, color=COLORS['text'])
            ),
        showlegend=False,
            margin=dict(t=50, b=30, l=30, r=30),
            height=270,
            width=270,
        plot_bgcolor='white',
            paper_bgcolor='white'
    )
    # Add percentage
    fig_left.add_annotation(
        text=f"{left_percent:.0f}%",
        x=0.5,
        y=0.65,
        font=dict(size=36, color=COLORS['secondary']),
        showarrow=False
    )
    # Add raw value
    fig_left.add_annotation(
            text=f"{left_value:.1f} {unit}",
        x=0.5,
        y=0.35,
        font=dict(size=16, color=COLORS['secondary']),
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
            title=dict(
                text="Right",
                y=0.95,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=24, color=COLORS['text'])
            ),
        showlegend=False,
            margin=dict(t=50, b=30, l=30, r=30),
            height=270,
            width=270,
        plot_bgcolor='white',
            paper_bgcolor='white'
    )
    # Add percentage
    fig_right.add_annotation(
        text=f"{right_percent:.0f}%",
        x=0.5,
        y=0.65,
        font=dict(size=36, color=COLORS['primary']),
        showarrow=False
    )
    # Add raw value
    fig_right.add_annotation(
            text=f"{right_value:.1f} {unit}",
        x=0.5,
        y=0.35,
        font=dict(size=16, color=COLORS['primary']),
        showarrow=False
    )
    
        # Create container for both charts and asymmetry
    return html.Div([
            # Container for charts
        html.Div([
            html.Div([
                dcc.Graph(
                    figure=fig_left,
                    config={'displayModeBar': False}
                    )
                ], style={'width': '50%', 'display': 'inline-block'}),
                html.Div([
                    dcc.Graph(
                        figure=fig_right,
                        config={'displayModeBar': False}
                    )
                ], style={'width': '50%', 'display': 'inline-block'})
            ], style={
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'width': '100%'
            }),
            # Asymmetry indicator
                html.Div([
                    html.Span("Asymmetry: ", style={
                        'color': COLORS['text'],
                    'fontSize': '16px',
                        'fontWeight': 'normal'
                    }),
                    html.Span(f"{asymmetry:.1f}%", style={
                        'color': asymmetry_color,
                    'fontSize': '20px',
                        'fontWeight': 'bold',
                    'marginLeft': '4px'
                    })
                ], style={
                    'textAlign': 'center',
                'marginTop': '10px',
                    'backgroundColor': 'rgba(255, 255, 255, 0.9)',
                'padding': '8px 16px',
                'borderRadius': '8px',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                'display': 'inline-block',
                'position': 'relative',
                'left': '50%',
                'transform': 'translateX(-50%)'
            })
        ])

def create_reactive_chart(title, page_type=None):
    # Get the data for achieved values from original reactive_data
    original_data = reactive_data[title]
    left_value = original_data['left']
    right_value = original_data['right']
    unit = original_data['unit']
    
    # Get the appropriate target based on page type
    if page_type == "linear":
        target = linear_data[title]['target']  # This is already 70% of original
    elif page_type == "direction":
        target = direction_data[title]['target']  # This is already 80% of original
    else:
        target = original_data['target']
    
    # Determine if this is a bilateral exercise (where left == right)
    is_bilateral = left_value == right_value
    
    if is_bilateral:
        # For bilateral exercises, create a single donut showing percentage of target
        value = left_value  # since left == right, either can be used
        percentage = (value / target) * 100  # Calculate percentage relative to target
        
        # Create the donut chart
        fig = go.Figure()
        
        # Add the donut chart
        fig.add_trace(go.Pie(
            values=[percentage, 100-percentage],
            labels=['Achieved', 'Remaining'],
            hole=0.7,
            marker_colors=[COLORS['secondary'], 'rgba(0, 188, 212, 0.2)'],
            showlegend=False,
            textinfo='none',
            hoverinfo='none'
        ))
        
        # Add percentage in the center
        fig.add_annotation(
            text=f"{percentage:.0f}%",
            x=0.5,
            y=0.65,
            font=dict(size=36, color=COLORS['secondary']),
            showarrow=False
        )
        
        # Add raw value
        fig.add_annotation(
            text=f"{value:.2f} {unit}",
            x=0.5,
            y=0.35,
            font=dict(size=16, color=COLORS['secondary']),
            showarrow=False
        )
        
        # Update layout
        fig.update_layout(
            showlegend=False,
            margin=dict(t=30, b=30, l=30, r=30),
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=270,
            width=270
        )
        
        return html.Div([
            dcc.Graph(figure=fig, config={'displayModeBar': False})
        ])
    else:
        # Calculate percentages relative to target
        left_percent = (left_value / target) * 100
        right_percent = (right_value / target) * 100
        
        # Calculate asymmetry
        asymmetry = abs(left_value - right_value) / max(left_value, right_value) * 100
        asymmetry_color = (
            '#4CAF50' if asymmetry < 10 else  # Green for <10%
            '#FFC107' if asymmetry < 20 else  # Amber for 10-20%
            '#F44336'  # Red for >20%
        )
        
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
            title=dict(
                text="Left",
                y=0.95,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=24, color=COLORS['text'])
            ),
            showlegend=False,
            margin=dict(t=50, b=30, l=30, r=30),
            height=270,
            width=270,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        # Add percentage
        fig_left.add_annotation(
            text=f"{left_percent:.0f}%",
            x=0.5,
            y=0.65,
            font=dict(size=36, color=COLORS['secondary']),
            showarrow=False
        )
        # Add raw value
        fig_left.add_annotation(
            text=f"{left_value:.2f} {unit}",
            x=0.5,
            y=0.35,
            font=dict(size=16, color=COLORS['secondary']),
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
            title=dict(
                text="Right",
                y=0.95,
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=24, color=COLORS['text'])
            ),
            showlegend=False,
            margin=dict(t=50, b=30, l=30, r=30),
            height=270,
            width=270,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        # Add percentage
        fig_right.add_annotation(
            text=f"{right_percent:.0f}%",
            x=0.5,
            y=0.65,
            font=dict(size=36, color=COLORS['primary']),
            showarrow=False
        )
        # Add raw value
        fig_right.add_annotation(
            text=f"{right_value:.2f} {unit}",
            x=0.5,
            y=0.35,
            font=dict(size=16, color=COLORS['primary']),
            showarrow=False
        )
        
        # Create container for both charts and asymmetry
        return html.Div([
            # Container for charts
            html.Div([
                html.Div([
                    dcc.Graph(
                        figure=fig_left,
                        config={'displayModeBar': False}
                    )
                ], style={'width': '50%', 'display': 'inline-block'}),
            html.Div([
                dcc.Graph(
                    figure=fig_right,
                    config={'displayModeBar': False}
                )
                ], style={'width': '50%', 'display': 'inline-block'})
        ], style={
            'display': 'flex',
            'justifyContent': 'center',
                'alignItems': 'center',
                'width': '100%'
            }),
            # Asymmetry indicator
            html.Div([
                html.Span("Asymmetry: ", style={
                    'color': COLORS['text'],
                    'fontSize': '16px',
                    'fontWeight': 'normal'
                }),
                html.Span(f"{asymmetry:.1f}%", style={
                    'color': asymmetry_color,
                    'fontSize': '20px',
                    'fontWeight': 'bold',
                    'marginLeft': '4px'
                })
            ], style={
                'textAlign': 'center',
                'marginTop': '10px',
                'backgroundColor': 'rgba(255, 255, 255, 0.9)',
                'padding': '8px 16px',
                'borderRadius': '8px',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                'display': 'inline-block',
                'position': 'relative',
                'left': '50%',
                'transform': 'translateX(-50%)'
            })
        ])

def create_line_graph(title, yaxis_title, target=None, is_split_squat=False, show_both_sides=False, is_linear=False, is_direction=False):
    # Get the data for this metric
    if title in strength_data:
        data = strength_data[title]
    elif title in power_data:
        data = power_data[title]
    elif title in reactive_data:
        data = reactive_data[title]
    elif title in linear_data:
        data = linear_data[title]
    elif title in direction_data:
        data = direction_data[title]
    else:
        data = {'left': 100, 'right': 100, 'target': 100}
    
    # Adjust target based on section
    if is_linear:
        target = data['target'] * 0.7  # 70% of target for linear running
    elif is_direction:
        target = data['target'] * 0.8  # 80% of target for change of direction
    else:
        target = data['target']
    
    # Create sample data for the line graph
    line_data = pd.DataFrame({
        'Date': DATES,
        'Left': [data['left']] * len(DATES),
        'Right': [data['right']] * len(DATES)
    })
    
    # Get the most recent test date
    latest_date = line_data['Date'].max()
    test_date = latest_date.strftime('%d/%m/%Y')
    
    # Create line graph
    fig_line = go.Figure()
    
    if is_split_squat or show_both_sides:
        # Add glow effect for left
        for i in range(5, 0, -1):
            fig_line.add_trace(go.Scatter(
                x=line_data['Date'],
                y=line_data['Left'],
                name='',
                line=dict(color=COLORS['secondary'], width=2*i),
                opacity=0.1,
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add main left trace
        fig_line.add_trace(go.Scatter(
            x=line_data['Date'],
            y=line_data['Left'],
            name='Left',
            line=dict(color=COLORS['secondary'], width=2),
            hovertemplate='%{y:.1f}'
        ))
        
        # Add glow effect for right
        for i in range(5, 0, -1):
            fig_line.add_trace(go.Scatter(
                x=line_data['Date'],
                y=line_data['Right'],
                name='',
                line=dict(color=COLORS['primary'], width=2*i),
                opacity=0.1,
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add main right trace
        fig_line.add_trace(go.Scatter(
            x=line_data['Date'],
            y=line_data['Right'],
            name='Right',
            line=dict(color=COLORS['primary'], width=2),
            hovertemplate='%{y:.1f}'
        ))
    else:
        # For non-split squat exercises, use a single line
        value = (line_data['Left'] + line_data['Right']) / 2  # Average of left and right
        
        # Add glow effect
        for i in range(5, 0, -1):
            fig_line.add_trace(go.Scatter(
                x=line_data['Date'],
                y=value,
                name='',
                line=dict(color=COLORS['secondary'], width=2*i),
                opacity=0.1,
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add main trace
        fig_line.add_trace(go.Scatter(
            x=line_data['Date'],
            y=value,
            name=title,
            line=dict(color=COLORS['secondary'], width=2),
            hovertemplate='%{y:.1f}'
        ))
    
    # Add target line
    fig_line.add_hline(
        y=target,
        line_dash="dash",
        line_color=COLORS['primary'],
        annotation_text=f"Target: {target:.1f} {data['unit']}",
        annotation_position="top right"
    )
    
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
        autosize=True,
        dragmode='pan'
    )
    
    return html.Div([
        dcc.Graph(
            id=f'graph-{title.lower().replace(" ", "-")}',
            figure=fig_line,
            style={'height': '300px', 'marginBottom': '10px'},
            config={'responsive': True, 'displayModeBar': False}
        ),
        html.Div(f"Last tested: {test_date}", style={
            'textAlign': 'center',
            'color': COLORS['text'],
            'fontSize': '14px',
            'marginBottom': '10px',
            'fontFamily': 'Helvetica, Arial, sans-serif',
            'fontWeight': 'normal',
            'opacity': '0.8'
        })
    ])

def create_capacity_page(active_page):
    # Create the header with consistent styling
    header = html.Div([
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
            "flex": "1"
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
                    "boxShadow": "0 0 105px rgba(0, 188, 212, 0.63), 0 0 75px rgba(0, 188, 212, 0.42), 0 0 45px rgba(0, 188, 212, 0.315)"
                }),
                href="/",
                style={"textDecoration": "none"}
            )
        ], style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "position": "absolute",
            "left": "50%",
            "transform": "translateX(-50%)"
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
                        "border": f"2px solid {COLORS['secondary']}"
                    }
                ),
                dcc.Dropdown(
                    id='date-dropdown',
                    options=[{'label': '15/03/2024', 'value': '15/03/2024'}],
                    value='15/03/2024',
                    persistence=True,
                    persistence_type='session',
                    style={
                        "width": "200px",
                        "fontFamily": "Helvetica, Arial, sans-serif",
                        "borderRadius": "8px",
                        "border": f"2px solid {COLORS['secondary']}"
                    }
                )
            ], style={
                "display": "flex",
                "alignItems": "center"
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
        "position": "relative",
        "width": "100%",
        "maxWidth": "1400px",
        "margin": "0 auto",
        "boxSizing": "border-box",
        "overflow": "visible"
    })

    # Navigation Circles Container
    nav_circles = html.Div([
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
        "gap": "15px",
        "overflowX": "auto",
        "whiteSpace": "nowrap",
        "padding": "40px",
        "backgroundColor": "white",
        "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
        "borderRadius": "12px",
        "width": "100%",
        "maxWidth": "1400px",
        "margin": "0 auto"
    })

    # Define historical data for each exercise
    historical_data = {
        # Lower Limb Tests
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
        },
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
        # Upper Limb Tests
        'Push-ups': {
            '2023-01-01': {'left': 15, 'right': 15},
            '2023-02-01': {'left': 16, 'right': 16},
            '2023-03-01': {'left': 17, 'right': 17},
            '2023-04-01': {'left': 18, 'right': 18},
            '2023-05-01': {'left': 19, 'right': 19},
            '2023-06-01': {'left': 20, 'right': 20},
            '2023-07-01': {'left': 21, 'right': 21},
            '2023-08-01': {'left': 22, 'right': 22},
            '2023-09-01': {'left': 23, 'right': 23},
            '2023-10-01': {'left': 24, 'right': 24},
            '2023-11-01': {'left': 24, 'right': 24},
            '2023-12-01': {'left': 24, 'right': 24}
        },
        'Chin-ups': {
            '2023-01-01': {'left': 5, 'right': 5},
            '2023-02-01': {'left': 6, 'right': 6},
            '2023-03-01': {'left': 6, 'right': 6},
            '2023-04-01': {'left': 7, 'right': 7},
            '2023-05-01': {'left': 7, 'right': 7},
            '2023-06-01': {'left': 8, 'right': 8},
            '2023-07-01': {'left': 8, 'right': 8},
            '2023-08-01': {'left': 9, 'right': 9},
            '2023-09-01': {'left': 9, 'right': 9},
            '2023-10-01': {'left': 10, 'right': 10},
            '2023-11-01': {'left': 10, 'right': 10},
            '2023-12-01': {'left': 10, 'right': 10}
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
        # Separate lower and upper limb tests
        lower_limb_tests = ['Single Leg Calf Raises', 'Single Leg Bridge', 'Single Leg Squat']
        upper_limb_tests = ['Push-ups', 'Chin-ups']
        
        lower_limb_charts = []
        upper_limb_charts = []
        
        # Create lower limb charts
        for exercise in lower_limb_tests:
            latest_data = get_latest_data(exercise, selected_date)
            test_date = None
            for date in sorted(historical_data[exercise].keys(), reverse=True):
                if date <= selected_date:
                    test_date = pd.to_datetime(date).strftime('%d/%m/%Y')
                    break
            lower_limb_charts.append(
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
        
        # Create upper limb charts
        for exercise in upper_limb_tests:
            latest_data = get_latest_data(exercise, selected_date)
            test_date = None
            for date in sorted(historical_data[exercise].keys(), reverse=True):
                if date <= selected_date:
                    test_date = pd.to_datetime(date).strftime('%d/%m/%Y')
                    break
            upper_limb_charts.append(
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
        
        return {
            'lower_limb': lower_limb_charts,
            'upper_limb': upper_limb_charts
        }

    # Default to the most recent date
    default_date = dates[-1]
    charts = create_charts(default_date.strftime('%Y-%m-%d'))

    # Create content for capacity page
    content = []

    # Add lower limb charts section
    content.append(html.Div([
        html.H2("Lower Limb Tests", style={
            'textAlign': 'center',
            'color': COLORS['text'],
            'marginBottom': '20px',
            'fontSize': '28px',
            'fontWeight': 'bold'
        }),
        html.Div(charts['lower_limb'], style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'justifyContent': 'center',
            'gap': '20px',
            'marginBottom': '40px'
        })
    ]))

    # Add upper limb charts section
    content.append(html.Div([
        html.H2("Upper Limb Tests", style={
            'textAlign': 'center',
            'color': COLORS['text'],
            'marginBottom': '20px',
            'fontSize': '28px',
            'fontWeight': 'bold'
        }),
        html.Div(charts['upper_limb'], style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'justifyContent': 'center',
            'gap': '20px',
            'marginBottom': '40px'
        })
    ]))

    # Add tickbox sections
    for section_title, items in tickbox_data["capacity"].items():
        content.append(create_tickbox_section(section_title, items))

    # Return the complete layout with consistent container width
    return html.Div([
        header,
        nav_circles,
        html.Div(content, style={
            "maxWidth": "1400px",
            "margin": "0 auto",
            "padding": "20px"
        })
    ], style={
        "minHeight": "100vh",
        "padding": "20px",
        "maxWidth": "1400px",
        "margin": "0 auto",
        "width": "100%",
        "position": "relative",
        "left": "50%",
        "transform": "translateX(-50%)",
        "boxSizing": "border-box",
        "overflow": "hidden"
    })

def create_traffic_light(title, page_type):
    # Get original values from appropriate data source
    if "Strength" in title:
        original_data = strength_data[title]
    elif "Countermovement Jump" in title:
        original_data = power_data[title]
    else:
        original_data = reactive_data[title]
    
    left_value = original_data['left']
    right_value = original_data['right']
    
    # Get adjusted target based on page type
    if page_type == "linear":
        target = linear_data[title]['target']  # Already at 70%
    else:  # direction
        target = direction_data[title]['target']  # Already at 80%
    
    # Calculate percentages
    left_percent = (left_value / target) * 100
    right_percent = (right_value / target) * 100
    
    # Create the traffic light display
    return html.Div([
        html.Div(title, style={
            'fontSize': '17px',  # Increased from 16px
            'fontWeight': 'bold',
            'marginBottom': '10px',  # Increased from 9px
            'color': COLORS['text']
        }),
        html.Div([
            # Left light
            html.Div([
                html.Div(style={
                    'width': '24px',  # Increased from 23px
                    'height': '24px',  # Increased from 23px
                    'borderRadius': '50%',
                    'backgroundColor': '#4DB863' if left_value >= target else '#FF6B6B',
                    'display': 'inline-block',
                    'boxShadow': '0 0 10px rgba(77, 184, 99, 0.5)' if left_value >= target else '0 0 10px rgba(255, 107, 107, 0.5)',
                    'marginRight': '8px'  # Increased from 7px
                }),
                html.Div(f"{left_percent:.0f}%", style={
                    'display': 'inline-block',
                    'fontSize': '19px',  # Increased from 18px
                    'color': '#4DB863' if left_value >= target else '#FF6B6B'
                })
            ], style={
                'display': 'inline-block',
                'marginRight': '19px'  # Increased from 18px
            }),
            # Right light
            html.Div([
                html.Div(style={
                    'width': '24px',  # Increased from 23px
                    'height': '24px',  # Increased from 23px
                    'borderRadius': '50%',
                    'backgroundColor': '#4DB863' if right_value >= target else '#FF6B6B',
                    'display': 'inline-block',
                    'boxShadow': '0 0 10px rgba(77, 184, 99, 0.5)' if right_value >= target else '0 0 10px rgba(255, 107, 107, 0.5)',
                    'marginRight': '8px'  # Increased from 7px
                }),
                html.Div(f"{right_percent:.0f}%", style={
                    'display': 'inline-block',
                    'fontSize': '19px',  # Increased from 18px
                    'color': '#4DB863' if right_value >= target else '#FF6B6B'
                })
            ], style={
                'display': 'inline-block'
            })
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'flex-start'
        })
    ], style={
        'display': 'inline-block',
        'padding': '15px 19px',  # Increased from 14px 18px
        'borderRight': '1px solid #eee',
        'minWidth': '217px'  # Increased from 207px
    })

def create_metric_page(title, active_page):
    # Initialize dates for dropdown
    dates = [pd.to_datetime("15/03/2024", format="%d/%m/%Y")]  # Default date
    
    # Create the header with consistent styling
    header = html.Div([
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
            "flex": "1"
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
                    "boxShadow": "0 0 35px rgba(0, 188, 212, 0.21), 0 0 25px rgba(0, 188, 212, 0.14), 0 0 15px rgba(0, 188, 212, 0.105)"
                }),
                href="/",
                style={"textDecoration": "none"}
            )
        ], style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "position": "absolute",
            "left": "50%",
            "transform": "translateX(-50%)"
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
                        "border": f"2px solid {COLORS['secondary']}"
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
                        "border": f"2px solid {COLORS['secondary']}"
                    }
                )
            ], style={
                "display": "flex",
                "alignItems": "center"
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
        "position": "relative",
        "width": "100%",
        "maxWidth": "1400px",
        "margin": "0 auto",
        "boxSizing": "border-box",
        "overflow": "visible"
    })

    # Navigation Circles Container with the same styling as navigation dashboard
    nav_circles = html.Div([
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
        "gap": "15px",
        "overflowX": "auto",
        "whiteSpace": "nowrap",
        "padding": "40px",
        "backgroundColor": "white",
        "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
        "borderRadius": "12px",
        "width": "100%",
        "maxWidth": "1400px",
        "margin": "0 auto"
    })

    # Create graphs based on page type
    content = []
    
    if active_page == "capacity":
        # Add tickbox section for Motor Control & Capacity
        for section_title, items in tickbox_data["capacity"].items():
            content.append(create_tickbox_section(section_title, items))
    
    elif active_page == "strength":
        # Create strength/hypertrophy graphs
        content = []
        
        # Isolated Strength Assessment Section
        isolated_metrics = [
            "Knee Extension Strength",
            "Knee Flexion Strength",
            "Seated Plantarflexion Strength"
        ]
        
        content.append(html.Div([
            html.H2("Isolated Strength Assessment", style={
                'textAlign': 'center',
                'color': COLORS['text'],
                'marginBottom': '20px',
                'fontSize': '28px',
                'fontWeight': 'bold'
            }),
            html.Div([
                html.Div([
                    html.H3(metric, style={
                        'textAlign': 'center',
                        'color': COLORS['text'],
                        'marginBottom': '20px',
                        'fontSize': '24px',
                        'fontWeight': 'bold'
                    }),
                    html.Div([
                        html.Div([
                            create_strength_chart(metric)
                        ], style={
                            'width': '50%',
                            'display': 'inline-block',
                            'verticalAlign': 'top',
                            'backgroundColor': 'white',
                            'borderRadius': '12px',
                            'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                            'padding': '20px',
                            'margin': '10px'
                        }),
                        html.Div([
                            create_line_graph(
                                metric,
                                f"Strength ({strength_data[metric]['unit']})",
                                strength_data[metric]['target'],
                                show_both_sides=True
                            )
                        ], style={
                            'width': '50%',
                            'display': 'inline-block',
                            'verticalAlign': 'top',
                            'backgroundColor': 'white',
                            'borderRadius': '12px',
                            'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                            'padding': '20px',
                            'margin': '10px'
                        })
            ], style={
                'display': 'flex',
                        'justifyContent': 'center',
                        'alignItems': 'stretch'
                    })
                ], style={
                    'width': '100%',
                    'marginBottom': '20px'
                }) for metric in isolated_metrics
            ])
        ]))
        
        # Hypertrophy Section
        hypertrophy_metrics = [
            "Quadriceps Symmetry",
            "Hamstring Symmetry"
        ]
        
        content.append(html.Div([
            html.H2("Hypertrophy", style={
                'textAlign': 'center',
                'color': COLORS['text'],
                'marginBottom': '20px',
                'fontSize': '28px',
                'fontWeight': 'bold'
            }),
            html.Div([
                html.Div([
                    html.Div([
                        html.H4(metric, style={
                            'textAlign': 'center',
                            'color': COLORS['text'],
                            'marginBottom': '20px',
                            'fontSize': '20px',
                            'fontWeight': 'bold'
                        }),
                        create_strength_chart(metric)
                    ], style={
                        'width': '50%',
                        'display': 'inline-block',
                        'verticalAlign': 'top',
                        'textAlign': 'center'
                    }) for metric in hypertrophy_metrics
        ], style={
            'display': 'flex',
                    'justifyContent': 'center',
            'alignItems': 'center',
                    'backgroundColor': 'white',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
            'padding': '20px',
                    'margin': '10px'
                })
            ], style={
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'stretch'
            })
        ]))
        
        # RM Testing Section
        rm_metrics = [
            "Front Squat",
            "Split Squat",
            "Deadlift",
            "Bench Press",
            "Weighted Pull-Ups"
        ]
        
        rm_content = []
        for metric in rm_metrics:
            rm_content.append(html.Div([
                html.Div([
                    html.H3(metric, style={
                        'textAlign': 'center',
                        'color': COLORS['text'],
                        'marginBottom': '10px',  # Reduced from 20px
                        'fontSize': '24px',
                        'fontWeight': 'bold'
                    }),
                    html.Div([
                        create_strength_chart(metric)
                    ], style={
                        'display': 'flex',
                        'justifyContent': 'center',
                        'alignItems': 'center'
                    })
                ], style={
                    'width': '50%',
                    'display': 'inline-block',
                    'verticalAlign': 'top',
            'backgroundColor': 'white',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'padding': '10px',  # Reduced from 20px
                    'margin': '10px'
                }),
                html.Div([
                    create_line_graph(
                        metric,
                        f"Strength ({strength_data[metric]['unit']})",
                        strength_data[metric]['target'],
                        is_split_squat=(metric == "Split Squat"),
                        show_both_sides=(metric == "Split Squat")
                    )
                ], style={
                    'width': '50%',
                    'display': 'inline-block',
                    'verticalAlign': 'top',
                    'backgroundColor': 'white',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'padding': '10px',  # Reduced from 20px
                    'margin': '10px'
                })
            ], style={
                'display': 'flex',
                'marginBottom': '10px',  # Reduced from 20px
                'justifyContent': 'center',
                'alignItems': 'stretch'
            }))
        
        content.append(html.Div([
            html.H2("RM Testing", style={
                'textAlign': 'center',
                'color': COLORS['text'],
                'marginBottom': '20px',
                'fontSize': '28px',
                'fontWeight': 'bold'
            }),
            html.Div(rm_content)
        ]))
    
    elif active_page == "power":
        # Add power metric graphs first
        for metric in power_data.keys():
            data = power_data[metric]
            is_bilateral = data['left'] == data['right']
            
            content.append(html.Div([
        html.Div([
                    html.H3(metric, style={
                        'textAlign': 'center',
                        'color': COLORS['text'],
                        'marginBottom': '20px',
                        'fontSize': '24px',
                        'fontWeight': 'bold'
                    }),
                    html.Div([
                        create_power_chart(metric)
                    ], style={
                        'display': 'flex',
                        'justifyContent': 'center',
                        'alignItems': 'center'
                    })
                ], style={
                    'width': '50%',
                    'display': 'inline-block',
                    'verticalAlign': 'top',
                    'backgroundColor': 'white',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'padding': '20px',
                    'margin': '10px'
                }),
                html.Div([
                    create_line_graph(
                        metric,
                        f"Power ({data['unit']})",
                        data['target']
                    )
                ], style={
                    'width': '50%',
                    'display': 'inline-block',
                    'verticalAlign': 'top',
                    'backgroundColor': 'white',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'padding': '20px',
                    'margin': '10px'
                })
            ], style={
                'display': 'flex',
                'marginBottom': '20px',
                'justifyContent': 'center',
                'alignItems': 'stretch'
            }))
        
        # Add tickbox sections after graphs
        for section_title, items in tickbox_data["power"].items():
            content.append(create_tickbox_section(section_title, items))
    
    elif active_page == "reactive":
        # Add reactive strength graphs
        for metric in reactive_data.keys():
            data = reactive_data[metric]
            is_bilateral = data['left'] == data['right']
            
            content.append(html.Div([
        html.Div([
                    html.H3(metric, style={
                        'textAlign': 'center',
                        'color': COLORS['text'],
                        'marginBottom': '20px',
                        'fontSize': '24px',
                        'fontWeight': 'bold'
                    }),
                    html.Div([
                        create_reactive_chart(metric)
                    ], style={
                        'display': 'flex',
                        'justifyContent': 'center',
                        'alignItems': 'center'
                    })
    ], style={
                    'width': '50%',
                    'display': 'inline-block',
                    'verticalAlign': 'top',
                    'backgroundColor': 'white',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'padding': '20px',
                    'margin': '10px'
                }),
                html.Div([
                    create_line_graph(
                        metric,
                        f"RSI ({data['unit']})",
                        data['target']
                    )
                ], style={
                    'width': '50%',
                    'display': 'inline-block',
                    'verticalAlign': 'top',
                    'backgroundColor': 'white',
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
                    'padding': '20px',
                    'margin': '10px'
                })
            ], style={
                'display': 'flex',
                'marginBottom': '20px',
                'justifyContent': 'center',
                'alignItems': 'stretch'
            }))
    
    elif active_page == "linear":
        # Define the order of metrics
        linear_metrics_order = [
            "Knee Extension Strength",
            "Knee Flexion Strength",
            "Seated Plantarflexion Strength",
            "Single-Leg Countermovement Jump",
            "Single-Leg Drop Jump RSI"
        ]
        
        # Create a single row containing all traffic lights
        content.append(html.Div([
            html.Div([
                create_traffic_light(metric, "linear")
                for metric in linear_metrics_order
            ], style={
                'display': 'flex',
                'flexWrap': 'nowrap',
                'overflowX': 'auto',
                'whiteSpace': 'nowrap',
                'gap': '0',
                'maxWidth': '1400px',
                'margin': '0 auto',
                'justifyContent': 'center'  # Center the traffic lights
            })
        ], style={
            'backgroundColor': 'white',
            'borderRadius': '12px',
            'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
            'padding': '12px',
            'margin': '12px auto',
            'maxWidth': '1400px',
            'display': 'flex',
            'justifyContent': 'center'  # Center the container
        }))
        
        # Add tickbox sections after traffic lights
        for section_title, items in tickbox_data["linear"].items():
            content.append(create_tickbox_section(section_title, items))
    
    elif active_page == "direction":
        # Define the order of metrics for direction
        direction_metrics = list(direction_data.keys())
        
        # Create a single row containing all traffic lights
        content.append(html.Div([
            html.Div([
                create_traffic_light(metric, "direction")
                for metric in direction_metrics
            ], style={
                'display': 'flex',
                'flexWrap': 'nowrap',
                'overflowX': 'auto',
                'whiteSpace': 'nowrap',
                'gap': '0',
                'maxWidth': '1400px',
                'margin': '0 auto',
                'justifyContent': 'center'  # Center the traffic lights
            })
        ], style={
            'backgroundColor': 'white',
            'borderRadius': '12px',
            'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
            'padding': '12px',
            'margin': '12px auto',
            'maxWidth': '1400px',
            'display': 'flex',
            'justifyContent': 'center'  # Center the container
        }))
        
        # Add tickbox sections after traffic lights
        for section_title, items in tickbox_data["direction"].items():
            content.append(create_tickbox_section(section_title, items))

    # Return the complete layout with consistent container width
    return html.Div([
        header,
        nav_circles,
        html.Div(content, style={
            "maxWidth": "1400px",
            "margin": "0 auto",
            "padding": "20px"
        })
    ], style={
        "minHeight": "100vh",
        "padding": "20px",
        "maxWidth": "1400px",
        "margin": "0 auto",
        "width": "100%",
        "position": "relative",
        "left": "50%",
        "transform": "translateX(-50%)",
        "boxSizing": "border-box",
        "overflow": "hidden"
    })

def create_tickbox_section(section_title, items):
    return html.Div([
        html.H3(section_title, style={
            'color': COLORS['text'],
            'fontSize': '24px',
            'fontWeight': 'bold',
            'marginBottom': '20px',
            'textAlign': 'left'
        }),
        html.Div([
            html.Div([
                dcc.Checklist(
                    options=[{'label': item, 'value': item} for item in items],
                    value=[],
                    style={
                        'color': COLORS['text'],
                        'fontSize': '16px',
                        'lineHeight': '1.5'
                    }
                )
            ])
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '12px',
            'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)'
        })
    ], style={
        'marginBottom': '30px'
    }) 

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
                "marginBottom": "2px",
                "lineHeight": "1.1",
                "textDecoration": "none",
                "wordWrap": "break-word",
                "whiteSpace": "normal",
                "maxWidth": "130px"
            }),
            html.Div(sub_text, style={
                "fontSize": "16px",
                "color": COLORS['text'],
                "opacity": "0.8",
                "lineHeight": "1.1",
                "textDecoration": "none",
                "wordWrap": "break-word",
                "whiteSpace": "normal",
                "maxWidth": "130px"
            }) if sub_text else None
        ], style={
            "textAlign": "center",
            "width": "100%",
            "padding": "5px",
            "textDecoration": "none",
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "justifyContent": "center"
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
            "boxShadow": '0 0 90px rgba(0, 188, 212, 0.75), 0 0 135px rgba(0, 188, 212, 0.6), 0 0 180px rgba(0, 188, 212, 0.45)' if is_selected else '0 0 52.5px rgba(0, 188, 212, 0.315), 0 0 37.5px rgba(0, 188, 212, 0.21), 0 0 22.5px rgba(0, 188, 212, 0.1575)',
            "transform": "scale(1.08)" if is_selected else "scale(1)",
            "color": COLORS['text'],
            "backgroundImage": "linear-gradient(to bottom, rgba(255,255,255,0.9), rgba(255,255,255,1))",
            "transition": "all 0.3s ease",
            "zIndex": "1000" if is_selected else "1",
            "textDecoration": "none",
            "position": "relative",
            "flexShrink": "0",
            "&:hover": {
                "transform": "scale(1.3)"
            }
        }
    )

def create_navigation_dashboard():
    """Create the main navigation dashboard layout."""
    header = html.Div([
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
            "flex": "1"
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
                    "boxShadow": "0 0 105px rgba(0, 188, 212, 0.63), 0 0 75px rgba(0, 188, 212, 0.42), 0 0 45px rgba(0, 188, 212, 0.315)"
                }),
                href="/",
                style={"textDecoration": "none"}
            )
        ], style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "position": "absolute",
            "left": "50%",
            "transform": "translateX(-50%)"
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
                        "border": f"2px solid {COLORS['secondary']}"
                    }
                ),
                dcc.Dropdown(
                    id='date-dropdown',
                    options=[{'label': '15/03/2024', 'value': '15/03/2024'}],
                    value='15/03/2024',
                    persistence=True,
                    persistence_type='session',
                    style={
                        "width": "200px",
                        "fontFamily": "Helvetica, Arial, sans-serif",
                        "borderRadius": "8px",
                        "border": f"2px solid {COLORS['secondary']}"
                    }
                )
            ], style={
                "display": "flex",
                "alignItems": "center"
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
        "position": "relative",
        "width": "100%",
        "maxWidth": "1400px",
        "margin": "0 auto",
        "boxSizing": "border-box",
        "overflow": "visible"
    })

    # Navigation Circles Container
    nav_circles = html.Div([
        create_nav_circle("Capacity / Motor Control", "/capacity", False),
        create_nav_circle("Strength / Hypertrophy", "/strength", False),
        create_nav_circle("Power / RFD (Slow SSC)", "/power", False),
        create_nav_circle("Reactive Strength (Fast SSC)", "/reactive", False),
        create_nav_circle("Linear Running", "/linear", False),
        create_nav_circle("Change of Direction", "/direction", False)
    ], style={
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center",
        "flexWrap": "nowrap",
        "gap": "15px",
        "overflowX": "auto",
        "whiteSpace": "nowrap",
        "padding": "40px",
        "backgroundColor": "white",
        "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.1)",
        "borderRadius": "12px",
        "width": "100%",
        "maxWidth": "1400px",
        "margin": "0 auto"
    })

    return html.Div([
        header,
        nav_circles
    ], style={
        "minHeight": "100vh",
        "padding": "20px",
        "maxWidth": "1400px",
        "margin": "0 auto",
        "width": "100%",
        "position": "relative",
        "left": "50%",
        "transform": "translateX(-50%)",
        "boxSizing": "border-box",
        "overflow": "hidden"
    })

# Initialize the Dash app
app = dash.Dash(__name__)

# Create the layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback to update page content based on URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return create_navigation_dashboard()
    elif pathname == '/capacity':
        return create_capacity_page('capacity')
    elif pathname == '/strength':
        return create_metric_page('Strength / Hypertrophy', 'strength')
    elif pathname == '/power':
        return create_metric_page('Power / RFD', 'power')
    elif pathname == '/reactive':
        return create_metric_page('Reactive Strength', 'reactive')
    elif pathname == '/linear':
        return create_metric_page('Linear Running', 'linear')
    elif pathname == '/direction':
        return create_metric_page('Change of Direction', 'direction')
    else:
        return create_navigation_dashboard()

if __name__ == '__main__':
    app.run(debug=True)