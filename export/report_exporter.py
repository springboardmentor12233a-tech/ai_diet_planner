"""
Report exporter for generating PDF and JSON outputs of diet plans.

This module provides the ReportExporter class for exporting diet plans
in professional PDF format and structured JSON format.
"""

import json
from io import BytesIO
from typing import Optional
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie

from ..models import DietPlan, PatientProfile


class ReportExporter:
    """
    Export diet plans in PDF and JSON formats.
    
    This class generates professional medical reports with patient information,
    health summaries, diet plans, and nutritional breakdowns.
    """
    
    def __init__(self):
        """Initialize the report exporter with default styles."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles for the report."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=1,  # Center
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12,
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#7F8C8D'),
            spaceAfter=8,
        ))
    
    def export_pdf(
        self,
        diet_plan: DietPlan,
        patient_info: Optional[PatientProfile] = None
    ) -> bytes:
        """
        Generate PDF report of diet plan.
        
        Args:
            diet_plan: Generated diet plan
            patient_info: Optional patient information for header
            
        Returns:
            PDF file as bytes
            
        Raises:
            ValueError: If diet plan is invalid
            RuntimeError: If PDF generation fails
        """
        if not diet_plan:
            raise ValueError("Diet plan cannot be None")
        
        if not diet_plan.meals:
            raise ValueError("Diet plan must contain at least one meal")
        
        try:
            # Create PDF in memory
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )
            
            # Build the document content
            story = []
            
            # Add title
            story.append(Paragraph(
                "Personalized Diet Plan Report",
                self.styles['CustomTitle']
            ))
            story.append(Spacer(1, 0.2 * inch))
            
            # Add patient information section
            if patient_info:
                story.extend(self._build_patient_info_section(patient_info))
            
            # Add health summary section
            story.extend(self._build_health_summary_section(diet_plan))
            
            # Add diet plan section
            story.extend(self._build_diet_plan_section(diet_plan))
            
            # Add nutritional breakdown section
            story.extend(self._build_nutritional_breakdown_section(diet_plan))
            
            # Add footer with disclaimers
            story.extend(self._build_footer_section(diet_plan))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            raise RuntimeError(f"PDF generation failed: {str(e)}") from e
    
    def _build_patient_info_section(
        self,
        patient_info: PatientProfile
    ) -> list:
        """Build patient information section."""
        elements = []
        
        elements.append(Paragraph(
            "Patient Information",
            self.styles['SectionHeader']
        ))
        
        # Create patient info table
        data = [
            ["Patient ID:", patient_info.patient_id],
            ["Age:", f"{patient_info.age} years"],
            ["Gender:", patient_info.gender.capitalize()],
            ["Height:", f"{patient_info.height_cm} cm"],
            ["Weight:", f"{patient_info.weight_kg} kg"],
            ["Activity Level:", patient_info.activity_level.replace('_', ' ').title()],
        ]
        
        if patient_info.preferences.dietary_style:
            data.append(["Dietary Style:", patient_info.preferences.dietary_style.capitalize()])
        
        if patient_info.preferences.allergies:
            data.append(["Allergies:", ", ".join(patient_info.preferences.allergies)])
        
        table = Table(data, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2C3E50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _build_health_summary_section(self, diet_plan: DietPlan) -> list:
        """Build health summary section."""
        elements = []
        
        elements.append(Paragraph(
            "Health Summary",
            self.styles['SectionHeader']
        ))
        
        # Health conditions
        if diet_plan.health_conditions:
            elements.append(Paragraph(
                "Detected Health Conditions:",
                self.styles['SubsectionHeader']
            ))
            
            conditions_data = [["Condition", "Confidence"]]
            for condition in diet_plan.health_conditions:
                condition_name = condition.condition_type.value.replace('_', ' ').title()
                confidence_pct = f"{condition.confidence * 100:.1f}%"
                conditions_data.append([condition_name, confidence_pct])
            
            table = Table(conditions_data, colWidths=[4 * inch, 2 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.2 * inch))
        
        # Dietary restrictions
        if diet_plan.restrictions:
            elements.append(Paragraph(
                "Dietary Restrictions:",
                self.styles['SubsectionHeader']
            ))
            
            for restriction in diet_plan.restrictions:
                restriction_text = (
                    f"<b>{restriction.restriction_type.title()}:</b> "
                    f"{', '.join(restriction.restricted_items)} "
                    f"(Severity: {restriction.severity})"
                )
                elements.append(Paragraph(restriction_text, self.styles['Normal']))
            
            elements.append(Spacer(1, 0.2 * inch))
        
        # Recommendations
        if diet_plan.recommendations:
            elements.append(Paragraph(
                "Dietary Recommendations:",
                self.styles['SubsectionHeader']
            ))
            
            for rec in diet_plan.recommendations:
                elements.append(Paragraph(f"• {rec}", self.styles['Normal']))
            
            elements.append(Spacer(1, 0.2 * inch))
        
        elements.append(Spacer(1, 0.2 * inch))
        
        return elements
    
    def _build_diet_plan_section(self, diet_plan: DietPlan) -> list:
        """Build diet plan section with meal details."""
        elements = []
        
        elements.append(Paragraph(
            "Daily Diet Plan",
            self.styles['SectionHeader']
        ))
        
        elements.append(Paragraph(
            f"<b>Target Daily Calories:</b> {diet_plan.daily_calories:.0f} kcal",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Macronutrient targets
        macro = diet_plan.macronutrient_targets
        elements.append(Paragraph(
            f"<b>Macronutrient Targets:</b> "
            f"Protein {macro.protein_percent:.0f}%, "
            f"Carbs {macro.carbs_percent:.0f}%, "
            f"Fat {macro.fat_percent:.0f}%",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Meals
        for meal in diet_plan.meals:
            meal_name = meal.meal_type.value.title()
            elements.append(Paragraph(
                f"{meal_name} ({meal.total_calories:.0f} kcal)",
                self.styles['SubsectionHeader']
            ))
            
            # Meal table
            meal_data = [["Food Item", "Portion", "Calories", "Protein", "Carbs", "Fat"]]
            
            for portion in meal.portions:
                meal_data.append([
                    portion.food.name,
                    f"{portion.amount:.0f} {portion.unit}",
                    f"{portion.calories:.0f}",
                    f"{portion.protein_g:.1f}g",
                    f"{portion.carbs_g:.1f}g",
                    f"{portion.fat_g:.1f}g",
                ])
            
            # Add totals row
            meal_data.append([
                "Total",
                "",
                f"{meal.total_calories:.0f}",
                f"{meal.total_protein_g:.1f}g",
                f"{meal.total_carbs_g:.1f}g",
                f"{meal.total_fat_g:.1f}g",
            ])
            
            table = Table(meal_data, colWidths=[2.2*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 8),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#EBF5FB')]),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D6EAF8')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.2 * inch))
        
        return elements
    
    def _build_nutritional_breakdown_section(self, diet_plan: DietPlan) -> list:
        """Build nutritional breakdown section with charts."""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph(
            "Nutritional Breakdown",
            self.styles['SectionHeader']
        ))
        
        # Calculate total macronutrients
        total_protein = sum(meal.total_protein_g for meal in diet_plan.meals)
        total_carbs = sum(meal.total_carbs_g for meal in diet_plan.meals)
        total_fat = sum(meal.total_fat_g for meal in diet_plan.meals)
        
        # Macronutrient pie chart
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 150
        pie.y = 50
        pie.width = 150
        pie.height = 150
        
        # Calculate calories from macros
        protein_cal = total_protein * 4
        carbs_cal = total_carbs * 4
        fat_cal = total_fat * 9
        
        pie.data = [protein_cal, carbs_cal, fat_cal]
        pie.labels = [
            f'Protein\n{total_protein:.1f}g',
            f'Carbs\n{total_carbs:.1f}g',
            f'Fat\n{total_fat:.1f}g'
        ]
        pie.slices.strokeWidth = 0.5
        pie.slices[0].fillColor = colors.HexColor('#E74C3C')
        pie.slices[1].fillColor = colors.HexColor('#3498DB')
        pie.slices[2].fillColor = colors.HexColor('#F39C12')
        
        drawing.add(pie)
        elements.append(drawing)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Daily totals table
        elements.append(Paragraph(
            "Daily Totals",
            self.styles['SubsectionHeader']
        ))
        
        totals_data = [
            ["Nutrient", "Amount", "Calories", "% of Total"],
            ["Protein", f"{total_protein:.1f}g", f"{protein_cal:.0f} kcal", f"{(protein_cal/diet_plan.daily_calories*100):.1f}%"],
            ["Carbohydrates", f"{total_carbs:.1f}g", f"{carbs_cal:.0f} kcal", f"{(carbs_cal/diet_plan.daily_calories*100):.1f}%"],
            ["Fat", f"{total_fat:.1f}g", f"{fat_cal:.0f} kcal", f"{(fat_cal/diet_plan.daily_calories*100):.1f}%"],
            ["Total", "", f"{diet_plan.daily_calories:.0f} kcal", "100%"],
        ]
        
        table = Table(totals_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#ECF0F1')]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#BDC3C7')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _build_footer_section(self, diet_plan: DietPlan) -> list:
        """Build footer section with disclaimers."""
        elements = []
        
        elements.append(Spacer(1, 0.5 * inch))
        
        # Disclaimer
        disclaimer_style = ParagraphStyle(
            name='Disclaimer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#7F8C8D'),
            alignment=1,  # Center
        )
        
        disclaimer_text = (
            "<b>Medical Disclaimer:</b> This diet plan is generated based on automated analysis "
            "of medical data and should not replace professional medical advice. Please consult "
            "with a healthcare provider or registered dietitian before making significant dietary changes."
        )
        elements.append(Paragraph(disclaimer_text, disclaimer_style))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Generation info
        if diet_plan.generated_at:
            gen_date = diet_plan.generated_at.strftime("%Y-%m-%d %H:%M:%S")
        else:
            gen_date = "Unknown"
        gen_info = f"Generated on: {gen_date} | Plan ID: {diet_plan.plan_id}"
        elements.append(Paragraph(gen_info, disclaimer_style))
        
        return elements
    
    def export_json(self, diet_plan: DietPlan) -> str:
        """
        Export diet plan as structured JSON.
        
        Args:
            diet_plan: Generated diet plan
            
        Returns:
            JSON string containing the complete diet plan
            
        Raises:
            ValueError: If diet plan is invalid
            RuntimeError: If JSON generation fails
        """
        if not diet_plan:
            raise ValueError("Diet plan cannot be None")
        
        try:
            # Build JSON structure
            json_data = {
                "plan_id": diet_plan.plan_id,
                "patient_id": diet_plan.patient_id,
                "generated_date": diet_plan.generated_at.isoformat() if diet_plan.generated_at else None,
                "health_summary": {
                    "conditions": [
                        {
                            "type": condition.condition_type.value,
                            "confidence": condition.confidence,
                            "detected_at": condition.detected_at.isoformat() if condition.detected_at else None,
                            "contributing_metrics": [m.value for m in condition.contributing_metrics]
                        }
                        for condition in diet_plan.health_conditions
                    ],
                    "restrictions": [
                        {
                            "type": restriction.restriction_type,
                            "items": restriction.restricted_items,
                            "severity": restriction.severity
                        }
                        for restriction in diet_plan.restrictions
                    ],
                    "recommendations": diet_plan.recommendations
                },
                "diet_plan": {
                    "daily_calories": diet_plan.daily_calories,
                    "macronutrient_targets": {
                        "protein_percent": diet_plan.macronutrient_targets.protein_percent,
                        "carbs_percent": diet_plan.macronutrient_targets.carbs_percent,
                        "fat_percent": diet_plan.macronutrient_targets.fat_percent
                    },
                    "meals": [
                        {
                            "meal_type": meal.meal_type.value,
                            "total_calories": meal.total_calories,
                            "total_protein_g": meal.total_protein_g,
                            "total_carbs_g": meal.total_carbs_g,
                            "total_fat_g": meal.total_fat_g,
                            "foods": [
                                {
                                    "name": portion.food.name,
                                    "portion": f"{portion.amount} {portion.unit}",
                                    "amount": portion.amount,
                                    "unit": portion.unit,
                                    "calories": portion.calories,
                                    "protein_g": portion.protein_g,
                                    "carbs_g": portion.carbs_g,
                                    "fat_g": portion.fat_g,
                                    "category": portion.food.category
                                }
                                for portion in meal.portions
                            ]
                        }
                        for meal in diet_plan.meals
                    ]
                }
            }
            
            # Validate and return JSON
            json_str = json.dumps(json_data, indent=2)
            
            # Validate by parsing back
            json.loads(json_str)
            
            return json_str
            
        except Exception as e:
            raise RuntimeError(f"JSON generation failed: {str(e)}") from e
    
    def validate_json_schema(self, json_data: str) -> bool:
        """
        Validate JSON against defined schema.
        
        Args:
            json_data: JSON string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            data = json.loads(json_data)
            
            # Check required top-level fields
            required_fields = ["plan_id", "patient_id", "generated_date", "health_summary", "diet_plan"]
            if not all(field in data for field in required_fields):
                return False
            
            # Check health_summary structure
            health_summary = data["health_summary"]
            if not all(field in health_summary for field in ["conditions", "restrictions", "recommendations"]):
                return False
            
            # Check diet_plan structure
            diet_plan = data["diet_plan"]
            if not all(field in diet_plan for field in ["daily_calories", "macronutrient_targets", "meals"]):
                return False
            
            # Check macronutrient_targets
            macro = diet_plan["macronutrient_targets"]
            if not all(field in macro for field in ["protein_percent", "carbs_percent", "fat_percent"]):
                return False
            
            # Check meals structure
            if not isinstance(diet_plan["meals"], list):
                return False
            
            for meal in diet_plan["meals"]:
                required_meal_fields = ["meal_type", "total_calories", "total_protein_g", "total_carbs_g", "total_fat_g", "foods"]
                if not all(field in meal for field in required_meal_fields):
                    return False
                
                # Check foods structure
                if not isinstance(meal["foods"], list):
                    return False
                
                for food in meal["foods"]:
                    required_food_fields = ["name", "portion", "calories", "protein_g", "carbs_g", "fat_g"]
                    if not all(field in food for field in required_food_fields):
                        return False
            
            return True
            
        except (json.JSONDecodeError, KeyError, TypeError):
            return False
