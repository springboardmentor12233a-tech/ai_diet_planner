"""
Fallback mechanisms for AI NutriCare System.

Provides graceful degradation strategies when primary processing fails:
- OCR failure → Manual data entry
- ML failure → Rule-based threshold analysis
- NLP failure → Manual diet rule entry
"""

import logging
from typing import Dict, List, Optional, Any

from ai_diet_planner.models.health_data import HealthMetric, Alert, HealthCondition
from ai_diet_planner.models.diet_data import DietRule
from ai_diet_planner.models.enums import AlertSeverity, ConditionType, MetricType, RulePriority

logger = logging.getLogger("nutricare.fallback")


class FallbackStrategies:
    """Fallback strategies for system failures."""
    
    @staticmethod
    def manual_data_entry_prompt() -> Dict[str, Any]:
        """
        Generate prompt for manual data entry when OCR fails.
        
        Returns:
            Dictionary with instructions and required fields
        """
        return {
            'message': 'OCR processing failed. Please enter health metrics manually.',
            'required_fields': [
                {'name': 'glucose', 'unit': 'mg/dL', 'type': 'number'},
                {'name': 'cholesterol_total', 'unit': 'mg/dL', 'type': 'number'},
                {'name': 'cholesterol_ldl', 'unit': 'mg/dL', 'type': 'number'},
                {'name': 'cholesterol_hdl', 'unit': 'mg/dL', 'type': 'number'},
                {'name': 'triglycerides', 'unit': 'mg/dL', 'type': 'number'},
                {'name': 'bmi', 'unit': 'kg/m²', 'type': 'number'},
                {'name': 'blood_pressure_systolic', 'unit': 'mmHg', 'type': 'number'},
                {'name': 'blood_pressure_diastolic', 'unit': 'mmHg', 'type': 'number'},
                {'name': 'hemoglobin', 'unit': 'g/dL', 'type': 'number'},
                {'name': 'hba1c', 'unit': '%', 'type': 'number'}
            ],
            'optional_fields': [
                {'name': 'doctor_notes', 'type': 'text'}
            ]
        }
    
    @staticmethod
    def rule_based_health_analysis(metrics: List[HealthMetric]) -> tuple[List[HealthCondition], List[Alert]]:
        """
        Perform rule-based threshold analysis when ML fails.
        
        Args:
            metrics: List of health metrics
            
        Returns:
            Tuple of (health conditions, alerts)
        """
        logger.info("Using rule-based fallback for health analysis")
        
        conditions: List[HealthCondition] = []
        alerts: List[Alert] = []
        
        # Create metric lookup
        metric_map = {m.metric_type: m for m in metrics}
        
        # Diabetes detection (rule-based)
        glucose = metric_map.get(MetricType.GLUCOSE)
        hba1c = metric_map.get(MetricType.HBA1C)
        
        if glucose and glucose.value >= 126:
            conditions.append(HealthCondition(
                condition_type=ConditionType.DIABETES_TYPE_2,
                confidence=0.8,
                contributing_metrics=[glucose]
            ))
            alerts.append(Alert(
                severity=AlertSeverity.CRITICAL,
                message=f"Fasting glucose level ({glucose.value} mg/dL) indicates diabetes",
                metric=glucose,
                recommended_action="Consult endocrinologist immediately"
            ))
        elif glucose and glucose.value >= 100:
            conditions.append(HealthCondition(
                condition_type=ConditionType.PREDIABETES,
                confidence=0.75,
                contributing_metrics=[glucose]
            ))
            alerts.append(Alert(
                severity=AlertSeverity.WARNING,
                message=f"Fasting glucose level ({glucose.value} mg/dL) indicates prediabetes",
                metric=glucose,
                recommended_action="Lifestyle modifications recommended"
            ))
        
        if hba1c and hba1c.value >= 6.5:
            if not any(c.condition_type == ConditionType.DIABETES_TYPE_2 for c in conditions):
                conditions.append(HealthCondition(
                    condition_type=ConditionType.DIABETES_TYPE_2,
                    confidence=0.8,
                    contributing_metrics=[hba1c]
                ))
            alerts.append(Alert(
                severity=AlertSeverity.CRITICAL,
                message=f"HbA1c level ({hba1c.value}%) indicates diabetes",
                metric=hba1c,
                recommended_action="Consult endocrinologist immediately"
            ))
        
        # Hypertension detection
        bp_sys = metric_map.get(MetricType.BLOOD_PRESSURE_SYSTOLIC)
        bp_dia = metric_map.get(MetricType.BLOOD_PRESSURE_DIASTOLIC)
        
        if bp_sys and bp_dia:
            if bp_sys.value >= 140 or bp_dia.value >= 90:
                stage = "Stage 2" if bp_sys.value >= 140 or bp_dia.value >= 90 else "Stage 1"
                conditions.append(HealthCondition(
                    condition_type=ConditionType.HYPERTENSION_STAGE_2 if stage == "Stage 2" else ConditionType.HYPERTENSION_STAGE_1,
                    confidence=0.75,
                    contributing_metrics=[bp_sys, bp_dia]
                ))
                alerts.append(Alert(
                    severity=AlertSeverity.CRITICAL if stage == "Stage 2" else AlertSeverity.WARNING,
                    message=f"Blood pressure ({bp_sys.value}/{bp_dia.value} mmHg) indicates {stage} hypertension",
                    metric=bp_sys,
                    recommended_action="Consult cardiologist"
                ))
        
        # Hyperlipidemia detection
        chol_total = metric_map.get(MetricType.CHOLESTEROL_TOTAL)
        chol_ldl = metric_map.get(MetricType.CHOLESTEROL_LDL)
        
        if chol_total and chol_total.value >= 240:
            conditions.append(HealthCondition(
                condition_type=ConditionType.HYPERLIPIDEMIA,
                confidence=0.75,
                contributing_metrics=[chol_total]
            ))
            alerts.append(Alert(
                severity=AlertSeverity.WARNING,
                message=f"Total cholesterol ({chol_total.value} mg/dL) is high",
                metric=chol_total,
                recommended_action="Dietary modifications and possible medication"
            ))
        
        if chol_ldl and chol_ldl.value >= 160:
            if not any(c.condition_type == ConditionType.HYPERLIPIDEMIA for c in conditions):
                conditions.append(HealthCondition(
                    condition_type=ConditionType.HYPERLIPIDEMIA,
                    confidence=0.75,
                    contributing_metrics=[chol_ldl]
                ))
            alerts.append(Alert(
                severity=AlertSeverity.WARNING,
                message=f"LDL cholesterol ({chol_ldl.value} mg/dL) is high",
                metric=chol_ldl,
                recommended_action="Dietary modifications and possible medication"
            ))
        
        # Obesity detection
        bmi = metric_map.get(MetricType.BMI)
        if bmi:
            if bmi.value >= 40:
                conditions.append(HealthCondition(
                    condition_type=ConditionType.OBESITY_CLASS_III,
                    confidence=0.9,
                    contributing_metrics=[bmi]
                ))
                alerts.append(Alert(
                    severity=AlertSeverity.CRITICAL,
                    message=f"BMI ({bmi.value}) indicates Class III obesity",
                    metric=bmi,
                    recommended_action="Consult healthcare provider for weight management"
                ))
            elif bmi.value >= 35:
                conditions.append(HealthCondition(
                    condition_type=ConditionType.OBESITY_CLASS_II,
                    confidence=0.9,
                    contributing_metrics=[bmi]
                ))
                alerts.append(Alert(
                    severity=AlertSeverity.WARNING,
                    message=f"BMI ({bmi.value}) indicates Class II obesity",
                    metric=bmi,
                    recommended_action="Weight management recommended"
                ))
            elif bmi.value >= 30:
                conditions.append(HealthCondition(
                    condition_type=ConditionType.OBESITY_CLASS_I,
                    confidence=0.9,
                    contributing_metrics=[bmi]
                ))
                alerts.append(Alert(
                    severity=AlertSeverity.WARNING,
                    message=f"BMI ({bmi.value}) indicates Class I obesity",
                    metric=bmi,
                    recommended_action="Weight management recommended"
                ))
        
        # Anemia detection
        hemoglobin = metric_map.get(MetricType.HEMOGLOBIN)
        if hemoglobin:
            if hemoglobin.value < 12:  # Simplified threshold
                conditions.append(HealthCondition(
                    condition_type=ConditionType.ANEMIA,
                    confidence=0.7,
                    contributing_metrics=[hemoglobin]
                ))
                alerts.append(Alert(
                    severity=AlertSeverity.WARNING,
                    message=f"Hemoglobin level ({hemoglobin.value} g/dL) indicates possible anemia",
                    metric=hemoglobin,
                    recommended_action="Consult healthcare provider"
                ))
        
        logger.info(f"Rule-based analysis found {len(conditions)} conditions and {len(alerts)} alerts")
        return conditions, alerts
    
    @staticmethod
    def manual_diet_rule_entry_prompt() -> Dict[str, Any]:
        """
        Generate prompt for manual diet rule entry when NLP fails.
        
        Returns:
            Dictionary with instructions and input fields
        """
        return {
            'message': 'NLP processing failed. Please enter dietary restrictions and recommendations manually.',
            'fields': [
                {
                    'name': 'allergies',
                    'label': 'Food Allergies (comma-separated)',
                    'type': 'text',
                    'placeholder': 'e.g., peanuts, shellfish, dairy',
                    'priority': RulePriority.REQUIRED.value
                },
                {
                    'name': 'intolerances',
                    'label': 'Food Intolerances (comma-separated)',
                    'type': 'text',
                    'placeholder': 'e.g., lactose, gluten',
                    'priority': RulePriority.REQUIRED.value
                },
                {
                    'name': 'restrictions',
                    'label': 'Dietary Restrictions (comma-separated)',
                    'type': 'text',
                    'placeholder': 'e.g., low sodium, low sugar, low fat',
                    'priority': RulePriority.RECOMMENDED.value
                },
                {
                    'name': 'recommendations',
                    'label': 'Dietary Recommendations (comma-separated)',
                    'type': 'text',
                    'placeholder': 'e.g., high fiber, omega-3 rich',
                    'priority': RulePriority.RECOMMENDED.value
                }
            ]
        }
    
    @staticmethod
    def parse_manual_diet_rules(manual_input: Dict[str, str]) -> List[DietRule]:
        """
        Parse manually entered diet rules.
        
        Args:
            manual_input: Dictionary with manual diet rule entries
            
        Returns:
            List of DietRule objects
        """
        logger.info("Parsing manual diet rules")
        rules: List[DietRule] = []
        
        # Parse allergies
        if manual_input.get('allergies'):
            for allergy in manual_input['allergies'].split(','):
                allergy = allergy.strip()
                if allergy:
                    rules.append(DietRule(
                        rule_text=f"Avoid {allergy} (allergy)",
                        priority=RulePriority.REQUIRED,
                        food_categories=['all'],
                        action='exclude'
                    ))
        
        # Parse intolerances
        if manual_input.get('intolerances'):
            for intolerance in manual_input['intolerances'].split(','):
                intolerance = intolerance.strip()
                if intolerance:
                    rules.append(DietRule(
                        rule_text=f"Avoid {intolerance} (intolerance)",
                        priority=RulePriority.REQUIRED,
                        food_categories=['all'],
                        action='exclude'
                    ))
        
        # Parse restrictions
        if manual_input.get('restrictions'):
            for restriction in manual_input['restrictions'].split(','):
                restriction = restriction.strip()
                if restriction:
                    rules.append(DietRule(
                        rule_text=f"Follow {restriction} diet",
                        priority=RulePriority.RECOMMENDED,
                        food_categories=['all'],
                        action='limit'
                    ))
        
        # Parse recommendations
        if manual_input.get('recommendations'):
            for recommendation in manual_input['recommendations'].split(','):
                recommendation = recommendation.strip()
                if recommendation:
                    rules.append(DietRule(
                        rule_text=f"Include {recommendation} foods",
                        priority=RulePriority.RECOMMENDED,
                        food_categories=['all'],
                        action='include'
                    ))
        
        logger.info(f"Parsed {len(rules)} manual diet rules")
        return rules
