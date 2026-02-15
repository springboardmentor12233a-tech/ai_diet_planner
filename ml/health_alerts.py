"""
Health Alerts Module for AI NutriCare System

This module provides a simplified interface for generating health alerts
from patient data. It uses the MLHealthAnalyzer for threshold-based
alert generation with severity levels and recommended actions.

This module has been refactored to use MLHealthAnalyzer.detect_abnormal_values()
to avoid code duplication and ensure consistency across the system.

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""

from typing import Dict, List, Any
from ai_diet_planner.ml.health_analyzer import MLHealthAnalyzer


def get_health_alerts(patient_data: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Generate health alerts from patient data using MLHealthAnalyzer.
    
    This function provides a simplified interface that returns alerts as
    dictionaries for backward compatibility with existing code.
    
    Args:
        patient_data: Dictionary of health metrics (e.g., {'Glucose': 120, 'BMI': 28})
        
    Returns:
        List of alert dictionaries with:
        - metric: Metric name
        - severity: 'CRITICAL', 'WARNING', or 'NORMAL'
        - message: Human-readable alert message
        - recommended_action: Recommended action to take
        
    Example:
        >>> patient = {'Glucose': 130, 'BMI': 32, 'BloodPressure': 85}
        >>> alerts = get_health_alerts(patient)
        >>> for alert in alerts:
        ...     print(f"[{alert['severity']}] {alert['metric']}: {alert['message']}")
    """
    # Create analyzer instance (no model registry needed for threshold-based alerts)
    analyzer = MLHealthAnalyzer()
    
    # Get Alert objects from analyzer
    alert_objects = analyzer.detect_abnormal_values(patient_data)
    
    # Convert Alert objects to dictionaries for backward compatibility
    alerts = []
    for alert_obj in alert_objects:
        alerts.append({
            'metric': alert_obj.metric_type.value,
            'severity': alert_obj.severity.value.upper(),
            'message': alert_obj.message,
            'recommended_action': alert_obj.recommended_action
        })
    
    return alerts


def _read_float(prompt: str) -> float:
    """
    Read a float value from user input with validation.
    
    Args:
        prompt: Prompt message to display
        
    Returns:
        Float value entered by user
    """
    while True:
        raw_value = input(prompt).strip()
        try:
            return float(raw_value)
        except ValueError:
            print("Please enter a valid number.")


def get_patient_data_from_user() -> Dict[str, float]:
    """
    Interactively collect patient health data from user input.
    
    Returns:
        Dictionary of health metrics
    """
    return {
        "Glucose": _read_float("Enter fasting glucose (mg/dL): "),
        "BMI": _read_float("Enter BMI: "),
        "BloodPressure": _read_float("Enter diastolic blood pressure (mmHg): "),
    }


if __name__ == "__main__":
    print("=== AI NutriCare Health Alerts System ===\n")
    
    patient = get_patient_data_from_user()
    alerts = get_health_alerts(patient)

    print("\n=== Health Alert Report ===\n")
    
    if not alerts:
        print("✓ No active alerts. All metrics are within normal ranges.")
        print("  Keep up the good work!")
    else:
        # Group by severity
        critical_alerts = [a for a in alerts if a['severity'] == 'CRITICAL']
        warning_alerts = [a for a in alerts if a['severity'] == 'WARNING']
        
        if critical_alerts:
            print("🔴 CRITICAL ALERTS:")
            for alert in critical_alerts:
                print(f"\n  [{alert['severity']}] {alert['metric']}")
                print(f"  {alert['message']}")
                print(f"  → {alert['recommended_action']}")
        
        if warning_alerts:
            print("\n🟡 WARNING ALERTS:")
            for alert in warning_alerts:
                print(f"\n  [{alert['severity']}] {alert['metric']}")
                print(f"  {alert['message']}")
                print(f"  → {alert['recommended_action']}")
