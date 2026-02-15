"""
Example usage of the enhanced health alerts system

This example demonstrates:
1. Threshold-based alert generation
2. Severity levels: CRITICAL, WARNING, NORMAL
3. Alert prioritization by medical severity
4. Recommended actions for each alert
5. Integration with MLHealthAnalyzer

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""

from ai_diet_planner.ml.health_analyzer import MLHealthAnalyzer
from ai_diet_planner.ml.health_alerts import get_health_alerts


def example_comprehensive_alerts():
    """Example with multiple abnormal values across different severity levels"""
    print("=" * 80)
    print("Example 1: Comprehensive Health Alert System")
    print("=" * 80)
    
    # Patient with multiple health concerns
    patient_data = {
        'Glucose': 145,           # CRITICAL - Diabetes range
        'HbA1c': 7.2,            # CRITICAL - Diabetes confirmed
        'BMI': 33,               # CRITICAL - Obesity Class I
        'BloodPressure': 135,    # WARNING - Stage 1 Hypertension (systolic)
        'Cholesterol': 220,      # WARNING - Borderline high
        'LDL': 145,              # WARNING - Borderline high
        'Triglycerides': 180,    # WARNING - Borderline high
        'HDL': 38,               # CRITICAL - Low HDL (reverse threshold)
        'Hemoglobin': 11.8       # WARNING - Borderline low (reverse threshold)
    }
    
    # Get alerts using the simplified interface
    alerts = get_health_alerts(patient_data)
    
    print(f"\nPatient Metrics:")
    for metric, value in patient_data.items():
        print(f"  {metric}: {value}")
    
    print(f"\n{'=' * 80}")
    print(f"Generated {len(alerts)} alerts (prioritized by severity)")
    print(f"{'=' * 80}\n")
    
    # Group by severity
    critical_alerts = [a for a in alerts if a['severity'] == 'CRITICAL']
    warning_alerts = [a for a in alerts if a['severity'] == 'WARNING']
    
    if critical_alerts:
        print("🔴 CRITICAL ALERTS (Immediate attention required):")
        print("-" * 80)
        for i, alert in enumerate(critical_alerts, 1):
            print(f"\n{i}. {alert['metric'].upper()}")
            print(f"   {alert['message']}")
            print(f"   ➜ {alert['recommended_action']}")
    
    if warning_alerts:
        print("\n\n🟡 WARNING ALERTS (Monitoring recommended):")
        print("-" * 80)
        for i, alert in enumerate(warning_alerts, 1):
            print(f"\n{i}. {alert['metric'].upper()}")
            print(f"   {alert['message']}")
            print(f"   ➜ {alert['recommended_action']}")
    
    print("\n" + "=" * 80)


def example_direct_analyzer_usage():
    """Example using MLHealthAnalyzer directly for Alert objects"""
    print("\n\n" + "=" * 80)
    print("Example 2: Direct MLHealthAnalyzer Usage (Alert Objects)")
    print("=" * 80)
    
    analyzer = MLHealthAnalyzer()
    
    # Patient with critical glucose and BMI
    metrics = {
        'Glucose': 155,
        'BMI': 35.5,
        'BloodPressure': 88
    }
    
    print(f"\nPatient Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value}")
    
    # Get Alert objects directly
    alert_objects = analyzer.detect_abnormal_values(metrics)
    
    print(f"\n{'=' * 80}")
    print(f"Generated {len(alert_objects)} Alert objects")
    print(f"{'=' * 80}\n")
    
    for i, alert in enumerate(alert_objects, 1):
        print(f"{i}. Alert Object:")
        print(f"   Metric Type: {alert.metric_type.value}")
        print(f"   Severity: {alert.severity.value.upper()}")
        print(f"   Message: {alert.message}")
        print(f"   Recommended Action: {alert.recommended_action[:100]}...")
        print()


def example_normal_values():
    """Example with all normal values (no alerts)"""
    print("\n" + "=" * 80)
    print("Example 3: Normal Values (No Alerts)")
    print("=" * 80)
    
    # Healthy patient
    healthy_patient = {
        'Glucose': 92,
        'BMI': 23.5,
        'BloodPressure': 75,
        'Cholesterol': 180,
        'HDL': 55,
        'LDL': 110,
        'Triglycerides': 120,
        'HbA1c': 5.2,
        'Hemoglobin': 14.0
    }
    
    print(f"\nPatient Metrics:")
    for metric, value in healthy_patient.items():
        print(f"  {metric}: {value}")
    
    alerts = get_health_alerts(healthy_patient)
    
    print(f"\n{'=' * 80}")
    if not alerts:
        print("✓ No alerts generated - All metrics within normal ranges!")
        print("  Patient health indicators are optimal.")
    print("=" * 80)


def example_reverse_thresholds():
    """Example demonstrating reverse thresholds (lower is worse)"""
    print("\n\n" + "=" * 80)
    print("Example 4: Reverse Thresholds (HDL & Hemoglobin)")
    print("=" * 80)
    
    # Patient with low HDL and hemoglobin
    patient = {
        'HDL': 35,        # CRITICAL - Low HDL increases cardiovascular risk
        'Hemoglobin': 11.0  # CRITICAL - Anemia
    }
    
    print(f"\nPatient Metrics:")
    for metric, value in patient.items():
        print(f"  {metric}: {value}")
    
    print("\nNote: For HDL and Hemoglobin, LOWER values trigger alerts")
    print("(reverse thresholds)")
    
    alerts = get_health_alerts(patient)
    
    print(f"\n{'=' * 80}")
    print(f"Generated {len(alerts)} alerts")
    print(f"{'=' * 80}\n")
    
    for i, alert in enumerate(alerts, 1):
        print(f"{i}. [{alert['severity']}] {alert['metric'].upper()}")
        print(f"   {alert['message']}")
        print(f"   ➜ {alert['recommended_action']}")
        print()


def example_alert_prioritization():
    """Example demonstrating alert prioritization"""
    print("\n" + "=" * 80)
    print("Example 5: Alert Prioritization (CRITICAL before WARNING)")
    print("=" * 80)
    
    # Mix of critical and warning alerts
    patient = {
        'Glucose': 110,  # WARNING
        'BMI': 35,       # CRITICAL
        'BloodPressure': 85,  # WARNING
        'Cholesterol': 245,   # CRITICAL
        'LDL': 140       # WARNING
    }
    
    print(f"\nPatient Metrics (mixed severity):")
    for metric, value in patient.items():
        print(f"  {metric}: {value}")
    
    alerts = get_health_alerts(patient)
    
    print(f"\n{'=' * 80}")
    print("Alerts are automatically prioritized by medical severity:")
    print("=" * 80)
    
    for i, alert in enumerate(alerts, 1):
        severity_icon = "🔴" if alert['severity'] == 'CRITICAL' else "🟡"
        print(f"\n{i}. {severity_icon} [{alert['severity']}] {alert['metric'].upper()}")
        print(f"   {alert['message']}")
    
    print("\n" + "=" * 80)
    print("Note: CRITICAL alerts appear first for immediate attention")
    print("=" * 80)


if __name__ == "__main__":
    # Run all examples
    example_comprehensive_alerts()
    example_direct_analyzer_usage()
    example_normal_values()
    example_reverse_thresholds()
    example_alert_prioritization()
    
    print("\n\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)
