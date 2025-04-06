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
    'right': '#364650'  # Secondary color for right side
}

# Load data
df = pd.read_csv("data.csv")
df["date"] = pd.to_datetime(df["date"])
df["date_of_birth"] = pd.to_datetime(df["date_of_birth"])
df["injury_date"] = pd.to_datetime(df["injury_date"])

# Calculate derived metrics for both sides
df["knee_extension_left"] = (df["knee_extension_force_left"] * df["knee_extension_lever_left"]) / df["body_mass"]
df["knee_extension_right"] = (df["knee_extension_force_right"] * df["knee_extension_lever_right"]) / df["body_mass"]
df["knee_flexion_left"] = (df["knee_flexion_force_left"] * df["knee_flexion_lever_left"]) / df["body_mass"]
df["knee_flexion_right"] = (df["knee_flexion_force_right"] * df["knee_flexion_lever_right"]) / df["body_mass"]
df["calf_strength_left"] = (df["calf_force_left"] / 9.81) / df["body_mass"] * 100  # Convert to % bodyweight
df["calf_strength_right"] = (df["calf_force_right"] / 9.81) / df["body_mass"] * 100  # Convert to % bodyweight

# Calculate asymmetry indices (percentage difference)
def calculate_asymmetry(left, right):
    return ((right - left) / ((left + right) / 2)) * 100

df["knee_extension_asymmetry"] = calculate_asymmetry(df["knee_extension_left"], df["knee_extension_right"])
df["knee_flexion_asymmetry"] = calculate_asymmetry(df["knee_flexion_left"], df["knee_flexion_right"])
df["calf_strength_asymmetry"] = calculate_asymmetry(df["calf_strength_left"], df["calf_strength_right"])
df["jump_height_asymmetry"] = calculate_asymmetry(df["sl_jump_height_left"], df["sl_jump_height_right"])
df["rsid_asymmetry"] = calculate_asymmetry(df["rsid_left"], df["rsid_right"])

# Create Dash app
app = dash.Dash(__name__)
app.title = "Athlete Dashboard"

# Dropdown options - filter out any null values
athletes = sorted(df["athlete"].dropna().unique())
dates = sorted(df["date"].unique())

def get_color_gradient(percentage, side):
    """Create a modern gradient effect for donut charts"""
    if side == 'left':
        # Use the same blue as the line graphs
        return ['#01ADD8', '#018DB8']  # Primary blue colors
    else:
        # Use darker blue for right side
        return ['#364650', '#263640']  # Secondary blue colors

def get_glow_opacity(value, target, threshold=0.7):
    """Calculate glow opacity based on value relative to target"""
    if value >= target:
        return 0.1  # Maximum glow for target achievement
    elif value >= (target * threshold):
        return 0.05 + (value - (target * threshold)) / (target * (1 - threshold)) * 0.05  # Linear increase from threshold to target
    else:
        return 0.05  # Base glow

# Common style for all figures
def get_common_layout():
    return {
        "font": {"family": "Helvetica, Arial, sans-serif", "color": COLORS['secondary']},
        "paper_bgcolor": COLORS['white'],
        "plot_bgcolor": COLORS['white'],
        "margin": {"t": 30, "b": 30, "l": 30, "r": 30},
        "xaxis": {
            "showgrid": True,
            "gridcolor": "rgba(1, 173, 216, 0.1)",
            "title": {"font": {"family": "Helvetica, Arial, sans-serif"}}
        },
        "yaxis": {
            "showgrid": True,
            "gridcolor": "rgba(1, 173, 216, 0.1)",
            "title": {"font": {"family": "Helvetica, Arial, sans-serif"}}
        }
    }

