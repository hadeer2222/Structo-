"""
Export functions for saving calculation results to PDF and Excel.
"""

import pandas as pd
import io
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, 
    TableStyle, PageBreak, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import Dict, List, Any, Tuple
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def create_excel_download_link(design_results: Dict[str, Any], filename: str = "structo_results") -> str:
    """
    Create an Excel file with calculation results and return a download link.
    
    Args:
        design_results: Dictionary containing all calculation results
        filename: Base filename for the Excel file
        
    Returns:
        str: HTML for the download link
    """
    # Create a Pandas Excel writer
    buffer = io.BytesIO()
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    
    # Get workbook and add formats
    workbook = writer.book
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#D7E4BC',
        'border': 1
    })
    
    section_header_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'fg_color': '#4F81BD',
        'font_color': 'white',
        'border': 1,
        'align': 'center'
    })
    
    # Create the main summary sheet
    summary_df = pd.DataFrame({
        'Parameter': [
            'Design Type',
            'Span (m)',
            'Design Code',
            'Steel Grade',
            'Maximum Moment (kNm)',
            'Maximum Shear Force (kN)',
            'Maximum Deflection (mm)',
            'Selected Section',
            'Section Height (mm)',
            'Section Width (mm)',
            'Web Thickness (mm)',
            'Flange Thickness (mm)',
            'Section Area (mm²)',
            'Section Modulus (mm³)',
            'Overall Design Status'
        ],
        'Value': [
            design_results.get('design_type', 'Floor Beam'),
            design_results.get('span', 0),
            design_results.get('code', 'Egyptian'),
            design_results.get('steel_grade', 'St37'),
            design_results.get('moment', 0),
            design_results.get('shear', 0),
            design_results.get('results', {}).get('deflection', 0),
            design_results.get('results', {}).get('section_properties', {}).get('name', ''),
            design_results.get('results', {}).get('section_properties', {}).get('height', 0),
            design_results.get('results', {}).get('section_properties', {}).get('width', 0),
            design_results.get('results', {}).get('section_properties', {}).get('web_thickness', 0),
            design_results.get('results', {}).get('section_properties', {}).get('flange_thickness', 0),
            design_results.get('results', {}).get('section_properties', {}).get('area', 0),
            design_results.get('results', {}).get('section_properties', {}).get('Zx', 0),
            design_results.get('results', {}).get('overall_status', 'Unknown')
        ]
    })
    
    summary_df.to_excel(writer, sheet_name='Summary', index=False)
    summary_sheet = writer.sheets['Summary']
    summary_sheet.set_column('A:A', 30)
    summary_sheet.set_column('B:B', 20)
    
    # Format the header row
    for col_num, value in enumerate(summary_df.columns.values):
        summary_sheet.write(0, col_num, value, header_format)
    
    # Create the inputs sheet
    inputs_data = []
    inputs_data.append(['Input Parameter', 'Value', 'Unit'])
    
    # Add basic inputs
    inputs_data.append(['Span', design_results.get('span', 0), 'm'])
    inputs_data.append(['Dead Load', design_results.get('dead_load', 0), 'kN/m'])
    
    # Add different inputs based on design type
    if design_results.get('design_type') == 'Floor Beam':
        inputs_data.append(['Floor Cover Load', design_results.get('floor_cover_load', 0), 'kN/m²'])
        inputs_data.append(['Live Load', design_results.get('live_load', 0), 'kN/m²'])
        inputs_data.append(['Live Load Accessible', 'Yes' if design_results.get('is_accessible', True) else 'No', ''])
    else:  # Purlin
        inputs_data.append(['Live Load (distributed)', design_results.get('live_load', 0), 'kN/m'])
        inputs_data.append(['Maintenance Load', design_results.get('maintenance_load', 0), 'kN'])
        inputs_data.append(['Wind Load', design_results.get('wind_load', 0), 'kN/m²'])
    
    # Add common inputs
    inputs_data.append(['Chord Angle', design_results.get('chord_angle', 0), 'degrees'])
    inputs_data.append(['Steel Grade', design_results.get('steel_grade', ''), ''])
    inputs_data.append(['Design Code', design_results.get('code', ''), ''])
    
    # Add additional loads if present
    additional_loads = design_results.get('additional_loads', [])
    for i, load in enumerate(additional_loads):
        inputs_data.append([f'Additional Load {i+1}', load.get('value', 0), load.get('unit', '')])
    
    # Create DataFrame and write to Excel
    inputs_df = pd.DataFrame(inputs_data[1:], columns=inputs_data[0])
    inputs_df.to_excel(writer, sheet_name='Inputs', index=False)
    inputs_sheet = writer.sheets['Inputs']
    inputs_sheet.set_column('A:A', 25)
    inputs_sheet.set_column('B:B', 15)
    inputs_sheet.set_column('C:C', 10)
    
    # Format the header row
    for col_num, value in enumerate(inputs_df.columns.values):
        inputs_sheet.write(0, col_num, value, header_format)
    
    # Create the outputs/results sheet
    outputs_data = []
    
    # Section for moment results
    outputs_data.append(['Moment Analysis', '', ''])
    outputs_data.append(['Maximum Moment', design_results.get('moment', 0), 'kNm'])
    if 'critical_case' in design_results:
        outputs_data.append(['Critical Load Case', design_results.get('critical_case', ''), ''])
    
    # Section for shear results
    outputs_data.append(['', '', ''])
    outputs_data.append(['Shear Force Analysis', '', ''])
    outputs_data.append(['Maximum Shear Force', design_results.get('shear', 0), 'kN'])
    
    # Section for section properties
    outputs_data.append(['', '', ''])
    outputs_data.append(['Section Properties', '', ''])
    section_props = design_results.get('results', {}).get('section_properties', {})
    for key, value in section_props.items():
        if key not in ['name', 'type']:  # These are already in the summary
            # Add units based on property
            unit = ''
            if 'area' in key.lower():
                unit = 'mm²'
            elif 'i' in key.lower() and key != 'width':
                unit = 'mm⁴'
            elif 'z' in key.lower():
                unit = 'mm³'
            elif any(dim in key.lower() for dim in ['height', 'width', 'thickness']):
                unit = 'mm'
                
            outputs_data.append([key.capitalize(), value, unit])
    
    # Section for design checks
    outputs_data.append(['', '', ''])
    outputs_data.append(['Design Checks', '', ''])
    
    # Moment capacity check
    capacity_check = design_results.get('results', {}).get('capacity_check', {})
    outputs_data.append(['Moment Capacity Check', capacity_check.get('status', ''), ''])
    outputs_data.append(['Moment Capacity Utilization', capacity_check.get('utilization', 0), ''])
    outputs_data.append(['Moment Capacity', capacity_check.get('moment_capacity', 0), 'kNm'])
    
    # Deflection check
    deflection_check = design_results.get('results', {}).get('deflection_check', {})
    outputs_data.append(['Deflection Check', deflection_check.get('status', ''), ''])
    outputs_data.append(['Maximum Deflection', design_results.get('results', {}).get('deflection', 0), 'mm'])
    outputs_data.append(['Allowable Deflection', deflection_check.get('allowable_deflection', 0), 'mm'])
    outputs_data.append(['Deflection Utilization', deflection_check.get('utilization', 0), ''])
    
    # Compactness check
    compactness_check = design_results.get('results', {}).get('compactness_check', {})
    outputs_data.append(['Compactness Check', compactness_check.get('classification', ''), ''])
    outputs_data.append(['Flange Width-to-Thickness Ratio', compactness_check.get('flange_ratio', 0), ''])
    outputs_data.append(['Web Height-to-Thickness Ratio', compactness_check.get('web_ratio', 0), ''])
    
    # Lateral torsional buckling check
    ltb_check = design_results.get('results', {}).get('ltb_check', {})
    outputs_data.append(['Lateral Torsional Buckling Check', ltb_check.get('status', ''), ''])
    outputs_data.append(['LTB Utilization', ltb_check.get('utilization', 0), ''])
    
    # Overall design status
    outputs_data.append(['', '', ''])
    outputs_data.append(['Overall Design Status', design_results.get('results', {}).get('overall_status', ''), ''])
    
    # Create DataFrame and write to Excel
    # First, identify the section headers to format
    section_headers = ['Moment Analysis', 'Shear Force Analysis', 'Section Properties', 'Design Checks']
    section_header_indices = []
    
    for i, row in enumerate(outputs_data):
        if row[0] in section_headers:
            section_header_indices.append(i)
    
    # Write to Excel
    outputs_sheet = writer.book.add_worksheet('Results')
    for row_idx, row_data in enumerate(outputs_data):
        for col_idx, cell_data in enumerate(row_data):
            if row_idx in section_header_indices:
                outputs_sheet.write(row_idx, col_idx, cell_data, section_header_format)
            else:
                outputs_sheet.write(row_idx, col_idx, cell_data)
    
    # Set column widths
    outputs_sheet.set_column('A:A', 30)
    outputs_sheet.set_column('B:B', 20)
    outputs_sheet.set_column('C:C', 10)
    
    # Save the Excel file
    writer.close()
    
    # Get the Excel data and convert to base64
    excel_data = buffer.getvalue()
    b64 = base64.b64encode(excel_data).decode('utf-8')
    
    # Create download link
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">📥 Download Excel Report</a>'
    
    return href

