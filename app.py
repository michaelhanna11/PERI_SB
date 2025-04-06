import streamlit as st
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import requests
import os
import io
from datetime import datetime

# Program metadata
PROGRAM_VERSION = "1.0 - 2025"
PROGRAM = "Brace Frame Load Calculator"
COMPANY_NAME = "tekhne Consulting Engineers"
COMPANY_ADDRESS = "   "  # Update with actual address if needed
LOGO_URL = "https://drive.google.com/uc?export=download&id=1VebdT2loVGX57noP9t2GgQhwCNn8AA3h"
FALLBACK_LOGO_URL = "https://onedrive.live.com/download?cid=A48CC9068E3FACE0&resid=A48CC9068E3FACE0%21s252b6fb7fcd04f53968b2a09114d33ed"

# Brace frame data (unchanged, abbreviated for brevity)
brace_frame_data = {
    "SB-A+B": {
        "heights": [3.75, 4.00, 4.25, 4.50, 4.75, 5.00, 5.25, 5.50, 5.75, 6.00],
        "pressures": [40, 50, 60],
        "data": {
            5.50: {40: {"e": 1.90, "Z": 266, "V1": 72, "V2": 140, "f": 7},
                   50: {"e": 1.59, "Z": 318, "V1": 98, "V2": 161, "f": 9},
                   60: {"e": 1.39, "Z": 365, "V1": 105, "V2": 178, "f": 9}},
            # ... (other heights omitted for brevity)
        }
    },
    # ... (other brace types omitted for brevity)
    "SB-2": {
        "heights": [3.50, 3.75, 4.00, 4.25, 4.50, 4.75, 5.00, 5.25, 5.50, 5.75, 6.00],
        "pressures": [30, 40, 50],
        "data": {
            5.00: {30: {"e": 1.25, "Z": 186, "V1": 48, "V2": 98, "f": 4},
                   40: {"e": 1.25, "Z": 238, "V1": 63, "V2": 120, "f": 6},
                   50: {"e": 1.25, "Z": 283, "V1": 78, "V2": 135, "f": 6}},
            # ... (other heights omitted for brevity)
        }
    }
}

def interpolate_value(x, x0, x1, y0, y1):
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

def get_loads(brace_type, height, pressure):
    if brace_type not in brace_frame_data:
        return "Brace frame type not supported."
    
    data = brace_frame_data[brace_type]["data"]
    heights = brace_frame_data[brace_type]["heights"]
    pressures = brace_frame_data[brace_type]["pressures"]

    if height < min(heights) or height > max(heights) or pressure < min(pressures) or pressure > max(pressures):
        return f"Input out of range for {brace_type}. Height range: {min(heights)}-{max(heights)} m, Pressure range: {min(pressures)}-{max(pressures)} kN/m²."

    h_low = max([h for h in heights if h <= height])
    h_high = min([h for h in heights if h >= height])
    p_low = max([p for p in pressures if p <= pressure])
    p_high = min([p for p in pressures if p >= pressure])

    if h_high not in data or p_high not in data[h_high]:
        return f"Data not available for {brace_type} at height {h_high} m and pressure {p_high} kN/m²."

    if h_low == h_high and p_low == p_high:
        return data[h_low][p_low]

    if h_low == h_high:
        loads_low = data[h_low][p_low]
        loads_high = data[h_low][p_high]
        result = {}
        for key in ["e", "Z", "V1", "V2", "f"]:
            result[key] = interpolate_value(pressure, p_low, p_high, loads_low[key], loads_high[key])
        return result
    elif p_low == p_high:
        loads_low = data[h_low][p_low]
        loads_high = data[h_high][p_low]
        result = {}
        for key in ["e", "Z", "V1", "V2", "f"]:
            result[key] = interpolate_value(height, h_low, h_high, loads_low[key], loads_high[key])
        return result
    else:
        loads_ll = data[h_low][p_low]
        loads_lh = data[h_low][p_high] if p_high in data[h_low] else data[h_low][p_low]
        loads_hl = data[h_high][p_low]
        loads_hh = data[h_high][p_high] if p_high in data[h_high] else data[h_high][p_low]
        result = {}
        for key in ["e", "Z", "V1", "V2", "f"]:
            low_interp = interpolate_value(pressure, p_low, p_high, loads_ll[key], loads_lh[key]) if p_high in data[h_low] else loads_ll[key]
            high_interp = interpolate_value(pressure, p_low, p_high, loads_hl[key], loads_hh[key]) if p_high in data[h_high] else loads_hl[key]
            result[key] = interpolate_value(height, h_low, h_high, low_interp, high_interp)
        return result

