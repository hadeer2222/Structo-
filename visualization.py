"""
Visualization functions for structural analysis results.
"""

import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from matplotlib.figure import Figure
import io
import base64
from typing import Dict, List, Tuple, Any, Optional

def get_plotly_colors():
    """Return a set of colors for consistent use in plotly graphs"""
    return {
        'primary': '#4F8BF9',      # Blue
        'secondary': '#FFA500',    # Orange
        'tertiary': '#00CC96',     # Green
        'quaternary': '#EF553B',   # Red
        'light': '#E5ECF6',        # Light gray
        'dark': '#2A3F5F'          # Dark blue
    }

def get_matplotlib_colors():
    """Return a set of colors for consistent use in matplotlib graphs"""
    return {
        'primary': '#4F8BF9',      # Blue
        'secondary': '#FFA500',    # Orange
        'tertiary': '#00CC96',     # Green
        'quaternary': '#EF553B',   # Red
        'light': '#E5ECF6',        # Light gray
        'dark': '#2A3F5F'          # Dark blue
    }

def plot_moment_diagram(
    span: float, 
    moment: float, 
    load_type: str = "uniform"
) -> str:
    """
    Generate a moment diagram for a beam with the given parameters.
    
    Args:
        span: The span of the beam in meters
        moment: The maximum moment value in kNm
        load_type: The type of loading ("uniform", "point_center", etc.)
        
    Returns:
        str: Base64 encoded image of the moment diagram
    """
    colors = get_matplotlib_colors()
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Create x-axis points along the span
    x = np.linspace(0, span, 100)
    
    # Calculate moment values along the span based on load type
    if load_type == "uniform":
        # For uniform load: M(x) = (wx/2)(L-x)
        # Since we know M_max = wL²/8, then w = 8*M_max/L²
        w = 8 * moment / (span**2)
        y = (w * x / 2) * (span - x)
    elif load_type == "point_center":
        # For point load at center: M(x) = Px/2 for x <= L/2, M(x) = P(L-x)/2 for x > L/2
        # Since we know M_max = PL/4, then P = 4*M_max/L
        p = 4 * moment / span
        y = np.where(x <= span/2, p * x / 2, p * (span - x) / 2)
    else:
        # Default case
        y = np.zeros_like(x)
    
    # Plot the moment diagram
    ax.plot(x, y, color=colors['primary'], linewidth=2)
    ax.fill_between(x, y, color=colors['primary'], alpha=0.3)
    
    # Add zero line
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    
    # Add supports
    ax.plot([0], [0], 'v', color='black', markersize=10)
    ax.plot([span], [0], '^', color='black', markersize=10)
    
    # Add labels
    ax.set_xlabel('Span (m)', fontsize=12)
    ax.set_ylabel('Moment (kNm)', fontsize=12)
    ax.set_title('Moment Diagram', fontsize=14)
    
    # Add maximum moment value
    ax.text(span/2, -moment*0.2, f"M_max = {moment:.2f} kNm", 
            horizontalalignment='center', fontsize=12)
    
    # Set y-axis limits (negative because moments are typically shown below the beam)
    ax.set_ylim(-moment*1.2, moment*0.1)
    
    # Grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Save the figure to a BytesIO object
    buffer = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Convert to base64 for embedding in HTML
    plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)
    
    return plot_base64

