from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io


def export_full_report(result):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("AI Health Diet Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    # Extract values safely
    extracted_text = result.get("Extracted Text", "Not available")
    rules = result.get("Diet Rules", {})
    diet_plan = result.get("Diet Plan", {})

    # Prescription text
    elements.append(Paragraph("Doctor Prescription:", styles["Heading2"]))
    elements.append(Paragraph(extracted_text, styles["Normal"]))
    elements.append(Spacer(1, 10))

    # Diet rules
    elements.append(Paragraph("Diet Rules:", styles["Heading2"]))
    for key, value in rules.items():
        elements.append(Paragraph(f"{key}: {value}", styles["Normal"]))
    elements.append(Spacer(1, 10))

    # Weekly diet plan
    elements.append(Paragraph("1 Week Diet Plan:", styles["Heading2"]))

    for day, meals in diet_plan.items():
        elements.append(Paragraph(day, styles["Heading3"]))

        for meal, food in meals.items():
            elements.append(Paragraph(f"{meal}: {food}", styles["Normal"]))

        elements.append(Spacer(1, 10))

    doc.build(elements)
    buffer.seek(0)

    return buffer