def add_glow_effect(fig, x_values, y_values, color, opacity=0.2):
    """Add a gradient glow effect around data points and lines"""
    # Convert hex color to RGB for gradient creation
    rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    
    # Add multiple gradient fills with decreasing opacity
    opacities = [0.3, 0.2, 0.1, 0.05]
    for i, op in enumerate(opacities):
        y_offset = np.min(y_values) - (np.max(y_values) - np.min(y_values)) * 0.1 * i
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines',
            fill='tonexty' if i > 0 else 'tozeroy',
            fillcolor=f'rgba{rgb + (op,)}',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip',
            name=''
        ))
        if i < len(opacities) - 1:
            # Add intermediate line for next fill layer
            fig.add_trace(go.Scatter(
                x=x_values,
                y=[y_offset] * len(x_values),
                mode='lines',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip',
                name=''
            ))
    
    # Add glow effect for the line
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode='lines',
        line=dict(
            color=color,
            width=15,
            shape='spline'
        ),
        opacity=opacity * 0.5,
        showlegend=False,
        hoverinfo='skip',
        name=''
    ))
    
    # Add glow effect for points
    sizes = [20, 30, 40]  # Increasing sizes for outer layers
    opacities = [opacity, opacity * 0.75, opacity * 0.5]  # Decreasing opacities
    
    for size, op in zip(sizes, opacities):
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='markers',
            marker=dict(
                size=size,
                color=color,
                line=dict(width=0)
            ),
            opacity=op,
            showlegend=False,
            hoverinfo='skip',
            name=''
        ))

def add_trend_glow(fig, x_values, y_values, color, opacity=0.2):
    """Add glow effect to trend lines"""
    # Create a wider line with lower opacity for the glow
    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode="lines",
        line=dict(
            color=color,
            width=8,
            opacity=opacity,
            shape='spline'
        ),
        showlegend=False,
        hoverinfo='skip'
    ))

def add_donut_glow(fig, percentage, color):
    """Add modern glow effect to donut chart"""
    # Add multiple layers of glow with decreasing opacity
    sizes = [0.85, 0.9, 0.95]  # Increasing sizes for outer layers
    
    if percentage >= 100:
        # Add pronounced green glow for 100% achievement
        opacities = [0.5, 0.4, 0.3]  # Higher opacities for green glow
        glow_color = '#2ecc71'  # Bright green color
    else:
        # Regular glow with original color
        opacities = [0.2, 0.15, 0.1]  # Standard opacities
        glow_color = color
    
    for size, opacity in zip(sizes, opacities):
        fig.add_trace(go.Pie(
            labels=["Glow"],
            values=[percentage],
            hole=size,
            marker=dict(
                colors=[glow_color],
                line=dict(width=0)
            ),
            opacity=opacity,
            showlegend=False,
            textinfo='none',
            hoverinfo='skip'
        ))

