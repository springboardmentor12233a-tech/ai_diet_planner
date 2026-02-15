"""
Tests for the ReportExporter class.

This module contains unit tests and property-based tests for PDF and JSON
export functionality.
"""

import json
import pytest
from datetime import datetime
from io import BytesIO

from PyPDF2 import PdfReader

from ai_diet_planner.export.report_exporter import ReportExporter
from ai_diet_planner.models import (
    DietPlan,
    Meal,
    Portion,
    Food,
    MacronutrientRatios,
    HealthCondition,
    DietaryRestriction,
    PatientProfile,
    UserPreferences,
    MealType,
    ConditionType,
    MetricType,
)


@pytest.fixture
def sample_food():
    """Create a sample food item."""
    return Food(
        name="Grilled Chicken Breast",
        calories=165.0,
        protein_g=31.0,
        carbs_g=0.0,
        fat_g=3.6,
        fiber_g=0.0,
        sodium_mg=74.0,
        sugar_g=0.0,
        category="proteins",
        fdc_id="171477"
    )


@pytest.fixture
def sample_portion(sample_food):
    """Create a sample portion."""
    return Portion(
        food=sample_food,
        amount=100.0,
        unit="g",
        calories=165.0,
        protein_g=31.0,
        carbs_g=0.0,
        fat_g=3.6
    )


@pytest.fixture
def sample_meal(sample_portion):
    """Create a sample meal."""
    return Meal(
        meal_type=MealType.LUNCH,
        portions=[sample_portion],
        total_calories=165.0,
        total_protein_g=31.0,
        total_carbs_g=0.0,
        total_fat_g=3.6
    )


@pytest.fixture
def sample_health_condition():
    """Create a sample health condition."""
    return HealthCondition(
        condition_type=ConditionType.DIABETES_TYPE2,
        confidence=0.85,
        detected_at=datetime.now(),
        contributing_metrics=[MetricType.GLUCOSE, MetricType.HBA1C]
    )


@pytest.fixture
def sample_dietary_restriction():
    """Create a sample dietary restriction."""
    return DietaryRestriction(
        restriction_type="allergy",
        restricted_items=["peanuts", "tree nuts"],
        severity="strict"
    )


@pytest.fixture
def sample_diet_plan(sample_meal, sample_health_condition, sample_dietary_restriction):
    """Create a sample diet plan."""
    return DietPlan(
        plan_id="plan_123",
        patient_id="patient_456",
        generated_at=datetime.now(),
        daily_calories=2000.0,
        macronutrient_targets=MacronutrientRatios(
            protein_percent=30.0,
            carbs_percent=40.0,
            fat_percent=30.0
        ),
        meals=[sample_meal],
        restrictions=[sample_dietary_restriction],
        recommendations=["Increase fiber intake", "Stay hydrated"],
        health_conditions=[sample_health_condition]
    )


@pytest.fixture
def sample_patient_profile():
    """Create a sample patient profile."""
    return PatientProfile(
        patient_id="patient_456",
        age=45,
        gender="male",
        height_cm=175.0,
        weight_kg=80.0,
        activity_level="moderate",
        preferences=UserPreferences(
            dietary_style="balanced",
            allergies=["peanuts"],
            dislikes=["liver"],
            cultural_preferences=[]
        ),
        created_at=datetime.now()
    )


@pytest.fixture
def report_exporter():
    """Create a ReportExporter instance."""
    return ReportExporter()


