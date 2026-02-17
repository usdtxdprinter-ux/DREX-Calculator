"""
DREX - Dryer Exhaust Calculator
Commercial Dryer Exhaust System Sizing Program
Developed for US Draft Co.
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import base64

# Constants
DRYER_CONNECTOR_MAX_DP = 0.25  # IN WC
MANIFOLD_MAX_DP = 1.0  # IN WC
AIR_DENSITY = 0.0696  # lb/ft^3 at 120°F (dryer exhaust temperature)
DUCT_FRICTION_FACTOR = 0.35  # Friction factor for duct

# K-values for fittings (dimensionless) - Updated per engineering standards
K_VALUES = {
    "90° Elbow": 0.5,
    "45° Elbow": 0.25,
    "30° Elbow": 0.15,
    "Lateral Tee": 0.75,
    "Entry (flush)": 0.5,
    "Exit": 1.0
}

# DEF Fan Curve Data
DEF_FAN_CURVES = {
    "DEF04": {
        "CFM": [540, 490, 430, 350, 240],
        "SP": [0, 0.25, 0.5, 0.75, 1.0]
    },
    "DEF08": {
        "CFM": [970, 890, 840, 780, 680, 540, 440, 270],
        "SP": [0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75]
    },
    "DEF015": {
        "CFM": [1860, 1780, 1700, 1610, 1520, 1410, 1280, 1140, 990],
        "SP": [0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    },
    "DEF025": {
        "CFM": [2480, 2400, 2320, 2230, 2140, 2040, 1930, 1790, 1630],
        "SP": [0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    },
    "DEF035": {
        "CFM": [4100, 3940, 3770, 3610, 3460, 3300, 3120, 2900, 2630],
        "SP": [0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    },
    "DEF050": {
        "CFM": [5850, 5660, 5450, 5300, 5090, 4890, 4680, 4460, 4230],
        "SP": [0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    }
}

def initialize_session_state():
    """Initialize session state variables"""
    if 'project_info' not in st.session_state:
        st.session_state.project_info = {}
    if 'dryers' not in st.session_state:
        st.session_state.dryers = []
    if 'manifold_info' not in st.session_state:
        st.session_state.manifold_info = {}
    if 'step' not in st.session_state:
        st.session_state.step = 'welcome'
    if 'calculation_results' not in st.session_state:
        st.session_state.calculation_results = {}

def get_elevation_from_zip(zip_code):
    """Get elevation from zip code using external API"""
    try:
        # Get location from zip code
        response = requests.get(f"https://api.zippopotam.us/us/{zip_code}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            lat = float(data['places'][0]['latitude'])
            lon = float(data['places'][0]['longitude'])
            city = data['places'][0]['place name']
            state = data['places'][0]['state abbreviation']
            
            # Get elevation
            elev_response = requests.get(
                f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}",
                timeout=5
            )
            if elev_response.status_code == 200:
                elevation = elev_response.json()['results'][0]['elevation']
                elevation_ft = elevation * 3.28084  # Convert meters to feet
                return {
                    'city': city,
                    'state': state,
                    'elevation': round(elevation_ft, 0),
                    'success': True
                }
    except:
        pass
    return {'success': False}

def calculate_duct_pressure_loss(length, diameter, velocity, k_sum, rho=AIR_DENSITY):
    """
    Calculate pressure loss using the duct design equation
    dp = ((0.35*L/D) + SUM(k)) * rho * (V/1096.2)^2
    
    Where:
        0.35 = friction factor for duct
        L = length in feet
        D = diameter in inches
        k = sum of fitting loss coefficients (dimensionless)
        rho = air density at 120°F (0.0696 lb/ft^3)
        V = velocity in feet per minute
    
    Args:
        length: duct length in feet
        diameter: duct diameter in inches
        velocity: velocity in feet per minute
        k_sum: sum of all k-values (dimensionless)
        rho: air density in lb/ft^3 (default: 0.0696 at 120°F)
    
    Returns:
        pressure loss in IN WC
    """
    if diameter <= 0:
        return 0
    
    # Note: diameter is in inches, so L/D gives friction in feet/inch
    friction_term = DUCT_FRICTION_FACTOR * (length / diameter)
    total_term = friction_term + k_sum
    velocity_term = (velocity / 1096.2) ** 2
    
    dp = total_term * rho * velocity_term
    return dp

def calculate_velocity(cfm, diameter):
    """Calculate velocity in FPM given CFM and diameter in inches"""
    area_sq_ft = (np.pi * (diameter / 12) ** 2) / 4
    if area_sq_ft > 0:
        return cfm / area_sq_ft
    return 0

def optimize_manifold_diameter(total_cfm, length, k_sum, max_dp=MANIFOLD_MAX_DP):
    """
    Optimize manifold diameter to achieve maximum pressure loss of max_dp
    """
    # Standard duct diameters in inches
    standard_diameters = [4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]
    
    for diameter in standard_diameters:
        velocity = calculate_velocity(total_cfm, diameter)
        dp = calculate_duct_pressure_loss(length, diameter, velocity, k_sum)
        if dp <= max_dp:
            return diameter, velocity, dp
    
    # If no standard diameter works, return the largest
    diameter = standard_diameters[-1]
    velocity = calculate_velocity(total_cfm, diameter)
    dp = calculate_duct_pressure_loss(length, diameter, velocity, k_sum)
    return diameter, velocity, dp

def select_def_fan(required_cfm, required_sp):
    """Select appropriate DEF fan based on CFM and static pressure requirements"""
    suitable_fans = []
    
    for fan_model, curve_data in DEF_FAN_CURVES.items():
        cfm_values = curve_data['CFM']
        sp_values = curve_data['SP']
        
        # Interpolate to find available CFM at required SP
        if required_sp <= max(sp_values):
            available_cfm = np.interp(required_sp, sp_values, cfm_values)
            if available_cfm >= required_cfm:
                # Calculate margin
                margin = ((available_cfm - required_cfm) / required_cfm) * 100
                suitable_fans.append({
                    'model': fan_model,
                    'available_cfm': available_cfm,
                    'margin': margin,
                    'max_cfm': max(cfm_values),
                    'max_sp': max(sp_values)
                })
    
    # Sort by margin (prefer fans with 10-25% margin)
    suitable_fans.sort(key=lambda x: abs(x['margin'] - 17.5))
    
    return suitable_fans

def generate_pdf_report(project_info, dryers, manifold_info, results):
    """Generate comprehensive PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#003366'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#003366'),
        spaceAfter=6,
        spaceBefore=12
    )
    
    # Title
    story.append(Paragraph("COMMERCIAL DRYER EXHAUST SYSTEM", title_style))
    story.append(Paragraph("SIZING CALCULATION REPORT", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Project Information
    story.append(Paragraph("PROJECT INFORMATION", heading_style))
    proj_data = [
        ["Project Name:", project_info.get('name', 'N/A')],
        ["Location:", f"{project_info.get('city', 'N/A')}, {project_info.get('state', 'N/A')} {project_info.get('zip', 'N/A')}"],
        ["Elevation:", f"{project_info.get('elevation', 'N/A')} feet"],
        ["Engineer:", project_info.get('user_name', 'N/A')],
        ["Email:", project_info.get('user_email', 'N/A')],
        ["Date:", datetime.now().strftime("%B %d, %Y")]
    ]
    
    proj_table = Table(proj_data, colWidths=[1.5*inch, 5*inch])
    proj_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(proj_table)
    story.append(Spacer(1, 0.2*inch))
    
    # System Summary
    story.append(Paragraph("SYSTEM SUMMARY", heading_style))
    summary_data = [
        ["Total Number of Dryers:", str(len(dryers))],
        ["Total System CFM:", f"{results.get('total_cfm', 0):.0f} CFM"],
        ["Worst Case Connector Loss:", f"{results.get('worst_connector_dp', 0):.3f} IN WC"],
        ["Manifold Diameter:", f"{manifold_info.get('diameter', 'N/A')} inches"],
        ["Manifold Pressure Loss:", f"{results.get('manifold_dp', 0):.3f} IN WC"],
        ["Total System Pressure Loss:", f"{results.get('total_system_dp', 0):.3f} IN WC"],
        ["Recommended Fan:", results.get('selected_fan', {}).get('model', 'N/A')]
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8E8E8')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Warnings
    if results.get('worst_connector_dp', 0) > DRYER_CONNECTOR_MAX_DP:
        warning_text = f"<font color='red'><b>WARNING:</b> Worst case dryer connector pressure loss ({results.get('worst_connector_dp', 0):.3f} IN WC) exceeds recommended maximum of {DRYER_CONNECTOR_MAX_DP} IN WC. Consider reducing connector length or adding a booster fan.</font>"
        story.append(Paragraph(warning_text, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    # Individual Dryer Details
    story.append(PageBreak())
    story.append(Paragraph("INDIVIDUAL DRYER DETAILS", heading_style))
    
    for idx, dryer in enumerate(dryers, 1):
        story.append(Paragraph(f"<b>Dryer #{idx}</b>", styles['Heading3']))
        
        dryer_detail_data = [
            ["CFM:", f"{dryer['cfm']} CFM"],
            ["Outlet Diameter:", f"{dryer['outlet_diameter']} inches"],
            ["Connector Length:", f"{dryer['connector_length']} feet"],
            ["Connector Fittings:", dryer['connector_fittings_summary']],
            ["Additional K-value:", f"{dryer.get('additional_k', 0):.2f}"],
            ["Total K-value:", f"{dryer['total_k']:.2f}"],
            ["Connector Velocity:", f"{dryer['connector_velocity']:.0f} FPM"],
            ["Connector Pressure Loss:", f"{dryer['connector_dp']:.3f} IN WC"]
        ]
        
        dryer_table = Table(dryer_detail_data, colWidths=[2*inch, 4.5*inch])
        dryer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(dryer_table)
        story.append(Spacer(1, 0.15*inch))
    
    # Manifold Details
    story.append(PageBreak())
    story.append(Paragraph("MANIFOLD DUCT DETAILS", heading_style))
    
    manifold_detail_data = [
        ["Manifold Length:", f"{manifold_info.get('length', 'N/A')} feet"],
        ["Manifold Diameter:", f"{manifold_info.get('diameter', 'N/A')} inches"],
        ["Diameter Selection:", "Optimized" if manifold_info.get('optimize', False) else "User Selected"],
        ["Manifold Fittings:", manifold_info.get('fittings_summary', 'N/A')],
        ["Additional K-value:", f"{manifold_info.get('additional_k', 0):.2f}"],
        ["Total K-value:", f"{results.get('manifold_total_k', 0):.2f}"],
        ["Manifold Velocity:", f"{results.get('manifold_velocity', 0):.0f} FPM"],
        ["Manifold Pressure Loss:", f"{results.get('manifold_dp', 0):.3f} IN WC"]
    ]
    
    manifold_table = Table(manifold_detail_data, colWidths=[2*inch, 4.5*inch])
    manifold_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(manifold_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Fan Selection Details
    story.append(Paragraph("FAN SELECTION", heading_style))
    
    if results.get('selected_fan'):
        fan = results['selected_fan']
        fan_data = [
            ["Selected Model:", fan['model']],
            ["Required CFM:", f"{results.get('total_cfm', 0):.0f} CFM"],
            ["Required Static Pressure:", f"{results.get('total_system_dp', 0):.3f} IN WC"],
            ["Fan Capacity at Operating Point:", f"{fan['available_cfm']:.0f} CFM"],
            ["Design Margin:", f"{fan['margin']:.1f}%"],
            ["Maximum Fan CFM:", f"{fan['max_cfm']:.0f} CFM"],
            ["Maximum Fan SP:", f"{fan['max_sp']:.2f} IN WC"]
        ]
        
        fan_table = Table(fan_data, colWidths=[2.5*inch, 4*inch])
        fan_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#E8E8E8')),
        ]))
        story.append(fan_table)
    else:
        story.append(Paragraph("<font color='red'>No suitable fan found for system requirements.</font>", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_csi_specification(project_info, dryers, manifold_info, results):
    """Generate CSI Specification document"""
    spec = f"""
SECTION 11 31 00
COMMERCIAL DRYER EXHAUST SYSTEM

PART 1 - GENERAL

1.1 SUMMARY
    A. Project: {project_info.get('name', 'N/A')}
    B. Location: {project_info.get('city', 'N/A')}, {project_info.get('state', 'N/A')}
    C. This section specifies a complete commercial dryer exhaust system including
       exhaust fan, ductwork, and all accessories required for proper operation.

1.2 SYSTEM DESCRIPTION
    A. Total Number of Dryers: {len(dryers)}
    B. Total System Airflow: {results.get('total_cfm', 0):.0f} CFM
    C. Total System Static Pressure: {results.get('total_system_dp', 0):.3f} IN WC

1.3 SUBMITTALS
    A. Product Data: Submit manufacturer's technical data for exhaust fan including
       performance curves, motor specifications, and installation instructions.
    B. Shop Drawings: Submit ductwork layout showing all fittings, transitions,
       and connections.
    C. Test Reports: Submit field test reports demonstrating system airflow and
       static pressure performance.

1.4 QUALITY ASSURANCE
    A. Manufacturer: Provide products from single manufacturer with minimum 10 years
       experience in dryer exhaust systems.
    B. Codes and Standards: Install system in accordance with:
       1. International Mechanical Code (IMC)
       2. NFPA 211 - Chimneys, Fireplaces, Vents, and Solid Fuel-Burning Appliances
       3. Local building codes and fire marshal requirements

PART 2 - PRODUCTS

2.1 EXHAUST FAN
    A. Manufacturer: US Draft Co. or approved equal
    B. Model: {results.get('selected_fan', {}).get('model', 'N/A')}
    C. Performance:
       1. Airflow Capacity: {results.get('total_cfm', 0):.0f} CFM minimum
       2. Static Pressure: {results.get('total_system_dp', 0):.3f} IN WC minimum
       3. Fan shall be capable of delivering required CFM at system static pressure
    D. Construction:
       1. Heavy gauge steel construction
       2. Factory assembled and tested
       3. Suitable for outdoor installation
    E. Motor:
       1. Thermally protected
       2. Permanently lubricated bearings
       3. Suitable for continuous duty

2.2 DUCTWORK
    A. Manifold Duct:
       1. Diameter: {manifold_info.get('diameter', 'N/A')} inches
       2. Material: Galvanized steel, minimum 24 gauge
       3. All seams and joints sealed to prevent lint accumulation
    B. Dryer Connectors:
       1. Individual connector ducts from each dryer to manifold
       2. Smooth interior finish to minimize lint accumulation
       3. All ducts sloped minimum 1/4 inch per foot toward dryers
    C. Fittings:
       1. All elbows and transitions formed from duct material
       2. Only lateral tees permitted - NO 90-degree tees
       3. Minimum radius for all elbows: 1.5 times duct diameter

2.3 ACCESSORIES
    A. Lint Collectors: As specified by Owner
    B. Backdraft Dampers: Where required by code
    C. Transition Fittings: As required for connections

PART 3 - EXECUTION

3.1 INSTALLATION
    A. Install exhaust fan in location shown on drawings
    B. Install ductwork with all joints sealed and properly supported
    C. Maintain clearances to combustibles per code requirements
    D. Slope all horizontal ductwork toward dryers for condensate drainage
    E. Provide access doors for cleaning at required intervals

3.2 FIELD QUALITY CONTROL
    A. System Testing:
       1. Measure and record actual system airflow
       2. Measure and record static pressure at fan inlet
       3. Verify proper operation of all dampers and controls
    B. System Balancing:
       1. Adjust system to deliver specified airflow
       2. Balance airflow from individual dryers as required

3.3 STARTUP SERVICE
    A. Factory-authorized technician to supervise initial startup
    B. Verify proper rotation and operation
    C. Instruct Owner's personnel in system operation and maintenance

3.4 DEMONSTRATION AND TRAINING
    A. Demonstrate system operation to Owner's personnel
    B. Provide operation and maintenance manuals

END OF SECTION
"""
    return spec

def main():
    st.set_page_config(page_title="DREX - Dryer Exhaust Calculator", layout="wide")
    initialize_session_state()
    
    # Header
    st.title("🌪️ DREX - Commercial Dryer Exhaust Calculator")
    st.markdown("*Developed by US Draft Co.*")
    st.markdown("---")
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        if st.button("🏠 Start Over"):
            st.session_state.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### Current Progress")
        steps = {
            'welcome': '✓ Welcome',
            'project_info': '✓ Project Info' if st.session_state.step != 'welcome' else '○ Project Info',
            'dryer_input': '✓ Dryer Input' if st.session_state.step not in ['welcome', 'project_info'] else '○ Dryer Input',
            'manifold_input': '✓ Manifold Input' if st.session_state.step not in ['welcome', 'project_info', 'dryer_input'] else '○ Manifold Input',
            'results': '✓ Results' if st.session_state.step == 'results' else '○ Results'
        }
        for step_name, label in steps.items():
            st.markdown(f"**{label}**")
    
    # Main content based on current step
    if st.session_state.step == 'welcome':
        show_welcome_screen()
    elif st.session_state.step == 'project_info':
        show_project_info_screen()
    elif st.session_state.step == 'dryer_input':
        show_dryer_input_screen()
    elif st.session_state.step == 'manifold_input':
        show_manifold_input_screen()
    elif st.session_state.step == 'results':
        show_results_screen()

def show_welcome_screen():
    """Display welcome screen"""
    st.header("Welcome to DREX!")
    st.markdown("""
    ### Commercial Dryer Exhaust System Sizing Calculator
    
    This calculator will help you design a compliant commercial dryer exhaust system by:
    
    - 📊 Calculating pressure losses through dryer connectors and manifold ductwork
    - ⚠️ Identifying potential issues with excessive pressure loss
    - 🔧 Optimizing manifold diameter for maximum efficiency
    - 📈 Selecting the appropriate DEF exhaust fan
    - 📄 Generating professional PDF reports and CSI specifications
    
    #### System Capabilities:
    - Up to 20 individual commercial dryers
    - Up to 4 different dryer capacities
    - Automatic or manual manifold sizing
    - Lint collector accommodation
    - Complete documentation package
    
    #### Design Criteria:
    - Maximum dryer connector loss: 0.25 IN WC (warning issued if exceeded)
    - Maximum manifold loss: 1.0 IN WC
    - Lateral tees only (no 90° tees permitted)
    
    Click **Next** to begin entering your project information.
    """)
    
    if st.button("Next ➡️", type="primary"):
        st.session_state.step = 'project_info'
        st.rerun()

def show_project_info_screen():
    """Display project information input screen"""
    st.header("Project Information")
    
    with st.form("project_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input("Project Name*", value=st.session_state.project_info.get('name', ''))
            zip_code = st.text_input("Zip Code*", value=st.session_state.project_info.get('zip', ''), max_chars=5)
            user_name = st.text_input("Your Name*", value=st.session_state.project_info.get('user_name', ''))
        
        with col2:
            user_email = st.text_input("Your Email*", value=st.session_state.project_info.get('user_email', ''))
            
            # Show location info if zip code is available
            if zip_code and len(zip_code) == 5:
                location_info = get_elevation_from_zip(zip_code)
                if location_info['success']:
                    st.info(f"📍 {location_info['city']}, {location_info['state']}")
                    st.info(f"⛰️ Elevation: {location_info['elevation']:.0f} feet")
        
        submitted = st.form_submit_button("Save and Continue ➡️", type="primary")
        
        if submitted:
            if not all([project_name, zip_code, user_name, user_email]):
                st.error("Please fill in all required fields.")
            elif len(zip_code) != 5 or not zip_code.isdigit():
                st.error("Please enter a valid 5-digit zip code.")
            else:
                location_info = get_elevation_from_zip(zip_code)
                
                st.session_state.project_info = {
                    'name': project_name,
                    'zip': zip_code,
                    'user_name': user_name,
                    'user_email': user_email,
                    'city': location_info.get('city', 'Unknown') if location_info['success'] else 'Unknown',
                    'state': location_info.get('state', 'Unknown') if location_info['success'] else 'Unknown',
                    'elevation': location_info.get('elevation', 0) if location_info['success'] else 0
                }
                st.session_state.step = 'dryer_input'
                st.rerun()

def show_dryer_input_screen():
    """Display dryer input screen"""
    st.header("Dryer Information")
    st.markdown(f"**Project:** {st.session_state.project_info.get('name', 'N/A')}")
    
    # Show existing dryers
    if st.session_state.dryers:
        st.subheader(f"Current Dryers ({len(st.session_state.dryers)}/20)")
        
        for idx, dryer in enumerate(st.session_state.dryers):
            with st.expander(f"Dryer #{idx + 1} - {dryer['cfm']} CFM"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**CFM:** {dryer['cfm']}")
                    st.write(f"**Outlet Diameter:** {dryer['outlet_diameter']} inches")
                with col2:
                    st.write(f"**Connector Length:** {dryer['connector_length']} feet")
                    st.write(f"**Total K-value:** {dryer['total_k']:.2f}")
                with col3:
                    if st.button(f"Remove Dryer #{idx + 1}", key=f"remove_{idx}"):
                        st.session_state.dryers.pop(idx)
                        st.rerun()
        
        st.markdown("---")
    
    # Add new dryer form
    if len(st.session_state.dryers) < 20:
        st.subheader("Add New Dryer")
        
        with st.form("add_dryer_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                cfm = st.number_input("Dryer CFM*", min_value=50, max_value=5000, value=200, step=50)
                outlet_diameter = st.number_input("Dryer Outlet Diameter (inches)*", min_value=3, max_value=12, value=4, step=1)
            
            with col2:
                connector_length = st.number_input("Connector Length (feet)*", min_value=1, max_value=100, value=10, step=1)
                additional_k = st.number_input("Additional K-value (lint collector, etc.)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            
            with col3:
                st.markdown("**Connector Fittings**")
                num_90_elbows = st.number_input("90° Elbows", min_value=0, max_value=10, value=2, step=1)
                num_45_elbows = st.number_input("45° Elbows", min_value=0, max_value=10, value=0, step=1)
                num_30_elbows = st.number_input("30° Elbows", min_value=0, max_value=10, value=0, step=1)
                num_lateral_tees = st.number_input("Lateral Tees", min_value=0, max_value=5, value=1, step=1)
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                copy_count = st.number_input("Number of copies to add", min_value=1, max_value=20, value=1, step=1)
            
            submitted = st.form_submit_button("Add Dryer(s)", type="primary")
            
            if submitted:
                # Calculate total K-value
                k_total = (
                    num_90_elbows * K_VALUES["90° Elbow"] +
                    num_45_elbows * K_VALUES["45° Elbow"] +
                    num_30_elbows * K_VALUES["30° Elbow"] +
                    num_lateral_tees * K_VALUES["Lateral Tee"] +
                    K_VALUES["Entry (flush)"] +
                    K_VALUES["Exit"] +
                    additional_k
                )
                
                # Create fittings summary
                fittings = []
                if num_90_elbows > 0:
                    fittings.append(f"{num_90_elbows}x 90° Elbow")
                if num_45_elbows > 0:
                    fittings.append(f"{num_45_elbows}x 45° Elbow")
                if num_30_elbows > 0:
                    fittings.append(f"{num_30_elbows}x 30° Elbow")
                if num_lateral_tees > 0:
                    fittings.append(f"{num_lateral_tees}x Lateral Tee")
                fittings.append("Entry + Exit")
                fittings_summary = ", ".join(fittings)
                
                # Calculate velocity and pressure loss
                velocity = calculate_velocity(cfm, outlet_diameter)
                dp = calculate_duct_pressure_loss(connector_length, outlet_diameter, velocity, k_total)
                
                # Create dryer object
                dryer_obj = {
                    'cfm': cfm,
                    'outlet_diameter': outlet_diameter,
                    'connector_length': connector_length,
                    'additional_k': additional_k,
                    'total_k': k_total,
                    'connector_fittings_summary': fittings_summary,
                    'connector_velocity': velocity,
                    'connector_dp': dp
                }
                
                # Add copies
                for _ in range(min(copy_count, 20 - len(st.session_state.dryers))):
                    st.session_state.dryers.append(dryer_obj.copy())
                
                st.rerun()
    
    else:
        st.warning("Maximum of 20 dryers reached.")
    
    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Back to Project Info"):
            st.session_state.step = 'project_info'
            st.rerun()
    
    with col3:
        if st.session_state.dryers:
            if st.button("Continue to Manifold ➡️", type="primary"):
                st.session_state.step = 'manifold_input'
                st.rerun()
        else:
            st.info("Add at least one dryer to continue")

def show_manifold_input_screen():
    """Display manifold input screen"""
    st.header("Manifold Duct Information")
    st.markdown(f"**Project:** {st.session_state.project_info.get('name', 'N/A')}")
    st.markdown(f"**Total Dryers:** {len(st.session_state.dryers)}")
    
    total_cfm = sum(d['cfm'] for d in st.session_state.dryers)
    st.markdown(f"**Total System CFM:** {total_cfm} CFM")
    
    with st.form("manifold_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            manifold_length = st.number_input("Manifold Length (feet)*", min_value=1, max_value=500, value=50, step=5)
            optimize_diameter = st.checkbox("Optimize manifold diameter (target 1.0 IN WC max)", value=True)
            
            if not optimize_diameter:
                manifold_diameter = st.number_input("Manifold Diameter (inches)*", min_value=6, max_value=36, value=12, step=2)
            else:
                manifold_diameter = None
                st.info("Diameter will be automatically optimized for 1.0 IN WC maximum pressure loss")
        
        with col2:
            st.markdown("**Manifold Fittings**")
            st.info("Note: Do NOT count straight-through tees. Only count lateral tees (change of direction).")
            num_90_elbows = st.number_input("90° Elbows", min_value=0, max_value=20, value=2, step=1, key="m_90")
            num_45_elbows = st.number_input("45° Elbows", min_value=0, max_value=20, value=0, step=1, key="m_45")
            num_30_elbows = st.number_input("30° Elbows", min_value=0, max_value=20, value=0, step=1, key="m_30")
            num_lateral_tees = st.number_input("Lateral Tees (change of direction only)", min_value=0, max_value=20, value=0, step=1, key="m_tee")
            additional_k_manifold = st.number_input("Additional K-value (lint collector, etc.)", min_value=0.0, max_value=10.0, value=0.0, step=0.1, key="m_addk")
        
        submitted = st.form_submit_button("Calculate System ➡️", type="primary")
        
        if submitted:
            # Calculate total K-value for manifold (no straight-through tees)
            k_total_manifold = (
                num_90_elbows * K_VALUES["90° Elbow"] +
                num_45_elbows * K_VALUES["45° Elbow"] +
                num_30_elbows * K_VALUES["30° Elbow"] +
                num_lateral_tees * K_VALUES["Lateral Tee"] +
                K_VALUES["Entry (flush)"] +
                K_VALUES["Exit"] +
                additional_k_manifold
            )
            
            # Create fittings summary
            fittings = []
            if num_90_elbows > 0:
                fittings.append(f"{num_90_elbows}x 90° Elbow")
            if num_45_elbows > 0:
                fittings.append(f"{num_45_elbows}x 45° Elbow")
            if num_30_elbows > 0:
                fittings.append(f"{num_30_elbows}x 30° Elbow")
            if num_lateral_tees > 0:
                fittings.append(f"{num_lateral_tees}x Lateral Tee")
            fittings.append("Entry + Exit")
            fittings_summary = ", ".join(fittings)
            
            # Optimize or use specified diameter
            if optimize_diameter:
                opt_diameter, velocity, dp = optimize_manifold_diameter(total_cfm, manifold_length, k_total_manifold)
                manifold_diameter = opt_diameter
            else:
                velocity = calculate_velocity(total_cfm, manifold_diameter)
                dp = calculate_duct_pressure_loss(manifold_length, manifold_diameter, velocity, k_total_manifold)
            
            # Save manifold info
            st.session_state.manifold_info = {
                'length': manifold_length,
                'diameter': manifold_diameter,
                'optimize': optimize_diameter,
                'fittings_summary': fittings_summary,
                'additional_k': additional_k_manifold,
                'total_k': k_total_manifold
            }
            
            # Calculate results
            worst_connector_dp = max(d['connector_dp'] for d in st.session_state.dryers)
            total_system_dp = worst_connector_dp + dp
            
            # Select fan
            suitable_fans = select_def_fan(total_cfm, total_system_dp)
            
            st.session_state.calculation_results = {
                'total_cfm': total_cfm,
                'worst_connector_dp': worst_connector_dp,
                'manifold_dp': dp,
                'manifold_velocity': velocity,
                'manifold_total_k': k_total_manifold,
                'total_system_dp': total_system_dp,
                'suitable_fans': suitable_fans,
                'selected_fan': suitable_fans[0] if suitable_fans else None
            }
            
            st.session_state.step = 'results'
            st.rerun()
    
    # Navigation
    st.markdown("---")
    if st.button("⬅️ Back to Dryer Input"):
        st.session_state.step = 'dryer_input'
        st.rerun()

def show_results_screen():
    """Display results and generate reports"""
    st.header("System Calculation Results")
    st.markdown(f"**Project:** {st.session_state.project_info.get('name', 'N/A')}")
    
    results = st.session_state.calculation_results
    
    # System Summary
    st.subheader("📊 System Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total System CFM", f"{results['total_cfm']:.0f}")
    with col2:
        st.metric("Manifold Diameter", f"{st.session_state.manifold_info['diameter']}\"")
    with col3:
        st.metric("Manifold Velocity", f"{results['manifold_velocity']:.0f} FPM")
    with col4:
        st.metric("Total System ΔP", f"{results['total_system_dp']:.3f} IN WC")
    
    st.markdown("---")
    
    # Pressure Loss Breakdown
    st.subheader("📉 Pressure Loss Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Worst Case Connector Loss",
            f"{results['worst_connector_dp']:.3f} IN WC",
            delta=f"{results['worst_connector_dp'] - DRYER_CONNECTOR_MAX_DP:.3f} IN WC" if results['worst_connector_dp'] > DRYER_CONNECTOR_MAX_DP else None,
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "Manifold Loss",
            f"{results['manifold_dp']:.3f} IN WC",
            delta=f"{results['manifold_dp'] - MANIFOLD_MAX_DP:.3f} IN WC" if results['manifold_dp'] > MANIFOLD_MAX_DP else None,
            delta_color="inverse"
        )
    
    # Warnings
    if results['worst_connector_dp'] > DRYER_CONNECTOR_MAX_DP:
        st.warning(f"⚠️ **WARNING:** Worst case dryer connector pressure loss ({results['worst_connector_dp']:.3f} IN WC) exceeds recommended maximum of {DRYER_CONNECTOR_MAX_DP} IN WC. Consider reducing connector length, increasing diameter, or adding a booster fan.")
    
    if results['manifold_dp'] > MANIFOLD_MAX_DP:
        st.error(f"❌ **ERROR:** Manifold pressure loss ({results['manifold_dp']:.3f} IN WC) exceeds maximum of {MANIFOLD_MAX_DP} IN WC. Increase manifold diameter.")
    
    st.markdown("---")
    
    # Fan Selection
    st.subheader("🔧 Fan Selection")
    
    if results['selected_fan']:
        fan = results['selected_fan']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.success(f"**Recommended Fan:** {fan['model']}")
            st.write(f"**Available CFM at Operating Point:** {fan['available_cfm']:.0f} CFM")
            st.write(f"**Design Margin:** {fan['margin']:.1f}%")
            st.write(f"**Maximum Fan Capacity:** {fan['max_cfm']:.0f} CFM @ {fan['max_sp']:.2f} IN WC")
        
        with col2:
            # Show fan curve visualization
            st.info("Fan operating point within acceptable range")
        
        # Show alternative fans if available
        if len(results['suitable_fans']) > 1:
            with st.expander("View Alternative Fan Options"):
                for alt_fan in results['suitable_fans'][1:4]:  # Show up to 3 alternatives
                    st.write(f"**{alt_fan['model']}** - {alt_fan['available_cfm']:.0f} CFM @ operating point ({alt_fan['margin']:.1f}% margin)")
    
    else:
        st.error("❌ No suitable DEF fan found for the system requirements. System pressure loss may be too high or CFM too low.")
    
    st.markdown("---")
    
    # Generate Reports
    st.subheader("📄 Download Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Generate PDF Report", type="primary"):
            pdf_buffer = generate_pdf_report(
                st.session_state.project_info,
                st.session_state.dryers,
                st.session_state.manifold_info,
                results
            )
            
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_buffer,
                file_name=f"DREX_Report_{st.session_state.project_info.get('name', 'Project').replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
    
    with col2:
        if st.button("Generate CSI Specification"):
            csi_spec = generate_csi_specification(
                st.session_state.project_info,
                st.session_state.dryers,
                st.session_state.manifold_info,
                results
            )
            
            st.download_button(
                label="📥 Download CSI Specification",
                data=csi_spec,
                file_name=f"CSI_Spec_113100_{st.session_state.project_info.get('name', 'Project').replace(' ', '_')}.txt",
                mime="text/plain"
            )
    
    # Navigation
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("⬅️ Back to Manifold Input"):
            st.session_state.step = 'manifold_input'
            st.rerun()
    
    with col2:
        if st.button("🏠 Start New Project"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
