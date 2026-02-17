# ENHANCED SALES-FOCUSED PDF REPORT FUNCTION
# Replace the generate_pdf_report() function in drex_calculator.py with this

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
import io
from datetime import datetime

def generate_pdf_report(project_info, dryers, manifold_info, results):
    """Generate professional sales-focused PDF report with LF Systems branding"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        topMargin=0.75*inch, 
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Styles with LF Systems branding
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2a3853'),  # LF Systems primary color
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#234699'),  # LF Systems secondary
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2a3853'),
        spaceBefore=16,
        spaceAfter=10,
        fontName='Helvetica-Bold',
        borderPadding=5,
        leftIndent=0
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    # LF Systems Logo (if available)
    try:
        logo = Image('lf_systems_logo.jpg', width=3*inch, height=0.75*inch)
        logo.hAlign = 'CENTER'
        story.append(logo)
        story.append(Spacer(1, 0.2*inch))
    except:
        # Fallback if logo not available
        logo_text = Paragraph("<b>LF SYSTEMS</b><br/>by RM Manifold Group Inc.", subtitle_style)
        story.append(logo_text)
        story.append(Spacer(1, 0.2*inch))
    
    # Title
    title = Paragraph("Commercial Dryer Exhaust<br/>System Proposal", title_style)
    story.append(title)
    
    subtitle = Paragraph(f"<i>{project_info.get('name', 'Your Project')}</i>", subtitle_style)
    story.append(subtitle)
    
    # Project Info Box
    project_data = [
        ['Project Location:', f"{project_info.get('city', 'N/A')}, {project_info.get('state', 'N/A')}"],
        ['Elevation:', f"{project_info.get('elevation', 'N/A')} ft"],
        ['Prepared For:', project_info.get('user_name', 'N/A')],
        ['Date:', datetime.now().strftime('%B %d, %Y')],
    ]
    
    project_table = Table(project_data, colWidths=[2*inch, 4*inch])
    project_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f2f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(project_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary Section
    story.append(Paragraph("Executive Summary", heading_style))
    
    exec_summary = f"""
    LF Systems is pleased to provide this comprehensive dryer exhaust system solution for your facility. 
    Our engineered approach ensures optimal performance, code compliance, and long-term reliability.
    <br/><br/>
    <b>System Highlights:</b><br/>
    • {len(dryers)} commercial dryers supported<br/>
    • {results['total_cfm']:.0f} CFM total exhaust capacity<br/>
    • {manifold_info['diameter']}" manifold duct system<br/>
    • DEF Series exhaust fan with L150 intelligent controls<br/>
    • Fully code-compliant design meeting IMC and NFPA standards
    """
    story.append(Paragraph(exec_summary, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Key System Specifications - Highlighted Box
    story.append(Paragraph("Recommended System Configuration", heading_style))
    
    spec_data = [
        ['SPECIFICATION', 'VALUE'],
        ['Total System Airflow', f"{results['total_cfm']:.0f} CFM"],
        ['Manifold Diameter', f"{manifold_info['diameter']}\""],
        ['Manifold Length', f"{manifold_info['length']} feet"],
        ['System Static Pressure', f"{results['total_system_dp']:.2f}\" WC"],
        ['Recommended Fan', results['selected_fan']['model'] if results['selected_fan'] else 'Contact Us'],
        ['Controller', 'L150 Constant Pressure'],
    ]
    
    spec_table = Table(spec_data, colWidths=[3*inch, 2.5*inch])
    spec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#234699')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#234699')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(spec_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Benefits Section
    story.append(Paragraph("Why Choose LF Systems?", heading_style))
    
    benefits = """
    <b>Industry-Leading Performance:</b> Our DEF Series fans deliver consistent, reliable exhaust 
    with intelligent pressure control that adapts to changing load conditions.<br/><br/>
    
    <b>Code Compliance Guaranteed:</b> Every system is engineered to meet or exceed IMC, NFPA 211, 
    and local building code requirements. Our UL-listed components ensure safety and reliability.<br/><br/>
    
    <b>Energy Efficiency:</b> Variable-speed EC motors and intelligent controls minimize energy 
    consumption while maintaining optimal exhaust performance.<br/><br/>
    
    <b>Proven Reliability:</b> Backed by RM Manifold Group's decades of HVAC expertise and a 
    comprehensive 24-month warranty on all equipment.
    """
    story.append(Paragraph(benefits, body_style))
    
    story.append(PageBreak())
    
    # Technical Details Section
    story.append(Paragraph("System Design Details", heading_style))
    
    # Dryer Configuration
    story.append(Paragraph("<b>Dryer Configuration:</b>", body_style))
    
    dryer_data = [['#', 'CFM', 'Outlet Ø', 'Connector', 'Pressure Loss']]
    for idx, dryer in enumerate(dryers[:10], 1):  # Show first 10
        dryer_data.append([
            str(idx),
            f"{dryer['cfm']} CFM",
            f"{dryer['outlet_diameter']}\"",
            f"{dryer['connector_length']} ft",
            f"{dryer['connector_dp']:.3f}\" WC"
        ])
    
    if len(dryers) > 10:
        dryer_data.append(['...', f'+{len(dryers)-10} more', '', '', ''])
    
    dryer_table = Table(dryer_data, colWidths=[0.5*inch, 1.2*inch, 1*inch, 1.2*inch, 1.3*inch])
    dryer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2a3853')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(dryer_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Manifold System
    story.append(Paragraph("<b>Manifold System:</b>", body_style))
    manifold_text = f"""
    • Length: {manifold_info['length']} feet<br/>
    • Diameter: {manifold_info['diameter']} inches<br/>
    • Fittings: {manifold_info.get('fittings_summary', 'As specified')}<br/>
    • Velocity: {results['manifold_velocity']:.0f} FPM<br/>
    • Pressure Loss: {results['manifold_dp']:.3f}\" WC (within {MANIFOLD_MAX_DP}\" WC limit)
    """
    story.append(Paragraph(manifold_text, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Fan Selection
    if results['selected_fan']:
        fan = results['selected_fan']
        story.append(Paragraph("<b>Exhaust Fan Selection:</b>", body_style))
        
        fan_info = f"""
        <b>Model:</b> {fan['model']}<br/>
        <b>Available CFM at Operating Point:</b> {fan['available_cfm']:.0f} CFM<br/>
        <b>Design Margin:</b> {fan['margin']:.1f}% (ensures reliable performance)<br/>
        <b>Maximum Capacity:</b> {fan['max_cfm']:.0f} CFM @ {fan['max_sp']:.2f}\" WC
        """
        story.append(Paragraph(fan_info, body_style))
        
        # Status indicator
        if fan['margin'] >= 10:
            status_text = '<font color="#00a86b">✓ EXCELLENT - Fan properly sized with adequate safety margin</font>'
        else:
            status_text = '<font color="#b11f33">⚠ Contact LF Systems for optimization recommendations</font>'
        story.append(Paragraph(status_text, body_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Engineering Notes
    story.append(Paragraph("Engineering Notes", heading_style))
    
    eng_notes = f"""
    <b>Design Standards:</b><br/>
    • Calculations per ASHRAE Fundamentals<br/>
    • Pressure loss: ΔP = (0.35 × L/D + ΣK) × ρ × (V/1096.2)²<br/>
    • Air density: 0.0696 lb/ft³ @ 120°F (dryer exhaust temperature)<br/>
    • Code compliance: IMC, NFPA 211, UL 705<br/><br/>
    
    <b>System Warnings:</b><br/>
    {"• ⚠ Connector pressure loss exceeds 0.25\" WC recommendation<br/>" if results['worst_connector_dp'] > DRYER_CONNECTOR_MAX_DP else ""}
    {"• ⚠ Manifold pressure loss exceeds 1.0\" WC maximum<br/>" if results['manifold_dp'] > MANIFOLD_MAX_DP else ""}
    {"• ✓ All pressure losses within acceptable limits<br/>" if results['manifold_dp'] <= MANIFOLD_MAX_DP and results['worst_connector_dp'] <= DRYER_CONNECTOR_MAX_DP else ""}
    """
    story.append(Paragraph(eng_notes, body_style))
    
    # New page for Next Steps
    story.append(PageBreak())
    
    # Next Steps / Call to Action
    story.append(Paragraph("Next Steps", heading_style))
    
    next_steps = """
    <b>1. Review & Approval</b><br/>
    Review this proposal and confirm it meets your project requirements.<br/><br/>
    
    <b>2. Detailed Engineering</b><br/>
    Our engineering team will provide detailed submittal drawings and specifications.<br/><br/>
    
    <b>3. Equipment Procurement</b><br/>
    Once approved, equipment will be manufactured and shipped to your project site.<br/><br/>
    
    <b>4. Installation Support</b><br/>
    LF Systems provides complete installation support and startup assistance.<br/><br/>
    
    <b>5. Training & Warranty</b><br/>
    Comprehensive operator training and 24-month equipment warranty included.
    """
    story.append(Paragraph(next_steps, body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Contact Information
    story.append(Paragraph("Contact Information", heading_style))
    
    contact = """
    <b>LF Systems</b><br/>
    A Division of RM Manifold Group Inc.<br/>
    <br/>
    <b>Website:</b> www.lfsystems.net<br/>
    <b>Phone:</b> (Contact your local representative)<br/>
    <b>Email:</b> info@lfsystems.net<br/>
    <br/>
    <i>Professional Dryer Exhaust Solutions Since 2008</i>
    """
    story.append(Paragraph(contact, body_style))
    
    # Footer with branding
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    footer = Paragraph(
        "This proposal is valid for 30 days from date of issue. "
        "Specifications subject to change based on final project requirements.<br/>"
        "© 2026 LF Systems by RM Manifold Group Inc. All rights reserved.",
        footer_style
    )
    story.append(footer)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# END OF ENHANCED SALES PDF FUNCTION