class TestReportExporterPDF:
    """Tests for PDF export functionality."""
    
    def test_export_pdf_basic(self, report_exporter, sample_diet_plan):
        """Test basic PDF generation."""
        pdf_bytes = report_exporter.export_pdf(sample_diet_plan)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Verify it's a valid PDF
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        assert len(pdf_reader.pages) > 0
    
    def test_export_pdf_with_patient_info(
        self,
        report_exporter,
        sample_diet_plan,
        sample_patient_profile
    ):
        """Test PDF generation with patient information."""
        pdf_bytes = report_exporter.export_pdf(
            sample_diet_plan,
            patient_info=sample_patient_profile
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Verify PDF contains patient info
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        first_page_text = pdf_reader.pages[0].extract_text()
        
        assert "Patient Information" in first_page_text
        assert sample_patient_profile.patient_id in first_page_text
    
    def test_export_pdf_contains_all_sections(
        self,
        report_exporter,
        sample_diet_plan,
        sample_patient_profile
    ):
        """Test that PDF contains all required sections."""
        pdf_bytes = report_exporter.export_pdf(
            sample_diet_plan,
            patient_info=sample_patient_profile
        )
        
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text()
        
        # Check for required sections
        assert "Personalized Diet Plan Report" in full_text
        assert "Patient Information" in full_text
        assert "Health Summary" in full_text
        assert "Daily Diet Plan" in full_text
        assert "Nutritional Breakdown" in full_text
        assert "Medical Disclaimer" in full_text
    
    def test_export_pdf_contains_health_conditions(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test that PDF includes health conditions."""
        pdf_bytes = report_exporter.export_pdf(sample_diet_plan)
        
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text()
        
        assert "Detected Health Conditions" in full_text
        assert "Diabetes Type2" in full_text or "Type2" in full_text
    
    def test_export_pdf_contains_dietary_restrictions(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test that PDF includes dietary restrictions."""
        pdf_bytes = report_exporter.export_pdf(sample_diet_plan)
        
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text()
        
        assert "Dietary Restrictions" in full_text
        assert "peanuts" in full_text.lower()
    
    def test_export_pdf_contains_meal_details(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test that PDF includes meal details."""
        pdf_bytes = report_exporter.export_pdf(sample_diet_plan)
        
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text()
        
        assert "Lunch" in full_text
        assert "Grilled Chicken Breast" in full_text
    
    def test_export_pdf_contains_nutritional_breakdown(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test that PDF includes nutritional breakdown."""
        pdf_bytes = report_exporter.export_pdf(sample_diet_plan)
        
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text()
        
        assert "Nutritional Breakdown" in full_text
        assert "Protein" in full_text
        assert "Carbohydrates" in full_text or "Carbs" in full_text
        assert "Fat" in full_text
    
    def test_export_pdf_none_diet_plan_raises_error(self, report_exporter):
        """Test that None diet plan raises ValueError."""
        with pytest.raises(ValueError, match="Diet plan cannot be None"):
            report_exporter.export_pdf(None)
    
    def test_export_pdf_empty_meals_raises_error(self, report_exporter, sample_diet_plan):
        """Test that diet plan with no meals raises ValueError."""
        sample_diet_plan.meals = []
        
        with pytest.raises(ValueError, match="Diet plan must contain at least one meal"):
            report_exporter.export_pdf(sample_diet_plan)
    
    def test_export_pdf_multiple_meals(self, report_exporter, sample_diet_plan, sample_portion):
        """Test PDF generation with multiple meals."""
        # Add more meals
        breakfast = Meal(
            meal_type=MealType.BREAKFAST,
            portions=[sample_portion],
            total_calories=165.0,
            total_protein_g=31.0,
            total_carbs_g=0.0,
            total_fat_g=3.6
        )
        dinner = Meal(
            meal_type=MealType.DINNER,
            portions=[sample_portion],
            total_calories=165.0,
            total_protein_g=31.0,
            total_carbs_g=0.0,
            total_fat_g=3.6
        )
        
        sample_diet_plan.meals.extend([breakfast, dinner])
        
        pdf_bytes = report_exporter.export_pdf(sample_diet_plan)
        
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text()
        
        assert "Breakfast" in full_text
        assert "Lunch" in full_text
        assert "Dinner" in full_text


class TestReportExporterJSON:
    """Tests for JSON export functionality."""
    
    def test_export_json_basic(self, report_exporter, sample_diet_plan):
        """Test basic JSON generation."""
        json_str = report_exporter.export_json(sample_diet_plan)
        
        assert isinstance(json_str, str)
        assert len(json_str) > 0
        
        # Verify it's valid JSON
        data = json.loads(json_str)
        assert isinstance(data, dict)
    
    def test_export_json_contains_required_fields(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test that JSON contains all required top-level fields."""
        json_str = report_exporter.export_json(sample_diet_plan)
        data = json.loads(json_str)
        
        assert "plan_id" in data
        assert "patient_id" in data
        assert "generated_date" in data
        assert "health_summary" in data
        assert "diet_plan" in data
    
    def test_export_json_health_summary_structure(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test that JSON health_summary has correct structure."""
        json_str = report_exporter.export_json(sample_diet_plan)
        data = json.loads(json_str)
        
        health_summary = data["health_summary"]
        assert "conditions" in health_summary
        assert "restrictions" in health_summary
        assert "recommendations" in health_summary
        
        # Check conditions structure
        assert len(health_summary["conditions"]) > 0
        condition = health_summary["conditions"][0]
        assert "type" in condition
        assert "confidence" in condition
        assert "detected_at" in condition
        assert "contributing_metrics" in condition
    
    def test_export_json_diet_plan_structure(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test that JSON diet_plan has correct structure."""
        json_str = report_exporter.export_json(sample_diet_plan)
        data = json.loads(json_str)
        
        diet_plan = data["diet_plan"]
        assert "daily_calories" in diet_plan
        assert "macronutrient_targets" in diet_plan
        assert "meals" in diet_plan
        
        # Check macronutrient_targets
        macro = diet_plan["macronutrient_targets"]
        assert "protein_percent" in macro
        assert "carbs_percent" in macro
        assert "fat_percent" in macro
    
    def test_export_json_meals_structure(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test that JSON meals have correct structure."""
        json_str = report_exporter.export_json(sample_diet_plan)
        data = json.loads(json_str)
        
        meals = data["diet_plan"]["meals"]
        assert len(meals) > 0
        
        meal = meals[0]
        assert "meal_type" in meal
        assert "total_calories" in meal
        assert "total_protein_g" in meal
        assert "total_carbs_g" in meal
        assert "total_fat_g" in meal
        assert "foods" in meal
        
        # Check foods structure
        assert len(meal["foods"]) > 0
        food = meal["foods"][0]
        assert "name" in food
        assert "portion" in food
        assert "calories" in food
        assert "protein_g" in food
        assert "carbs_g" in food
        assert "fat_g" in food
    
    def test_export_json_data_accuracy(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test that JSON data matches diet plan data."""
        json_str = report_exporter.export_json(sample_diet_plan)
        data = json.loads(json_str)
        
        assert data["plan_id"] == sample_diet_plan.plan_id
        assert data["patient_id"] == sample_diet_plan.patient_id
        assert data["diet_plan"]["daily_calories"] == sample_diet_plan.daily_calories
        
        # Check macronutrient targets
        macro = data["diet_plan"]["macronutrient_targets"]
        assert macro["protein_percent"] == sample_diet_plan.macronutrient_targets.protein_percent
        assert macro["carbs_percent"] == sample_diet_plan.macronutrient_targets.carbs_percent
        assert macro["fat_percent"] == sample_diet_plan.macronutrient_targets.fat_percent
    
    def test_export_json_none_diet_plan_raises_error(self, report_exporter):
        """Test that None diet plan raises ValueError."""
        with pytest.raises(ValueError, match="Diet plan cannot be None"):
            report_exporter.export_json(None)
    
    def test_validate_json_schema_valid(self, report_exporter, sample_diet_plan):
        """Test JSON schema validation with valid data."""
        json_str = report_exporter.export_json(sample_diet_plan)
        
        assert report_exporter.validate_json_schema(json_str) is True
    
    def test_validate_json_schema_invalid_missing_fields(self, report_exporter):
        """Test JSON schema validation with missing fields."""
        invalid_json = json.dumps({"plan_id": "123"})
        
        assert report_exporter.validate_json_schema(invalid_json) is False
    
    def test_validate_json_schema_invalid_json(self, report_exporter):
        """Test JSON schema validation with invalid JSON."""
        invalid_json = "not valid json"
        
        assert report_exporter.validate_json_schema(invalid_json) is False
    
    def test_validate_json_schema_missing_health_summary_fields(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test JSON schema validation with incomplete health_summary."""
        json_str = report_exporter.export_json(sample_diet_plan)
        data = json.loads(json_str)
        
        # Remove a required field
        del data["health_summary"]["conditions"]
        
        invalid_json = json.dumps(data)
        assert report_exporter.validate_json_schema(invalid_json) is False
    
    def test_validate_json_schema_missing_diet_plan_fields(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test JSON schema validation with incomplete diet_plan."""
        json_str = report_exporter.export_json(sample_diet_plan)
        data = json.loads(json_str)
        
        # Remove a required field
        del data["diet_plan"]["meals"]
        
        invalid_json = json.dumps(data)
        assert report_exporter.validate_json_schema(invalid_json) is False


class TestReportExporterPerformance:
    """Tests for export performance requirements."""
    
    def test_pdf_generation_performance(
        self,
        report_exporter,
        sample_diet_plan,
        sample_patient_profile
    ):
        """
        Test that PDF generation completes within 5 seconds.
        
        **Validates: Requirements 11.4**
        """
        import time
        
        start_time = time.time()
        pdf_bytes = report_exporter.export_pdf(
            sample_diet_plan,
            patient_info=sample_patient_profile
        )
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        assert elapsed_time < 5.0, f"PDF generation took {elapsed_time:.2f}s, expected < 5s"
        assert len(pdf_bytes) > 0
    
    def test_json_generation_performance(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """
        Test that JSON generation completes within 2 seconds.
        
        **Validates: Requirements 12.4**
        """
        import time
        
        start_time = time.time()
        json_str = report_exporter.export_json(sample_diet_plan)
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        assert elapsed_time < 2.0, f"JSON generation took {elapsed_time:.2f}s, expected < 2s"
        assert len(json_str) > 0


class TestReportExporterEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_export_pdf_no_health_conditions(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test PDF generation with no health conditions."""
        sample_diet_plan.health_conditions = []
        
        pdf_bytes = report_exporter.export_pdf(sample_diet_plan)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_export_pdf_no_restrictions(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test PDF generation with no dietary restrictions."""
        sample_diet_plan.restrictions = []
        
        pdf_bytes = report_exporter.export_pdf(sample_diet_plan)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_export_pdf_no_recommendations(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test PDF generation with no recommendations."""
        sample_diet_plan.recommendations = []
        
        pdf_bytes = report_exporter.export_pdf(sample_diet_plan)
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_export_json_no_health_conditions(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test JSON generation with no health conditions."""
        sample_diet_plan.health_conditions = []
        
        json_str = report_exporter.export_json(sample_diet_plan)
        data = json.loads(json_str)
        
        assert data["health_summary"]["conditions"] == []
        assert report_exporter.validate_json_schema(json_str) is True
    
    def test_export_json_no_restrictions(
        self,
        report_exporter,
        sample_diet_plan
    ):
        """Test JSON generation with no dietary restrictions."""
        sample_diet_plan.restrictions = []
        
        json_str = report_exporter.export_json(sample_diet_plan)
        data = json.loads(json_str)
        
        assert data["health_summary"]["restrictions"] == []
        assert report_exporter.validate_json_schema(json_str) is True
    
    def test_export_pdf_multiple_portions_per_meal(
        self,
        report_exporter,
        sample_diet_plan,
        sample_portion
    ):
        """Test PDF generation with multiple portions per meal."""
        # Add more portions to the meal
        rice = Portion(
            food=Food(
                name="Brown Rice",
                calories=112.0,
                protein_g=2.6,
                carbs_g=23.5,
                fat_g=0.9,
                fiber_g=1.8,
                sodium_mg=5.0,
                sugar_g=0.4,
                category="carbs"
            ),
            amount=100.0,
            unit="g",
            calories=112.0,
            protein_g=2.6,
            carbs_g=23.5,
            fat_g=0.9
        )
        
        sample_diet_plan.meals[0].portions.append(rice)
        sample_diet_plan.meals[0].total_calories += rice.calories
        sample_diet_plan.meals[0].total_protein_g += rice.protein_g
        sample_diet_plan.meals[0].total_carbs_g += rice.carbs_g
        sample_diet_plan.meals[0].total_fat_g += rice.fat_g
        
        pdf_bytes = report_exporter.export_pdf(sample_diet_plan)
        
        pdf_reader = PdfReader(BytesIO(pdf_bytes))
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text()
        
        assert "Brown Rice" in full_text
        assert "Grilled Chicken Breast" in full_text