def create_pdf_download_link(design_results: Dict[str, Any], diagrams: Dict[str, str], filename: str = "structo_results") -> str:
    """
    Create a PDF file with calculation results and charts, and return a download link.
    
    Args:
        design_results: Dictionary containing all calculation results
        diagrams: Dictionary containing base64-encoded diagrams
        filename: Base filename for the PDF file
        
    Returns:
        str: HTML for the download link
    """
    # Create a BytesIO buffer for the PDF
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        leftMargin=25*mm, 
        rightMargin=25*mm,
        topMargin=20*mm, 
        bottomMargin=20*mm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    # Modify existing Title style instead of adding a new one
    styles['Title'].alignment = TA_CENTER
    styles['Title'].fontSize = 16
    styles.add(ParagraphStyle(
        name='Subtitle',
        parent=styles['Heading2'],
        fontSize=14
    ))
    styles.add(ParagraphStyle(
        name='Section',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='TableHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.white,
        alignment=TA_CENTER,
        backColor=colors.grey
    ))
    # Modify existing Normal style instead of adding a new one
    styles['Normal'].spaceBefore = 6
    styles['Normal'].spaceAfter = 6
    
    # Build the document content
    elements = []
    
    # Add title and logo
    svg_code = '''
    <svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
        <rect x="10" y="10" width="180" height="80" fill="#4F8BF9" rx="10" ry="10" />
        <text x="50%" y="50%" font-family="Arial" font-size="28" fill="white" text-anchor="middle" dominant-baseline="middle">Structo 🏗</text>
        <line x1="30" y1="75" x2="170" y2="75" stroke="white" stroke-width="3" />
        <line x1="40" y1="65" x2="160" y2="65" stroke="white" stroke-width="2" />
    </svg>
    '''
    
    # Convert SVG to PNG for PDF (simplified approach - in a real app you'd use a proper SVG renderer)
    fig, ax = plt.subplots(figsize=(2, 1))
    ax.text(0.5, 0.5, 'Structo 🏗', fontsize=20, ha='center', va='center')
    ax.axis('off')
    logo_buffer = io.BytesIO()
    plt.savefig(logo_buffer, format='png')
    plt.close(fig)
    logo_buffer.seek(0)
    
    # Create a table for the header with logo and title
    date_str = datetime.now().strftime("%d %b %Y")
    header = [
        [
            Image(logo_buffer, width=80, height=40),
            Paragraph(f"<b>Steel Structure Design Report</b><br/>{date_str}", styles['Title'])
        ]
    ]
    
    header_table = Table(header, colWidths=[100, 350])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 10*mm))
    
    # Project information
    elements.append(Paragraph("Design Details", styles['Subtitle']))
    
    # Create a table for design info
    design_type = design_results.get('design_type', 'Floor Beam')
    code = design_results.get('code', 'Egyptian')
    
    info_data = [
        ["Design Type:", design_type],
        ["Design Code:", code],
        ["Steel Grade:", design_results.get('steel_grade', '')],
        ["Span:", f"{design_results.get('span', 0)} m"],
    ]
    
    if design_type == 'Floor Beam':
        info_data.extend([
            ["Dead Load:", f"{design_results.get('dead_load', 0)} kN/m"],
            ["Floor Cover Load:", f"{design_results.get('floor_cover_load', 0)} kN/m²"],
            ["Live Load:", f"{design_results.get('live_load', 0)} kN/m²"],
            ["Live Load Accessible:", "Yes" if design_results.get('is_accessible', True) else "No"]
        ])
    else:  # Purlin
        info_data.extend([
            ["Dead Load:", f"{design_results.get('dead_load', 0)} kN/m"],
            ["Live Load:", f"{design_results.get('live_load', 0)} kN/m"],
            ["Maintenance Load:", f"{design_results.get('maintenance_load', 0)} kN"],
            ["Wind Load:", f"{design_results.get('wind_load', 0)} kN/m²"]
        ])
    
    info_data.extend([
        ["Chord Angle:", f"{design_results.get('chord_angle', 0)}°"]
    ])
    
    # Add additional loads if present
    additional_loads = design_results.get('additional_loads', [])
    for i, load in enumerate(additional_loads):
        info_data.append([
            f"Additional Load {i+1}:", f"{load.get('value', 0)} {load.get('unit', '')}"
        ])
    
    info_table = Table(info_data, colWidths=[150, 300])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 10*mm))
    
    # Analysis Results Section
    elements.append(Paragraph("Analysis Results", styles['Subtitle']))
    elements.append(Spacer(1, 5*mm))
    
    # Add moment diagram
    if 'moment_diagram' in diagrams:
        elements.append(Paragraph("Moment Diagram", styles['Section']))
        moment_img_data = base64.b64decode(diagrams['moment_diagram'])
        moment_img_buffer = io.BytesIO(moment_img_data)
        elements.append(Image(moment_img_buffer, width=450, height=225))
        
        # Add text results for moment
        moment_data = [
            ["Maximum Moment:", f"{design_results.get('moment', 0):.2f} kNm"]
        ]
        if 'critical_case' in design_results:
            moment_data.append(["Critical Load Case:", design_results.get('critical_case', '')])
        
        moment_table = Table(moment_data, colWidths=[150, 300])
        moment_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(moment_table)
    
    elements.append(Spacer(1, 5*mm))
    
    # Add shear force diagram
    if 'shear_diagram' in diagrams:
        elements.append(Paragraph("Shear Force Diagram", styles['Section']))
        shear_img_data = base64.b64decode(diagrams['shear_diagram'])
        shear_img_buffer = io.BytesIO(shear_img_data)
        elements.append(Image(shear_img_buffer, width=450, height=225))
        
        # Add text results for shear
        shear_data = [
            ["Maximum Shear Force:", f"{design_results.get('shear', 0):.2f} kN"]
        ]
        
        shear_table = Table(shear_data, colWidths=[150, 300])
        shear_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(shear_table)
    
    elements.append(Spacer(1, 5*mm))
    
    # Add deflection diagram
    if 'deflection_diagram' in diagrams:
        elements.append(Paragraph("Deflection Diagram", styles['Section']))
        deflection_img_data = base64.b64decode(diagrams['deflection_diagram'])
        deflection_img_buffer = io.BytesIO(deflection_img_data)
        elements.append(Image(deflection_img_buffer, width=450, height=225))
        
        # Add text results for deflection
        deflection_value = design_results.get('results', {}).get('deflection', 0)
        deflection_check = design_results.get('results', {}).get('deflection_check', {})
        
        deflection_data = [
            ["Maximum Deflection:", f"{deflection_value:.2f} mm"],
            ["Allowable Deflection:", f"{deflection_check.get('allowable_deflection', 0):.2f} mm"],
            ["Deflection Check:", deflection_check.get('status', '')],
            ["Deflection Ratio:", deflection_check.get('limit_ratio', 'L/360')]
        ]
        
        deflection_table = Table(deflection_data, colWidths=[150, 300])
        deflection_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(deflection_table)
    
    # Add page break before section details
    elements.append(PageBreak())
    
    # Section Properties
    elements.append(Paragraph("Section Properties and Design Checks", styles['Subtitle']))
    elements.append(Spacer(1, 5*mm))
    
    # Add section profile
    if 'section_profile' in diagrams:
        elements.append(Paragraph("Section Profile", styles['Section']))
        section_img_data = base64.b64decode(diagrams['section_profile'])
        section_img_buffer = io.BytesIO(section_img_data)
        elements.append(Image(section_img_buffer, width=400, height=400))
    
    # Section properties table
    elements.append(Paragraph("Section Details", styles['Section']))
    
    section_props = design_results.get('results', {}).get('section_properties', {})
    section_data = [
        ["Property", "Value", "Unit"]
    ]
    
    # Add section properties
    section_data.extend([
        ["Section Type", section_props.get('type', ''), ""],
        ["Section Name", section_props.get('name', ''), ""],
        ["Height", f"{section_props.get('height', 0):.1f}", "mm"],
        ["Width", f"{section_props.get('width', 0):.1f}", "mm"],
        ["Web Thickness", f"{section_props.get('web_thickness', 0):.1f}", "mm"],
        ["Flange Thickness", f"{section_props.get('flange_thickness', 0):.1f}", "mm"],
        ["Cross-sectional Area", f"{section_props.get('area', 0):.1f}", "mm²"],
        ["Moment of Inertia (Ix)", f"{section_props.get('Ix', 0):.1e}", "mm⁴"],
        ["Section Modulus (Zx)", f"{section_props.get('Zx', 0):.1e}", "mm³"]
    ])
    
    section_table = Table(section_data, colWidths=[200, 180, 70])
    section_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(section_table)
    elements.append(Spacer(1, 10*mm))
    
    # Design Checks
    elements.append(Paragraph("Design Checks", styles['Section']))
    
    results = design_results.get('results', {})
    
    # Setup design checks data
    checks_data = [
        ["Check", "Status", "Utilization"]
    ]
    
    # Add design checks
    capacity_check = results.get('capacity_check', {})
    checks_data.append([
        "Moment Capacity",
        capacity_check.get('status', ''),
        f"{capacity_check.get('utilization', 0):.2f}"
    ])
    
    deflection_check = results.get('deflection_check', {})
    checks_data.append([
        "Deflection",
        deflection_check.get('status', ''),
        f"{deflection_check.get('utilization', 0):.2f}"
    ])
    
    compactness_check = results.get('compactness_check', {})
    checks_data.append([
        "Compactness",
        compactness_check.get('classification', ''),
        "N/A"
    ])
    
    ltb_check = results.get('ltb_check', {})
    checks_data.append([
        "Lateral Torsional Buckling",
        ltb_check.get('status', ''),
        f"{ltb_check.get('utilization', 0):.2f}" if ltb_check.get('utilization') else "N/A"
    ])
    
    checks_data.append([
        "Overall Design",
        results.get('overall_status', ''),
        "N/A"
    ])
    
    # Create the design checks table
    checks_table = Table(checks_data, colWidths=[200, 130, 120])
    
    # Define the style for the table
    table_style = [
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]
    
    # Add color-coding for status cells
    for i in range(1, len(checks_data) - 1):  # Skip header and overall status
        if "Safe" in checks_data[i][1] or "Compact" in checks_data[i][1]:
            table_style.append(('BACKGROUND', (1, i), (1, i), colors.lightgreen))
        elif "Unsafe" in checks_data[i][1] or "Non-Compact" in checks_data[i][1]:
            table_style.append(('BACKGROUND', (1, i), (1, i), colors.lightcoral))
    
    # Handle overall status separately
    if "Safe" in results.get('overall_status', ''):
        table_style.append(('BACKGROUND', (1, -1), (1, -1), colors.lightgreen))
    elif "Unsafe" in results.get('overall_status', ''):
        table_style.append(('BACKGROUND', (1, -1), (1, -1), colors.lightcoral))
    
    checks_table.setStyle(TableStyle(table_style))
    
    elements.append(checks_table)
    elements.append(Spacer(1, 10*mm))
    
    # Add additional design details
    elements.append(Paragraph("Additional Design Details", styles['Section']))
    
    # Compactness check details
    compactness_data = [
        ["Flange Width-to-Thickness Ratio", f"{compactness_check.get('flange_ratio', 0):.2f}"],
        ["Flange Compact Limit", f"{compactness_check.get('flange_compact_limit', 0):.2f}"],
        ["Flange Status", compactness_check.get('flange_status', '')],
        ["Web Height-to-Thickness Ratio", f"{compactness_check.get('web_ratio', 0):.2f}"],
        ["Web Compact Limit", f"{compactness_check.get('web_compact_limit', 0):.2f}"],
        ["Web Status", compactness_check.get('web_status', '')]
    ]
    
    compactness_table = Table(compactness_data, colWidths=[200, 250])
    compactness_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(compactness_table)
    
    # Add footer with page numbers
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(
            doc.pagesize[0] - doc.rightMargin, 
            doc.bottomMargin / 2, 
            text
        )
        # Add report footer
        canvas.drawString(
            doc.leftMargin, 
            doc.bottomMargin / 2, 
            "Structo 🏗 - Steel Structure Design Application"
        )
    
    # Build the document
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    
    # Get the PDF data and create download link
    pdf_data = buffer.getvalue()
    b64 = base64.b64encode(pdf_data).decode('utf-8')
    
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}.pdf">📥 Download PDF Report</a>'
    
    return href
