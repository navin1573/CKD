import io
import json
import matplotlib
matplotlib.use('Agg')  # Set headless backend for matplotlib
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_prediction_pdf(prediction):
    """
    Generates a professional clinical PDF report for a kidney disease prediction,
    complete with a dynamically plotted SHAP feature contribution bar chart.
    """
    buffer = io.BytesIO()
    
    # Initialize document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Styles for clinical theme
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#1e3a8a'), # Indigo
        spaceAfter=15,
        alignment=1 # Center
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#0f766e'), # Teal
        spaceBefore=10,
        spaceAfter=6
    )
    
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#374151') # Gray-700
    )
    
    bold_style = ParagraphStyle(
        'BoldText',
        parent=normal_style,
        fontName='Helvetica-Bold'
    )
    
    # 1. Header Band
    story.append(Paragraph("AI-BASED CHRONIC KIDNEY DISEASE DIAGNOSTIC REPORT", title_style))
    story.append(Paragraph("<b>Explainable AI (XAI) Patient Diagnostic Summary</b>", ParagraphStyle('Sub', parent=title_style, fontSize=12, spaceAfter=20)))
    
    # 2. Patient & Doctor Info Table
    patient_name = f"{prediction.patient.user.first_name} {prediction.patient.user.last_name}".strip() or prediction.patient.user.username
    doctor_name = f"Dr. {prediction.doctor.user.first_name} {prediction.doctor.user.last_name}".strip() if prediction.doctor else "Self Assessment"
    
    info_data = [
        [Paragraph("<b>Patient Name:</b>", normal_style), Paragraph(patient_name, normal_style),
         Paragraph("<b>Date of Report:</b>", normal_style), Paragraph(prediction.prediction_date.strftime("%Y-%m-%d %H:%M"), normal_style)],
        [Paragraph("<b>Email:</b>", normal_style), Paragraph(prediction.patient.user.email or "N/A", normal_style),
         Paragraph("<b>Assigned Physician:</b>", normal_style), Paragraph(doctor_name, normal_style)],
        [Paragraph("<b>Age:</b>", normal_style), Paragraph(f"{prediction.age or 'N/A'} yrs", normal_style),
         Paragraph("<b>Diagnosis Status:</b>", normal_style), Paragraph("<b>CKD DETECTED</b>" if prediction.predicted_class == 'ckd' else "NO CKD DETECTED", normal_style)]
    ]
    
    info_table = Table(info_data, colWidths=[100, 160, 100, 160])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 15))
    
    # 3. Prediction Result Callout box
    risk_color = '#dc2626' if prediction.risk_level == 'HIGH' else ('#d97706' if prediction.risk_level == 'MEDIUM' else '#059669')
    result_box_data = [
        [
            Paragraph(f"<font size=14 color='{risk_color}'><b>Diagnosis: {prediction.predicted_class.upper()}</b></font>", bold_style),
            Paragraph(f"<b>Prediction Probability:</b> {prediction.prediction_probability * 100:.2f}%", normal_style),
            Paragraph(f"<b>Risk Category:</b> <font color='{risk_color}'><b>{prediction.risk_level}</b></font>", normal_style)
        ]
    ]
    result_table = Table(result_box_data, colWidths=[200, 180, 140])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f9fafb')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor(risk_color)),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    
    story.append(result_table)
    story.append(Spacer(1, 15))
    
    # 4. Critical Lab Features Table
    story.append(Paragraph("Laboratory Test Metrics", section_heading))
    lab_data = [
        [Paragraph("<b>Biomarker</b>", bold_style), Paragraph("<b>Observed Value</b>", bold_style),
         Paragraph("<b>Biomarker</b>", bold_style), Paragraph("<b>Observed Value</b>", bold_style)]
    ]
    
    # Helper to clean value outputs
    def fmt(val):
        return str(val) if val is not None else "N/A"
        
    features_list = [
        ("Serum Creatinine (sc)", f"{fmt(prediction.sc)} mg/dL", "Hemoglobin (hemo)", f"{fmt(prediction.hemo)} g/dL"),
        ("Blood Pressure (bp)", f"{fmt(prediction.bp)} mm/Hg", "Specific Gravity (sg)", fmt(prediction.sg)),
        ("Albumin (al)", fmt(prediction.al), "Sugar (su)", fmt(prediction.su)),
        ("Blood Glucose Random (bgr)", f"{fmt(prediction.bgr)} mg/dL", "Blood Urea (bu)", f"{fmt(prediction.bu)} mg/dL"),
        ("Sodium (sod)", f"{fmt(prediction.sod)} mEq/L", "Potassium (pot)", f"{fmt(prediction.pot)} mEq/L"),
        ("Red Blood Cells (rbc)", fmt(prediction.rbc), "Pus Cells (pc)", fmt(prediction.pc)),
        ("Hypertension (htn)", fmt(prediction.htn), "Diabetes Mellitus (dm)", fmt(prediction.dm)),
    ]
    
    for row in features_list:
        lab_data.append([
            Paragraph(row[0], normal_style), Paragraph(row[1], normal_style),
            Paragraph(row[2], normal_style), Paragraph(row[3], normal_style)
        ])
        
    lab_table = Table(lab_data, colWidths=[150, 110, 150, 110])
    lab_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f3f4f6')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    
    story.append(lab_table)
    story.append(Spacer(1, 20))
    
    # 5. Explainable AI SHAP Chart
    story.append(Paragraph("Explainable AI (SHAP) Feature Contributions", section_heading))
    story.append(Paragraph("The chart below illustrates how much each biomarker influenced this specific diagnosis. Red/positive values increase the kidney disease risk score, while blue/negative values lower it.", normal_style))
    story.append(Spacer(1, 10))
    
    # Render Matplotlib SHAP chart
    try:
        explanation = prediction.explanation
        shap_data = json.loads(explanation.shap_values_json)
        
        # Take top 8 contributors to keep chart clean in PDF
        top_shap = shap_data[:8]
        
        features = [item['feature'] for item in top_shap][::-1]
        shap_vals = [item['shap_value'] for item in top_shap][::-1]
        
        # Color red for positive contributions, blue for negative contributions
        bar_colors = ['#ef4444' if val >= 0 else '#3b82f6' for val in shap_vals]
        
        plt.figure(figsize=(6.5, 2.5))
        plt.barh(features, shap_vals, color=bar_colors, edgecolor='none', height=0.6)
        plt.axvline(x=0, color='#9ca3af', linestyle='--', linewidth=0.8)
        plt.title('Top Biomarkers Influencing the Diagnostic Model', fontsize=10, fontweight='bold', color='#1f2937')
        plt.xlabel('SHAP Contribution Weight', fontsize=8, color='#4b5563')
        plt.tick_params(axis='both', which='major', labelsize=8)
        plt.tight_layout()
        
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png', dpi=200)
        img_buf.seek(0)
        plt.close()
        
        # Add plotted image to story
        story.append(Image(img_buf, width=480, height=184))
        
    except Exception as e:
        story.append(Paragraph(f"<i>Error rendering explanation chart: {str(e)}</i>", normal_style))
        
    # Build Document
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
