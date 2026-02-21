from fpdf import FPDF

# -----------------------------
# Export Full Health Report PDF
# -----------------------------
def export_full_report(result, filename="health_report.pdf"):

    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "AI Personalized Diet Plan Generator", ln=True, align="C")
    pdf.ln(10)

    # -----------------------------
    # Health Summary
    # -----------------------------
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Health Report", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, f"Diabetes Probability: {result['Probability']:.2f}", ln=True)
    pdf.cell(200, 10, f"Risk Level: {result['Risk']}", ln=True)
    pdf.ln(5)

    # -----------------------------
    # Diet Plan Section
    # -----------------------------
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Personalized Diet Plan", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)

    for key, value in result["Diet Plan"].items():
        pdf.cell(200, 10, f"{key}: {value}", ln=True)

    pdf.ln(5)

    # -----------------------------
    # Optional Prescription Rules
    # -----------------------------
    if "Prescription Rules" in result:

        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, "Doctor Prescription Guidelines", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", size=12)

        for rule in result["Prescription Rules"]:
            pdf.multi_cell(0, 10, f"- {rule}")

    pdf.output(filename)

    return filename