def plot_shear_force_diagram(
    span: float, 
    shear: float, 
    load_type: str = "uniform"
) -> str:
    """
    Generate a shear force diagram for a beam with the given parameters.
    
    Args:
        span: The span of the beam in meters
        shear: The maximum shear force value in kN
        load_type: The type of loading ("uniform", "point_center", etc.)
        
    Returns:
        str: Base64 encoded image of the shear force diagram
    """
    colors = get_matplotlib_colors()
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Create x-axis points along the span
    x = np.linspace(0, span, 100)
    
    # Calculate shear force values along the span based on load type
    if load_type == "uniform":
        # For uniform load: V(x) = w(L/2 - x)
        # Since we know V_max = wL/2, then w = 2*V_max/L
        w = 2 * shear / span
        y = w * (span/2 - x)
    elif load_type == "point_center":
        # For point load at center: V(x) = P/2 for x < L/2, V(x) = -P/2 for x > L/2
        y = np.where(x < span/2, shear, -shear)
    else:
        # Default case
        y = np.zeros_like(x)
    
    # Plot the shear force diagram
    ax.plot(x, y, color=colors['secondary'], linewidth=2)
    ax.fill_between(x, y, color=colors['secondary'], alpha=0.3)
    
    # Add zero line
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    
    # Add supports
    ax.plot([0], [0], 'v', color='black', markersize=10)
    ax.plot([span], [0], '^', color='black', markersize=10)
    
    # Add labels
    ax.set_xlabel('Span (m)', fontsize=12)
    ax.set_ylabel('Shear Force (kN)', fontsize=12)
    ax.set_title('Shear Force Diagram', fontsize=14)
    
    # Add maximum shear force values
    ax.text(span*0.1, shear*0.5, f"+V_max = {shear:.2f} kN", 
            horizontalalignment='left', fontsize=12)
    
    if load_type == "uniform":
        ax.text(span*0.9, -shear*0.5, f"-V_max = {shear:.2f} kN", 
                horizontalalignment='right', fontsize=12)
    
    # Set y-axis limits
    ax.set_ylim(-shear*1.2, shear*1.2)
    
    # Grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Save the figure to a BytesIO object
    buffer = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Convert to base64 for embedding in HTML
    plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)
    
    return plot_base64

def plot_deflection_diagram(
    span: float, 
    deflection: float, 
    load_type: str = "uniform"
) -> str:
    """
    Generate a deflection diagram for a beam with the given parameters.
    
    Args:
        span: The span of the beam in meters
        deflection: The maximum deflection value in mm
        load_type: The type of loading ("uniform", "point_center", etc.)
        
    Returns:
        str: Base64 encoded image of the deflection diagram
    """
    colors = get_matplotlib_colors()
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Create x-axis points along the span
    x = np.linspace(0, span, 100)
    
    # Calculate deflection values along the span based on load type
    if load_type == "uniform":
        # For uniform load: δ(x) = (wx/24EI)(L³ - 2Lx² + x³)
        # Since we're plotting a shape, we can simplify and normalize by max deflection
        y = (x * (span**3 - 2*span*x**2 + x**3)) / (span**4) * 16 * deflection / 5
    elif load_type == "point_center":
        # For point load at center: δ(x) = (Px/48EI)(3L² - 4x²) for x <= L/2
        y = np.where(
            x <= span/2,
            (x * (3*span**2 - 4*x**2)) / (span**3) * 4 * deflection,
            ((span - x) * (3*span**2 - 4*(span-x)**2)) / (span**3) * 4 * deflection
        )
    else:
        # Default case
        y = np.zeros_like(x)
    
    # Plot the deflection diagram (Note: typically deflection is shown downward, so multiply by -1)
    ax.plot(x, -y, color=colors['tertiary'], linewidth=2)
    ax.fill_between(x, -y, color=colors['tertiary'], alpha=0.3)
    
    # Add zero line (representing the undeflected beam)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    
    # Add supports
    ax.plot([0], [0], 'v', color='black', markersize=10)
    ax.plot([span], [0], '^', color='black', markersize=10)
    
    # Add labels
    ax.set_xlabel('Span (m)', fontsize=12)
    ax.set_ylabel('Deflection (mm)', fontsize=12)
    ax.set_title('Deflection Diagram', fontsize=14)
    
    # Add maximum deflection value
    ax.text(span/2, -deflection*1.1, f"δ_max = {deflection:.2f} mm", 
            horizontalalignment='center', fontsize=12)
    
    # Set y-axis limits
    ax.set_ylim(-deflection*1.5, deflection*0.5)
    
    # Grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Save the figure to a BytesIO object
    buffer = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Convert to base64 for embedding in HTML
    plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)
    
    return plot_base64