def validate_bracing(brace_type, height, e):
    validation_messages = []
    if "SB-" in brace_type and ("A" in brace_type or "B" in brace_type or "C" in brace_type):
        validation_messages.append("Recommendation: Pre-incline the Brace Frame by 2/3 of the calculated deflection.")
    if brace_type == "SB-A+B":
        if e <= 1.35 and height <= 5.25:
            validation_messages.append("Diagonal Bracing B can be omitted during concreting.")
        else:
            validation_messages.append("Required: Diagonal Bracing A and B for concreting.")
        validation_messages.append("Required: Diagonal Bracing for moving and lifting the formwork unit with the crane.")
    # ... (other validation rules omitted for brevity)
    elif brace_type == "SB-2":
        if height >= 5.00:
            validation_messages.append("Required: Diagonal Bracing for concreting (height ≥ 5.00 m).")
        else:
            validation_messages.append("No diagonal bracing required for concreting (height < 5.00 m).")
        validation_messages.append("Required: Diagonal Bracing for moving and lifting the formwork unit with the crane.")
        if e > 1.25:
            validation_messages.append("Warning: Permissible width of influence exceeds maximum of 1.25 m.")
    return validation_messages

def build_pdf_elements(brace_type, height, pressure, result, validation_messages, project_number, project_name):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='TitleStyle', parent=styles['Title'], fontSize=14, spaceAfter=8, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle(name='SubtitleStyle', parent=styles['Normal'], fontSize=10, spaceAfter=8, alignment=TA_CENTER)
    heading_style = ParagraphStyle(name='HeadingStyle', parent=styles['Heading2'], fontSize=12, spaceAfter=6)
    normal_style = ParagraphStyle(name='NormalStyle', parent=styles['Normal'], fontSize=9, spaceAfter=6)
    table_header_style = ParagraphStyle(name='TableHeaderStyle', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', alignment=TA_LEFT)
    table_cell_style = ParagraphStyle(name='TableCellStyle', parent=styles['Normal'], fontSize=8, alignment=TA_LEFT, leading=8)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])

    elements = []
    logo_file = "logo.png"
    if not os.path.exists(logo_file):
        for url in [LOGO_URL, FALLBACK_LOGO_URL]:
            try:
                response = requests.get(url, stream=True, allow_redirects=True, timeout=10)
                if 'image' in response.headers.get('Content-Type', '').lower():
                    response.raise_for_status()
                    with open(logo_file, 'wb') as f:
                        f.write(response.content)
                    break
            except Exception:
                continue

    company_text = f"<b>{COMPANY_NAME}</b><br/>{COMPANY_ADDRESS}"
    company_paragraph = Paragraph(company_text, normal_style)
    logo = Image(logo_file, width=50*mm, height=20*mm) if os.path.exists(logo_file) else Paragraph("[Logo Placeholder]", normal_style)
    header_data = [[logo, company_paragraph]]
    header_table = Table(header_data, colWidths=[60*mm, 120*mm])
    header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('ALIGN', (1, 0), (1, 0), 'CENTER')]))
    elements.extend([header_table, Spacer(1, 4*mm), Paragraph("Brace Frame Load Calculation Report", title_style)])

    project_details = f"Project Number: {project_number}<br/>Project Name: {project_name}<br/>Date: {datetime.now().strftime('%B %d, %Y')}"
    elements.extend([Paragraph(project_details, subtitle_style), Spacer(1, 2*mm), Paragraph("Input Parameters", heading_style)])

    input_data = [
        ["Parameter", "Value"],
        ["Brace Frame Type", brace_type],
        ["Concreting Height (m)", f"{height:.2f}"],
        ["Fresh Concrete Pressure (kN/m²)", f"{pressure:.2f}"],
    ]
    input_table = Table([[Paragraph(row[0], table_header_style if i == 0 else table_cell_style),
                          Paragraph(row[1], table_header_style if i == 0 else table_cell_style)] for i, row in enumerate(input_data)],
                        colWidths=[100*mm, 80*mm])
    input_table.setStyle(table_style)
    elements.extend([input_table, Spacer(1, 4*mm), Paragraph("Calculated Loads (Per Meter)", heading_style)])

    loads_data = [
        ["Parameter", "Value"],
        ["Permissible Width of Influence (e)", f"{result['e']:.2f} m"],
        ["Anchor Tension Force (Z)", f"{result['Z']:.2f} kN/m"],
        ["Spindle Force V1", f"{result['V1']:.2f} kN/m"],
        ["Spindle Force V2", f"{result['V2']:.2f} kN/m"],
        ["Deflection (f)", f"{result['f']:.2f} mm/m"],
    ]
    loads_table = Table([[Paragraph(row[0], table_header_style if i == 0 else table_cell_style),
                          Paragraph(row[1], table_header_style if i == 0 else table_cell_style)] for i, row in enumerate(loads_data)],
                        colWidths=[100*mm, 80*mm])
    loads_table.setStyle(table_style)
    elements.extend([loads_table, Spacer(1, 4*mm), Paragraph(f"Final Values Based on {result['e']:.2f} m Spacing", heading_style)])

    final_data = [
        ["Parameter", "Value"],
        ["Anchor Tension Force (Z)", f"{result['Z'] * result['e']:.2f} kN"],
        ["Spindle Force V1", f"{result['V1'] * result['e']:.2f} kN"],
        ["Spindle Force V2", f"{result['V2'] * result['e']:.2f} kN"],
        ["Deflection (f)", f"{result['f'] * result['e']:.2f} mm"],
    ]
    final_table = Table([[Paragraph(row[0], table_header_style if i == 0 else table_cell_style),
                          Paragraph(row[1], table_header_style if i == 0 else table_cell_style)] for i, row in enumerate(final_data)],
                        colWidths=[100*mm, 80*mm])
    final_table.setStyle(table_style)
    elements.extend([final_table, Spacer(1, 4*mm), Paragraph("Validation and Notes", heading_style)])

    notes_data = [["Notes"]] + [[Paragraph(msg, table_cell_style)] for msg in validation_messages]
    notes_table = Table(notes_data, colWidths=[180*mm])
    notes_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(notes_table)
    return elements

