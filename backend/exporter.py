from reportlab.pdfgen import canvas
import json

def generate_pdf_report(data, filepath):
    c = canvas.Canvas(filepath)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "AI Personalized Diet Plan")
    
    c.setFont("Helvetica", 12)
    y_position = 750
    for rule in data['diet_plan']:
        c.drawString(100, y_position, f"• {rule}")
        y_position -= 20
    c.save()

def generate_json_report(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)