# Layout
app.layout = html.Div([
    # Main content container with new layout
    html.Div([
        # Header Section
        html.Div([
            html.H1("Athlete Performance Dashboard", 
                    style={
                        "textAlign": "center",
                        "color": COLORS['secondary'],
                        "fontFamily": "Helvetica, Arial, sans-serif",
                        "marginBottom": "30px",
                        "fontSize": "32px",
                        "fontWeight": "bold",
                        "letterSpacing": "0.5px"
                    }),
            html.Div([
                html.H2(id="athlete-title", 
                       style={
                           "textAlign": "center",
                           "color": COLORS['primary'],
                           "fontFamily": "Helvetica, Arial, sans-serif",
                           "marginBottom": "15px",
                           "fontSize": "24px",
                           "fontWeight": "bold"
                       }),
                html.H3(id="athlete-info",
                       style={
                           "textAlign": "center",
                           "color": COLORS['secondary'],
                           "fontFamily": "Helvetica, Arial, sans-serif",
                           "marginBottom": "20px",
                           "fontSize": "18px",
                           "lineHeight": "1.5",
                           "padding": "10px 20px",
                           "backgroundColor": COLORS['light_gray'],
                           "borderRadius": "8px",
                           "display": "inline-block"
                       })
            ], style={"width": "100%", "textAlign": "center"}),
            
            # Dropdowns in a row
            html.Div([
    dcc.Dropdown(
        id="athlete-dropdown",
        options=[{"label": name, "value": name} for name in athletes],
                    value=athletes[0] if len(athletes) > 0 else None,
                    style={
                        "width": "200px",
                        "display": "inline-block",
                        "marginRight": "20px",
                        "fontFamily": "Helvetica, Arial, sans-serif",
                        "color": COLORS['secondary'],
                        "fontSize": "14px",
                        "backgroundColor": "transparent",
                        "border": "none",
                        "borderBottom": f"1px solid {COLORS['secondary']}",
                        "borderRadius": "0",
                        "padding": "5px 0"
                    }
                ),
                dcc.Dropdown(
                    id="date-dropdown",
                    options=[{"label": date.strftime("%d/%m/%Y"), "value": date} for date in dates],
                    value=dates[-1] if len(dates) > 0 else None,
                    style={
                        "width": "200px",
                        "display": "inline-block",
                        "fontFamily": "Helvetica, Arial, sans-serif",
                        "fontSize": "14px",
                        "backgroundColor": "transparent",
                        "border": "none",
                        "borderBottom": f"1px solid {COLORS['secondary']}",
                        "borderRadius": "0",
                        "padding": "5px 0"
                    }
                )
            ], style={
                "width": "100%", 
                "textAlign": "center", 
                "marginBottom": "20px",
                "padding": "10px",
                "backgroundColor": "transparent"
            })
        ], style={
            "marginBottom": "30px",
            "padding": "20px",
            "backgroundColor": COLORS['white'],
            "borderRadius": "12px",
            "boxShadow": "0 4px 6px rgba(0,0,0,0.1)"
        }),

        # Strength Graphs Row
        html.Div([
            html.H3("Strength", style={
                "textAlign": "center",
                "color": COLORS['secondary'],
                "marginBottom": "20px",
                "fontSize": "20px",
                "fontWeight": "bold",
                "width": "100%",
                "letterSpacing": "0.5px",
                "fontFamily": "Helvetica, Arial, sans-serif"
            }),
            # Left side - Knee Extension
            html.Div([
                dcc.Graph(id="extension-line", style={"height": "300px"})
            ], style={"width": "33%", "display": "inline-block"}),

            # Middle - Knee Flexion
            html.Div([
                dcc.Graph(id="flexion-line", style={"height": "300px"})
            ], style={"width": "33%", "display": "inline-block"}),

            # Right side - Calf Strength
            html.Div([
                dcc.Graph(id="calf-line", style={"height": "300px"})
            ], style={"width": "33%", "display": "inline-block"})
        ], style={"marginBottom": "30px"}),

        # Donut Charts Row
        html.Div([
            html.H3("Power and Reactive Strength", style={
                "textAlign": "center",
                "color": COLORS['secondary'],
                "marginBottom": "20px",
                "fontSize": "20px",
                "fontWeight": "bold",
                "width": "100%",
                "letterSpacing": "0.5px",
                "fontFamily": "Helvetica, Arial, sans-serif"
            }),
            html.Div([
                # Jump Height Left Donut
                html.Div([
                    html.H4("Jump Height Left", style={
                        "textAlign": "center",
                        "color": COLORS['secondary'],
                        "marginBottom": "5px",
                        "fontSize": "16px",
                        "fontWeight": "bold",
                        "letterSpacing": "0.3px",
                        "fontFamily": "Helvetica, Arial, sans-serif"
                    }),
                    dcc.Graph(id="jump-left-donut", style={"height": "250px"})
                ], style={"width": "20%", "display": "inline-block"}),

                # Jump Height Asymmetry
                html.Div([
                    html.H4("Jump Height Asymmetry", style={
                        "textAlign": "center",
                        "color": COLORS['secondary'],
                        "marginBottom": "5px",
                        "fontSize": "16px",
                        "fontWeight": "bold",
                        "letterSpacing": "0.3px",
                        "fontFamily": "Helvetica, Arial, sans-serif"
                    }),
                    html.H2(id="jump-asymmetry", style={
                        "textAlign": "center",
                        "color": COLORS['secondary'],
                        "fontSize": "18px",
                        "fontWeight": "bold",
                        "fontFamily": "Helvetica, Arial, sans-serif"
                    })
                ], style={"width": "5%", "display": "inline-block", "verticalAlign": "middle"}),

                # Jump Height Right Donut
                html.Div([
                    html.H4("Jump Height Right", style={
                        "textAlign": "center",
                        "color": COLORS['secondary'],
                        "marginBottom": "5px",
                        "fontSize": "16px",
                        "fontWeight": "bold",
                        "letterSpacing": "0.3px",
                        "fontFamily": "Helvetica, Arial, sans-serif"
                    }),
                    dcc.Graph(id="jump-right-donut", style={"height": "250px"})
                ], style={"width": "20%", "display": "inline-block", "marginRight": "5%"}),

                # RSI Left Donut
                html.Div([
                    html.H4("RSI Left", style={
                        "textAlign": "center",
                        "color": COLORS['secondary'],
                        "marginBottom": "5px",
                        "fontSize": "16px",
                        "fontWeight": "bold",
                        "letterSpacing": "0.3px",
                        "fontFamily": "Helvetica, Arial, sans-serif"
                    }),
                    dcc.Graph(id="rsid-left-donut", style={"height": "250px"})
                ], style={"width": "20%", "display": "inline-block"}),

                # RSI Asymmetry
    html.Div([
                    html.H4("RSI Asymmetry", style={
                        "textAlign": "center",
                        "color": COLORS['secondary'],
                        "marginBottom": "5px",
                        "fontSize": "16px",
                        "fontWeight": "bold",
                        "letterSpacing": "0.3px",
                        "fontFamily": "Helvetica, Arial, sans-serif"
                    }),
                    html.H2(id="rsid-asymmetry", style={
                        "textAlign": "center",
                        "color": COLORS['secondary'],
                        "fontSize": "18px",
                        "fontWeight": "bold",
                        "fontFamily": "Helvetica, Arial, sans-serif"
                    })
                ], style={"width": "5%", "display": "inline-block", "verticalAlign": "middle"}),

                # RSI Right Donut
                html.Div([
                    html.H4("RSI Right", style={
                        "textAlign": "center",
                        "color": COLORS['secondary'],
                        "marginBottom": "5px",
                        "fontSize": "16px",
                        "fontWeight": "bold",
                        "letterSpacing": "0.3px",
                        "fontFamily": "Helvetica, Arial, sans-serif"
                    }),
                    dcc.Graph(id="rsid-right-donut", style={"height": "250px"})
                ], style={"width": "20%", "display": "inline-block"})
            ], style={"width": "100%", "textAlign": "center"})
        ], style={"width": "100%", "textAlign": "center"})
    ], style={
        "backgroundColor": COLORS['white'],
        "padding": "30px",
        "maxWidth": "1800px",
        "margin": "0 auto"
    })
], style={
    "backgroundColor": COLORS['white'],
    "padding": "30px",
    "maxWidth": "1800px",
    "margin": "0 auto"
})