def plot_section_profile(section_properties: Dict[str, Any]) -> str:
    """
    Generate a 2D visualization of the section profile.
    
    Args:
        section_properties: Dictionary containing section dimensions
        
    Returns:
        str: Base64 encoded image of the section profile
    """
    section_type = section_properties.get("type", "I-Beam")
    height = section_properties.get("height", 200)
    width = section_properties.get("width", 100)
    web_thickness = section_properties.get("web_thickness", 8)
    flange_thickness = section_properties.get("flange_thickness", 12)
    
    colors = get_matplotlib_colors()
    fig, ax = plt.subplots(figsize=(8, 8))
    
    if section_type == "I-Beam":
        # Draw the I-beam
        # Top flange
        ax.add_patch(plt.Rectangle((-width/2, height/2-flange_thickness), width, flange_thickness, color=colors['primary']))
        
        # Web
        ax.add_patch(plt.Rectangle((-web_thickness/2, -height/2+flange_thickness), web_thickness, height-2*flange_thickness, color=colors['primary']))
        
        # Bottom flange
        ax.add_patch(plt.Rectangle((-width/2, -height/2), width, flange_thickness, color=colors['primary']))
        
    elif section_type == "Channel":
        # Draw the channel section
        # Top flange
        ax.add_patch(plt.Rectangle((-web_thickness/2, height/2-flange_thickness), width, flange_thickness, color=colors['primary']))
        
        # Web
        ax.add_patch(plt.Rectangle((-web_thickness/2, -height/2+flange_thickness), web_thickness, height-2*flange_thickness, color=colors['primary']))
        
        # Bottom flange
        ax.add_patch(plt.Rectangle((-web_thickness/2, -height/2), width, flange_thickness, color=colors['primary']))
    
    # Add dimensions
    # Height
    ax.annotate(
        f"{height} mm", 
        xy=(-width*0.7, 0), 
        xytext=(-width*1.2, 0),
        arrowprops=dict(arrowstyle='<->', color='black'),
        ha='right', va='center', fontsize=10
    )
    
    # Width
    ax.annotate(
        f"{width} mm", 
        xy=(0, height/2+flange_thickness*0.5), 
        xytext=(0, height/2+flange_thickness*2),
        arrowprops=dict(arrowstyle='<->', color='black'),
        ha='center', va='bottom', fontsize=10
    )
    
    # Web thickness
    ax.annotate(
        f"{web_thickness} mm", 
        xy=(web_thickness/2, 0), 
        xytext=(width*0.5, 0),
        arrowprops=dict(arrowstyle='<->', color='black'),
        ha='left', va='center', fontsize=10
    )
    
    # Flange thickness
    ax.annotate(
        f"{flange_thickness} mm", 
        xy=(width*0.3, height/2), 
        xytext=(width*0.3, height/2-flange_thickness),
        arrowprops=dict(arrowstyle='<->', color='black'),
        ha='center', va='center', fontsize=10
    )
    
    # Add coordinate system indicator
    ax.plot([0, 0], [-height/2, height/2], 'k--', alpha=0.3)
    ax.plot([-width/2, width/2], [0, 0], 'k--', alpha=0.3)
    
    # Add section properties text
    props_text = f"Section: {section_properties.get('name', '')}\n"
    props_text += f"Area: {section_properties.get('area', 0):.1f} mm²\n"
    props_text += f"Ix: {section_properties.get('Ix', 0):.1e} mm⁴\n"
    props_text += f"Zx: {section_properties.get('Zx', 0):.1e} mm³\n"
    
    ax.text(0, -height*0.9, props_text,
            horizontalalignment='center', verticalalignment='center',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
    
    # Set equal aspect ratio and limits
    ax.set_aspect('equal')
    ax.set_xlim(-width*1.5, width*1.5)
    ax.set_ylim(-height, height)
    
    # Remove axis ticks
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Set title
    ax.set_title(f"{section_type} Section Profile", fontsize=14)
    
    # Save the figure to a BytesIO object
    buffer = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Convert to base64 for embedding in HTML
    plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close(fig)
    
    return plot_base64

def create_interactive_moment_diagram(
    span: float, 
    moment: float, 
    load_type: str = "uniform"
) -> go.Figure:
    """
    Create an interactive plotly moment diagram.
    
    Args:
        span: The span of the beam in meters
        moment: The maximum moment value in kNm
        load_type: The type of loading ("uniform", "point_center", etc.)
        
    Returns:
        go.Figure: Plotly figure object
    """
    colors = get_plotly_colors()
    
    # Create x-axis points along the span
    x = np.linspace(0, span, 100)
    
    # Calculate moment values along the span based on load type
    if load_type == "uniform":
        # For uniform load: M(x) = (wx/2)(L-x)
        # Since we know M_max = wL²/8, then w = 8*M_max/L²
        w = 8 * moment / (span**2)
        y = (w * x / 2) * (span - x)
    elif load_type == "point_center":
        # For point load at center: M(x) = Px/2 for x <= L/2, M(x) = P(L-x)/2 for x > L/2
        # Since we know M_max = PL/4, then P = 4*M_max/L
        p = 4 * moment / span
        y = np.where(x <= span/2, p * x / 2, p * (span - x) / 2)
    else:
        # Default case
        y = np.zeros_like(x)
    
    # Create the plotly figure
    fig = go.Figure()
    
    # Add the moment curve
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='lines',
        fill='tozeroy',
        name='Moment',
        line=dict(color=colors['primary'], width=3),
        fillcolor=f"rgba({int(colors['primary'][1:3], 16)}, {int(colors['primary'][3:5], 16)}, {int(colors['primary'][5:7], 16)}, 0.3)"
    ))
    
    # Add supports
    fig.add_trace(go.Scatter(
        x=[0, span],
        y=[0, 0],
        mode='markers',
        marker=dict(symbol=['triangle-down', 'triangle-up'], size=15, color='black'),
        showlegend=False
    ))
    
    # Add zero line
    fig.add_trace(go.Scatter(
        x=[0, span],
        y=[0, 0],
        mode='lines',
        line=dict(color='black', width=1),
        showlegend=False
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Moment Diagram',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Span (m)',
        yaxis_title='Moment (kNm)',
        margin=dict(l=20, r=20, t=60, b=20),
        height=400,
        annotations=[
            dict(
                x=span/2,
                y=-moment*0.2,
                text=f"M_max = {moment:.2f} kNm",
                showarrow=False,
                font=dict(size=14)
            )
        ]
    )
    
    # Update axes
    fig.update_xaxes(range=[-span*0.1, span*1.1])
    fig.update_yaxes(range=[-moment*1.2, moment*0.1])
    
    return fig

def create_interactive_results_chart(results: Dict[str, Any]) -> go.Figure:
    """
    Create an interactive plotly chart summarizing design check results.
    
    Args:
        results: Dictionary containing check results with utilization ratios
        
    Returns:
        go.Figure: Plotly figure object
    """
    colors = get_plotly_colors()
    
    # Extract utilization values from results
    checks = [
        "Moment Capacity",
        "Deflection",
        "Compactness",
        "Lateral Torsional Buckling"
    ]
    
    utilizations = [
        results.get("capacity_check", {}).get("utilization", 0),
        results.get("deflection_check", {}).get("utilization", 0),
        1.0 if results.get("compactness_check", {}).get("classification", "") == "Compact" else 1.2,
        results.get("ltb_check", {}).get("utilization", 0) or 0
    ]
    
    # Create color scale based on utilization (green for good, red for over-utilized)
    colors_scaled = [
        colors['tertiary'] if u <= 1.0 else colors['quaternary'] for u in utilizations
    ]
    
    # Create the plotly figure
    fig = go.Figure()
    
    # Add horizontal bars for each check
    fig.add_trace(go.Bar(
        x=utilizations,
        y=checks,
        orientation='h',
        marker_color=colors_scaled,
        text=[f"{u:.2f}" for u in utilizations],
        textposition='auto',
        hoverinfo='x+text'
    ))
    
    # Add a vertical line at utilization = 1.0 (limit)
    fig.add_shape(
        type='line',
        x0=1, y0=-0.5,
        x1=1, y1=len(checks)-0.5,
        line=dict(color='red', dash='dash')
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Design Check Results',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Utilization Ratio',
        margin=dict(l=20, r=20, t=60, b=20),
        height=300,
        xaxis=dict(range=[0, max(max(utilizations)*1.1, 1.2)])
    )
    
    return fig