def generate_pdf_report(brace_type, height, pressure, result, validation_messages, project_number, project_name):
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    elements = build_pdf_elements(brace_type, height, pressure, result, validation_messages, project_number, project_name)

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        page_num = canvas.getPageNumber()
        canvas.drawCentredString(doc.pagesize[0] / 2.0, 10 * mm, f"{PROGRAM} {PROGRAM_VERSION} | tekhne © | Page {page_num}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# Streamlit app
st.title("Brace Frame Load Calculator")

# Sidebar for inputs
st.sidebar.header("Input Parameters")
brace_type = st.sidebar.selectbox("Brace Frame Type", list(brace_frame_data.keys()))
height = st.sidebar.number_input("Concreting Height (m)", min_value=2.50, max_value=8.75, step=0.01, value=5.50)
pressure = st.sidebar.number_input("Fresh Concrete Pressure (kN/m²)", min_value=30, max_value=60, step=1, value=60)
project_number = st.sidebar.text_input("Project Number", "PRJ-001")
project_name = st.sidebar.text_input("Project Name", "Sample Project")

# Calculate loads
result = get_loads(brace_type, height, pressure)

# Display results
st.header("Results")
if isinstance(result, str):
    st.error(result)
else:
    st.write(f"**Brace Frame:** {brace_type}")
    st.write(f"**Concreting Height:** {height} m")
    st.write(f"**Fresh Concrete Pressure:** {pressure} kN/m²")
    
    st.subheader("Calculated Loads (Per Meter)")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Permissible Width of Influence (e): **{result['e']:.2f} m**")
        st.write(f"Anchor Tension Force (Z): **{result['Z']:.2f} kN/m**")
        st.write(f"Spindle Force V1: **{result['V1']:.2f} kN/m**")
    with col2:
        st.write(f"Spindle Force V2: **{result['V2']:.2f} kN/m**")
        st.write(f"Deflection (f): **{result['f']:.2f} mm/m**")

    st.subheader(f"Final Values Based on {result['e']:.2f} m Spacing")
    final_Z = result['Z'] * result['e']
    final_V1 = result['V1'] * result['e']
    final_V2 = result['V2'] * result['e']
    final_f = result['f'] * result['e']
    col3, col4 = st.columns(2)
    with col3:
        st.write(f"Anchor Tension Force (Z): **{final_Z:.2f} kN**")
        st.write(f"Spindle Force V1: **{final_V1:.2f} kN**")
    with col4:
        st.write(f"Spindle Force V2: **{final_V2:.2f} kN**")
        st.write(f"Deflection (f): **{final_f:.2f} mm**")

    st.subheader("Validation and Notes")
    validation_messages = validate_bracing(brace_type, height, result['e'])
    for message in validation_messages:
        if "Warning" in message:
            st.warning(message)
        elif "Required" in message:
            st.info(message)
        else:
            st.success(message)

    # Generate and offer PDF download
    pdf_data = generate_pdf_report(brace_type, height, pressure, result, validation_messages, project_number, project_name)
    if pdf_data:
        st.download_button(
            label="Download PDF Report",
            data=pdf_data,
            file_name=f"Brace_Frame_Calculation_Report_{project_name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )

# Sidebar notes
st.sidebar.markdown("---")
st.sidebar.write("**Notes:**")
st.sidebar.write("- Values are interpolated if not exact matches.")
st.sidebar.write("- Ensure inputs are within the supported ranges for each brace type.")
st.sidebar.write("- All values refer to a width of influence of 1.00 m unless otherwise specified.")
st.sidebar.write("- Final values are calculated by multiplying loads and deflection by the permissible width of influence (e).")