# Callbacks
@app.callback(
    Output("athlete-title", "children"),
    Output("athlete-info", "children"),
    Output("jump-left-donut", "figure"),
    Output("jump-right-donut", "figure"),
    Output("rsid-left-donut", "figure"),
    Output("rsid-right-donut", "figure"),
    Output("jump-asymmetry", "children"),
    Output("rsid-asymmetry", "children"),
    Output("extension-line", "figure"),
    Output("flexion-line", "figure"),
    Output("calf-line", "figure"),
    Input("athlete-dropdown", "value"),
    Input("date-dropdown", "value")
)
def update_dashboard(selected_athlete, selected_date):
    if selected_athlete is None or selected_date is None:
        return "", "", {}, {}, {}, {}, "", "", {}, {}, {}
        
    athlete_df = df[df["athlete"] == selected_athlete].sort_values("date")
    latest = athlete_df[athlete_df["date"] == selected_date].iloc[0]
    
    # Calculate age
    age = (latest["date"] - latest["date_of_birth"]).days / 365.25
    injury_days = (latest["date"] - latest["injury_date"]).days
    
    # Calculate weeks since injury for x-axis
    weeks_since_injury = (athlete_df["date"] - latest["injury_date"]).dt.days / 7

    # Calculate percentages for each side
    jump_left_percentage = (latest["sl_jump_height_left"] / 17.0) * 100
    jump_right_percentage = (latest["sl_jump_height_right"] / 17.0) * 100
    rsid_left_percentage = (latest["rsid_left"] / 0.52) * 100
    rsid_right_percentage = (latest["rsid_right"] / 0.52) * 100

    # Get common layout
    common_layout = get_common_layout()

    # Donut chart: Single-leg jump height (Left)
    colors_left = get_color_gradient(jump_left_percentage, 'left')
    jump_left_fig = go.Figure()
    
    # Add glow effect
    add_donut_glow(jump_left_fig, jump_left_percentage, colors_left[0])
    
    # Add main donut
    jump_left_fig.add_trace(go.Pie(
        labels=["Achieved", "Remaining"],
        values=[
            latest["sl_jump_height_left"],
            max(0, 17.0 - latest["sl_jump_height_left"])
        ],
        hole=0.7,
        marker=dict(
            colors=[colors_left[0], COLORS['light_gray']],
            line=dict(width=0)
        ),
        textinfo='none'
    ))
    
    # Update layout
    jump_left_fig.update_layout(
        title={
            "text": "",
            "font": {"size": 16, "color": COLORS['secondary']},
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center"
        },
        showlegend=False,
        annotations=[dict(
            text=f"{jump_left_percentage:.1f}%<br>{latest['sl_jump_height_left']:.1f}cm",
            font=dict(size=32, color=COLORS['secondary']),
            showarrow=False,
            x=0.5,
            y=0.5
        )],
        **common_layout
    )

    # Donut chart: Single-leg jump height (Right)
    colors_right = get_color_gradient(jump_right_percentage, 'right')
    jump_right_fig = go.Figure()
    
    # Add glow effect
    add_donut_glow(jump_right_fig, jump_right_percentage, colors_right[0])
    
    # Add main donut
    jump_right_fig.add_trace(go.Pie(
        labels=["Achieved", "Remaining"],
        values=[
            latest["sl_jump_height_right"],
            max(0, 17.0 - latest["sl_jump_height_right"])
        ],
        hole=0.7,
        marker=dict(
            colors=[colors_right[0], COLORS['light_gray']],
            line=dict(width=0)
        ),
        textinfo='none'
    ))
    
    # Update layout
    jump_right_fig.update_layout(
        title={
            "text": "",
            "font": {"size": 16, "color": COLORS['secondary']},
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center"
        },
        showlegend=False,
        annotations=[dict(
            text=f"{jump_right_percentage:.1f}%<br>{latest['sl_jump_height_right']:.1f}cm",
            font=dict(size=32, color=COLORS['secondary']),
            showarrow=False,
            x=0.5,
            y=0.5
        )],
        **common_layout
    )

    # Donut chart: Reactive Strength Index (Left)
    colors_left = get_color_gradient(rsid_left_percentage, 'left')
    rsid_left_fig = go.Figure()
    
    # Add glow effect
    add_donut_glow(rsid_left_fig, rsid_left_percentage, colors_left[0])
    
    # Add main donut
    rsid_left_fig.add_trace(go.Pie(
        labels=["Achieved", "Remaining"],
        values=[
            latest["rsid_left"],
            max(0, 0.52 - latest["rsid_left"])
        ],
        hole=0.7,
        marker=dict(
            colors=[colors_left[0], COLORS['light_gray']],
            line=dict(width=0)
        ),
        textinfo='none'
    ))
    
    # Update layout
    rsid_left_fig.update_layout(
        title={
            "text": "",
            "font": {"size": 16, "color": COLORS['secondary']},
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center"
        },
        showlegend=False,
        annotations=[dict(
            text=f"{rsid_left_percentage:.1f}%<br>{latest['rsid_left']:.2f}",
            font=dict(size=32, color=COLORS['secondary']),
            showarrow=False,
            x=0.5,
            y=0.5
        )],
        **common_layout
    )

    # Donut chart: Reactive Strength Index (Right)
    colors_right = get_color_gradient(rsid_right_percentage, 'right')
    rsid_right_fig = go.Figure()
    
    # Add glow effect
    add_donut_glow(rsid_right_fig, rsid_right_percentage, colors_right[0])
    
    # Add main donut
    rsid_right_fig.add_trace(go.Pie(
        labels=["Achieved", "Remaining"],
        values=[
            latest["rsid_right"],
            max(0, 0.52 - latest["rsid_right"])
        ],
        hole=0.7,
        marker=dict(
            colors=[colors_right[0], COLORS['light_gray']],
            line=dict(width=0)
        ),
        textinfo='none'
    ))
    
    # Update layout
    rsid_right_fig.update_layout(
        title={
            "text": "",
            "font": {"size": 16, "color": COLORS['secondary']},
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center"
        },
        showlegend=False,
        annotations=[dict(
            text=f"{rsid_right_percentage:.1f}%<br>{latest['rsid_right']:.2f}",
            font=dict(size=32, color=COLORS['secondary']),
            showarrow=False,
            x=0.5,
            y=0.5
        )],
        **common_layout
    )

    # Line graph: Knee Extension Strength
    extension_fig = go.Figure()
    
    # Add knee extension traces with glow effects
    add_glow_effect(extension_fig, 
                   weeks_since_injury,
                   athlete_df["knee_extension_left"],
                   COLORS['left'],
                   opacity=0.2)
    add_glow_effect(extension_fig,
                   weeks_since_injury,
                   athlete_df["knee_extension_right"],
                   COLORS['right'],
                   opacity=0.2)
    
    # Add knee extension traces
    extension_fig.add_trace(go.Scatter(
        x=weeks_since_injury,
        y=athlete_df["knee_extension_left"],
        mode="lines+markers",
        name="Left",
        legendgroup="Left",
        line=dict(
            color=COLORS['left'],
            width=5,
            shape='spline'
        ),
        marker=dict(
            size=12,
            color=COLORS['left'],
            line=dict(width=3, color=COLORS['white'])
        ),
        hovertemplate='%{y:.2f} N.m.kg⁻¹<extra>Left</extra>'
    ))
    extension_fig.add_trace(go.Scatter(
        x=weeks_since_injury,
        y=athlete_df["knee_extension_right"],
        mode="lines+markers",
        name="Right",
        legendgroup="Right",
        line=dict(
            color=COLORS['right'],
            width=5,
            shape='spline'
        ),
        marker=dict(
            size=12,
            color=COLORS['right'],
            line=dict(width=3, color=COLORS['white'])
        ),
        hovertemplate='%{y:.2f} N.m.kg⁻¹<extra>Right</extra>'
    ))
    
    # Add target line
    extension_fig.add_hline(
        y=3.3,
        line_dash="dash",
        line_color=COLORS['secondary'],
        line_width=2,
        annotation_text="Target: 3.3 N.m.kg⁻¹",
        annotation_position="right",
        annotation_font_size=12,
        annotation_font_color=COLORS['secondary']
    )
    
    # Add 70% threshold line
    extension_fig.add_hline(
        y=2.31,  # 70% of 3.3
        line_dash="dot",
        line_color=COLORS['secondary'],
        line_width=1,
        annotation_text="70% Target: 2.31 N.m.kg⁻¹",
        annotation_position="right",
        annotation_font_size=10,
        annotation_font_color=COLORS['secondary']
    )

    # Update layout
    extension_fig.update_layout(
        title={
            "text": "Knee Extension",
            "font": {"size": 24, "color": COLORS['secondary']},
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center"
        },
        yaxis_title={
            "text": "Strength (N.m.kg⁻¹)",
            "font": {"size": 14, "color": COLORS['secondary']}
        },
        xaxis_title={
            "text": "Weeks Post-Injury",
            "font": {"size": 14, "color": COLORS['secondary']}
        },
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor=COLORS['white'],
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=12, color=COLORS['secondary'])
        ),
        **common_layout
    )

    # Line graph: Knee Flexion Strength
    flexion_fig = go.Figure()
    
    # Add knee flexion traces with glow effects
    add_glow_effect(flexion_fig,
                   weeks_since_injury,
                   athlete_df["knee_flexion_left"],
                   COLORS['left'],
                   opacity=0.2)
    add_glow_effect(flexion_fig,
                   weeks_since_injury,
                   athlete_df["knee_flexion_right"],
                   COLORS['right'],
                   opacity=0.2)
    
    # Add knee flexion traces
    flexion_fig.add_trace(go.Scatter(
        x=weeks_since_injury,
        y=athlete_df["knee_flexion_left"],
        mode="lines+markers",
        name="Left",
        legendgroup="Left",
        line=dict(
            color=COLORS['left'],
            width=5,
            shape='spline'
        ),
        marker=dict(
            size=12,
            color=COLORS['left'],
            line=dict(width=3, color=COLORS['white'])
        ),
        hovertemplate='%{y:.2f} N.m.kg⁻¹<extra>Left</extra>'
    ))
    flexion_fig.add_trace(go.Scatter(
        x=weeks_since_injury,
        y=athlete_df["knee_flexion_right"],
        mode="lines+markers",
        name="Right",
        legendgroup="Right",
        line=dict(
            color=COLORS['right'],
            width=5,
            shape='spline'
        ),
        marker=dict(
            size=12,
            color=COLORS['right'],
            line=dict(width=3, color=COLORS['white'])
        ),
        hovertemplate='%{y:.2f} N.m.kg⁻¹<extra>Right</extra>'
    ))
    
    # Add target line
    flexion_fig.add_hline(
        y=2.0,
        line_dash="dash",
        line_color=COLORS['secondary'],
        line_width=2,
        annotation_text="Target: 2.0 N.m.kg⁻¹",
        annotation_position="right",
        annotation_font_size=12,
        annotation_font_color=COLORS['secondary']
    )
    
    # Add 70% threshold line
    flexion_fig.add_hline(
        y=1.4,  # 70% of 2.0
        line_dash="dot",
        line_color=COLORS['secondary'],
        line_width=1,
        annotation_text="70% Target: 1.4 N.m.kg⁻¹",
        annotation_position="right",
        annotation_font_size=10,
        annotation_font_color=COLORS['secondary']
    )

    # Update layout
    flexion_fig.update_layout(
        title={
            "text": "Knee Flexion",
            "font": {"size": 24, "color": COLORS['secondary']},
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center"
        },
        yaxis_title={
            "text": "Strength (N.m.kg⁻¹)",
            "font": {"size": 14, "color": COLORS['secondary']}
        },
        xaxis_title={
            "text": "Weeks Post-Injury",
            "font": {"size": 14, "color": COLORS['secondary']}
        },
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor=COLORS['white'],
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=12, color=COLORS['secondary'])
        ),
        **common_layout
    )

    # Line graph: Calf Strength
    calf_fig = go.Figure()
    
    # Add calf strength traces with glow effects
    add_glow_effect(calf_fig,
                   weeks_since_injury,
                   athlete_df["calf_strength_left"],
                   COLORS['left'],
                   opacity=0.2)
    add_glow_effect(calf_fig,
                   weeks_since_injury,
                   athlete_df["calf_strength_right"],
                   COLORS['right'],
                   opacity=0.2)
    
    # Add calf strength traces
    calf_fig.add_trace(go.Scatter(
        x=weeks_since_injury,
        y=athlete_df["calf_strength_left"],
        mode="lines+markers",
        name="Left",
        legendgroup="Left",
        line=dict(
            color=COLORS['left'],
            width=5,
            shape='spline'
        ),
        marker=dict(
            size=12,
            color=COLORS['left'],
            line=dict(width=3, color=COLORS['white'])
        ),
        hovertemplate='%{y:.1f}%% BW<extra>Left</extra>'
    ))
    calf_fig.add_trace(go.Scatter(
        x=weeks_since_injury,
        y=athlete_df["calf_strength_right"],
        mode="lines+markers",
        name="Right",
        legendgroup="Right",
        line=dict(
            color=COLORS['right'],
            width=5,
            shape='spline'
        ),
        marker=dict(
            size=12,
            color=COLORS['right'],
            line=dict(width=3, color=COLORS['white'])
        ),
        hovertemplate='%{y:.1f}%% BW<extra>Right</extra>'
    ))
    
    # Add target line (200% bodyweight)
    calf_fig.add_hline(
        y=200,
        line_dash="dash",
        line_color=COLORS['secondary'],
        line_width=2,
        annotation_text="Target: 200% BW",
        annotation_position="right",
        annotation_font_size=12,
        annotation_font_color=COLORS['secondary']
    )
    
    # Add 70% threshold line (140% bodyweight)
    calf_fig.add_hline(
        y=140,  # 70% of 200
        line_dash="dot",
        line_color=COLORS['secondary'],
        line_width=1,
        annotation_text="70% Target: 140% BW",
        annotation_position="right",
        annotation_font_size=10,
        annotation_font_color=COLORS['secondary']
    )
    
    # Update layout
    calf_fig.update_layout(
        title={
            "text": "Seated Plantarflexion",
            "font": {"size": 24, "color": COLORS['secondary']},
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center"
        },
        yaxis_title={
            "text": "Strength (% Bodyweight)",
            "font": {"size": 14, "color": COLORS['secondary']}
        },
        xaxis_title={
            "text": "Weeks Post-Injury",
            "font": {"size": 14, "color": COLORS['secondary']}
        },
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor=COLORS['white'],
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=12, color=COLORS['secondary'])
        ),
        **common_layout
    )

    # Update the layout for all line graphs to include gradient fill
    for fig in [extension_fig, flexion_fig, calf_fig]:
        fig.update_layout(
            plot_bgcolor=COLORS['white'],
            paper_bgcolor=COLORS['white'],
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(1, 173, 216, 0.1)",
                zeroline=False
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(1, 173, 216, 0.1)",
                zeroline=False
            )
        )

    # Update layout for all graphs
    for fig in [extension_fig, flexion_fig, calf_fig]:
        fig.update_layout(
            title={
                "text": fig.layout.title.text,
                "font": {
                    "size": 20,
                    "color": COLORS['secondary'],
                    "family": "Helvetica, Arial, sans-serif",
                    "weight": "bold"
                },
                "y": 0.95,
                "x": 0.5,
                "xanchor": "center"
            },
            yaxis_title={
                "text": fig.layout.yaxis.title.text,
                "font": {
                    "size": 14,
                    "color": COLORS['secondary'],
                    "family": "Helvetica, Arial, sans-serif"
                }
            },
            xaxis_title={
                "text": fig.layout.xaxis.title.text,
                "font": {
                    "size": 14,
                    "color": COLORS['secondary'],
                    "family": "Helvetica, Arial, sans-serif"
                }
            },
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor=COLORS['white'],
                bordercolor="rgba(0,0,0,0)",
                font=dict(
                    size=12,
                    color=COLORS['secondary'],
                    family="Helvetica, Arial, sans-serif"
                )
            ),
            **common_layout
        )

    return (selected_athlete,
            f"Age: {age:.1f} years | Injury Date: {latest['injury_date'].strftime('%d/%m/%Y')} | Weeks Post-Injury: {injury_days/7:.1f}",
            jump_left_fig, jump_right_fig, rsid_left_fig, rsid_right_fig,
            f"{latest['jump_height_asymmetry']:.1f}%",
            f"{latest['rsid_asymmetry']:.1f}%",
            extension_fig, flexion_fig, calf_fig)

# Run app
if __name__ == "__main__":
    app.run(debug=True)
