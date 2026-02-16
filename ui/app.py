"""
Main Streamlit application for the AI NutriCare System.

This module provides the main entry point for the Streamlit UI with multi-page
navigation and session state management.

Requirements:
- 13.1: User Interface for Report Upload
- 13.5: Display supported file formats and size limits
"""

# Load environment variables FIRST before any other imports
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from typing import Optional
from datetime import datetime


def initialize_session_state():
    """
    Initialize session state variables for maintaining data across pages.
    
    Session state variables:
    - current_page: The currently active page
    - uploaded_file: The uploaded medical report file
    - report_id: Unique identifier for the uploaded report
    - processing_status: Status of report processing
    - extracted_data: Extracted health data from the report
    - textual_notes: Extracted textual notes from the report
    - health_conditions: Detected health conditions
    - health_alerts: Generated health alerts
    - diet_rules: Extracted dietary rules
    - diet_plan: Generated personalized diet plan
    - pdf_export: PDF export bytes
    - json_export: JSON export string
    - processing_time: Time taken to process the report
    - patient_id: Current patient identifier
    - patient_profile: Patient profile information
    """
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Upload"
    
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    
    if "report_id" not in st.session_state:
        st.session_state.report_id = None
    
    if "processing_status" not in st.session_state:
        st.session_state.processing_status = None
    
    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = None
    
    if "textual_notes" not in st.session_state:
        st.session_state.textual_notes = []
    
    if "health_conditions" not in st.session_state:
        st.session_state.health_conditions = []
    
    if "health_alerts" not in st.session_state:
        st.session_state.health_alerts = []
    
    if "diet_rules" not in st.session_state:
        st.session_state.diet_rules = []
    
    if "diet_plan" not in st.session_state:
        st.session_state.diet_plan = None
    
    if "pdf_export" not in st.session_state:
        st.session_state.pdf_export = None
    
    if "json_export" not in st.session_state:
        st.session_state.json_export = None
    
    if "processing_time" not in st.session_state:
        st.session_state.processing_time = 0.0
    
    if "patient_id" not in st.session_state:
        st.session_state.patient_id = None
    
    if "patient_profile" not in st.session_state:
        st.session_state.patient_profile = None


def render_sidebar():
    """
    Render the sidebar with navigation menu.
    
    Provides navigation between four main pages:
    - Upload: Upload medical reports
    - Review: Review extracted health data
    - Diet Plan: View personalized diet plan
    - History: View patient history
    """
    with st.sidebar:
        st.title("AI NutriCare System")
        st.markdown("---")
        
        # Navigation menu
        pages = ["Upload", "Review", "Diet Plan", "History"]
        
        for page in pages:
            if st.button(
                page,
                key=f"nav_{page}",
                use_container_width=True,
                type="primary" if st.session_state.current_page == page else "secondary"
            ):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        
        # Display current status
        st.subheader("Status")
        if st.session_state.report_id:
            st.success(f"Report ID: {st.session_state.report_id[:8]}...")
        else:
            st.info("No report uploaded")
        
        if st.session_state.processing_status:
            st.info(f"Status: {st.session_state.processing_status}")


def render_upload_page():
    """
    Render the upload page for medical report submission.
    
    Features:
    - File upload with drag-and-drop
    - Format validation
    - Size limit display
    - Upload progress indication
    - Real backend integration with AINutriCareOrchestrator
    
    Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5
    """
    st.header("Upload Medical Report")
    
    st.markdown("""
    Upload your medical report to get started with personalized diet planning.
    The system will extract health data and generate recommendations based on your results.
    """)
    
    # Display supported formats and size limits (Requirement 13.5)
    with st.expander("ℹ️ Supported Formats and Requirements", expanded=False):
        st.markdown("""
        **Supported File Formats:**
        - PDF documents (.pdf)
        - JPEG images (.jpg, .jpeg)
        - PNG images (.png)
        - TIFF images (.tif, .tiff)
        - Plain text files (.txt)
        
        **File Size Limit:** Maximum 10 MB
        
        **Tips for Best Results:**
        - Ensure documents are clear and readable
        - Use high-resolution scans (300 DPI recommended)
        - Avoid blurry or low-quality images
        """)
    
    # File upload component with drag-and-drop (Requirement 13.1)
    uploaded_file = st.file_uploader(
        "Choose a medical report file",
        type=["pdf", "jpg", "jpeg", "png", "tif", "tiff", "txt"],
        help="Drag and drop a file or click to browse",
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        # Display file information
        file_size_mb = uploaded_file.size / (1024 * 1024)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{file_size_mb:.2f} MB")
        with col3:
            st.metric("File Type", uploaded_file.type)
        
        # Validate file size (Requirement 13.4)
        if file_size_mb > 10:
            st.error("❌ File size exceeds 10 MB limit. Please upload a smaller file.")
            return
        
        # Optional: Patient profile input
        with st.expander("📋 Patient Information (Optional)", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", min_value=1, max_value=120, value=30)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                height_cm = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
            with col2:
                weight_kg = st.number_input("Weight (kg)", min_value=20, max_value=300, value=70)
                activity_level = st.selectbox(
                    "Activity Level",
                    ["sedentary", "light", "moderate", "active", "very_active"]
                )
        
        # Optional: Dietary preferences
        with st.expander("🥗 Dietary Preferences (Optional)", expanded=False):
            dietary_style = st.selectbox(
                "Dietary Style",
                ["None", "Vegetarian", "Vegan", "Keto", "Paleo", "Mediterranean"]
            )
            allergies_input = st.text_input(
                "Allergies (comma-separated)",
                placeholder="e.g., peanuts, shellfish, dairy"
            )
            dislikes_input = st.text_input(
                "Foods to Avoid (comma-separated)",
                placeholder="e.g., mushrooms, olives"
            )
        
        # Process button
        if st.button("Process Report", type="primary", use_container_width=True):
            # Show progress bar (Requirement 13.2)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Import orchestrator
                status_text.text("Loading modules...")
                from ai_diet_planner.main import AINutriCareOrchestrator
                from ai_diet_planner.processor.report_processor import UploadedFile
                from ai_diet_planner.models import PatientProfile, UserPreferences
                
                # Initialize orchestrator with lazy loading
                status_text.text("Initializing system (this may take a moment on first run)...")
                progress_bar.progress(10)
                
                # Use environment variables for configuration
                import os
                ocr_backend = os.getenv("NUTRICARE_OCR_BACKEND", "tesseract")
                nlp_model = os.getenv("NUTRICARE_NLP_MODEL", "groq")
                
                # Show which model is being used
                st.info(f"🤖 Using NLP Model: {nlp_model.upper()}")
                
                try:
                    orchestrator = AINutriCareOrchestrator(
                        ocr_backend=ocr_backend,
                        nlp_model=nlp_model
                    )
                    status_text.text("System initialized successfully!")
                except Exception as init_error:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ Failed to initialize system: {init_error}")
                    st.markdown("""
                    **Common Issues:**
                    1. **Missing API Keys**: Make sure you have set up your API keys in the `.env` file
                    2. **Missing Dependencies**: Run `pip install -r requirements.txt`
                    3. **Groq Library**: If using Groq, run `pip install groq`
                    
                    **Quick Fix:**
                    - See `GROQ_SETUP.md` for detailed setup instructions
                    - Or check `TROUBLESHOOTING.md` for more help
                    """)
                    return
                
                # Prepare uploaded file
                status_text.text("Validating file...")
                progress_bar.progress(20)
                file_content = uploaded_file.read()
                uploaded_file.seek(0)  # Reset file pointer
                
                uploaded_file_obj = UploadedFile(
                    filename=uploaded_file.name,
                    content=file_content
                )
                
                # Prepare patient profile if provided
                patient_profile = None
                if 'age' in locals():
                    status_text.text("Processing patient information...")
                    progress_bar.progress(30)
                    
                    # Parse allergies and dislikes
                    allergies = [a.strip() for a in allergies_input.split(",")] if allergies_input else []
                    dislikes = [d.strip() for d in dislikes_input.split(",")] if dislikes_input else []
                    
                    user_preferences = UserPreferences(
                        dietary_style=dietary_style if dietary_style != "None" else None,
                        allergies=allergies,
                        dislikes=dislikes,
                        cultural_preferences=[]
                    )
                    
                    patient_profile = PatientProfile(
                        patient_id="",  # Will be generated by data store
                        age=age,
                        gender=gender,
                        height_cm=height_cm,
                        weight_kg=weight_kg,
                        activity_level=activity_level,
                        preferences=user_preferences,
                        created_at=None  # Will be set by data store
                    )
                else:
                    user_preferences = UserPreferences(
                        dietary_style=None,
                        allergies=[],
                        dislikes=[],
                        cultural_preferences=[]
                    )
                
                # Process report through pipeline
                status_text.text("Extracting text from report...")
                progress_bar.progress(40)
                
                result = orchestrator.process_report(
                    uploaded_file=uploaded_file_obj,
                    patient_profile=patient_profile,
                    user_preferences=user_preferences,
                    export_pdf=True,
                    export_json=True
                )
                
                progress_bar.progress(100)
                
                # Check result status
                if result.status.value == "completed":
                    # Store results in session state
                    st.session_state.report_id = result.report_id
                    st.session_state.processing_status = "Completed"
                    st.session_state.extracted_data = result.structured_data
                    st.session_state.textual_notes = result.textual_notes
                    st.session_state.health_conditions = result.health_conditions
                    st.session_state.health_alerts = result.alerts
                    st.session_state.diet_rules = result.diet_rules
                    st.session_state.diet_plan = result.diet_plan
                    st.session_state.pdf_export = result.pdf_export
                    st.session_state.json_export = result.json_export
                    st.session_state.processing_time = result.processing_time
                    
                    # Display success message (Requirement 13.3)
                    status_text.empty()
                    st.success(f"✅ Report processed successfully in {result.processing_time:.1f}s!")
                    
                    # Show summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Health Metrics", len(result.structured_data.metrics) if result.structured_data else 0)
                    with col2:
                        st.metric("Conditions Detected", len(result.health_conditions))
                    with col3:
                        st.metric("Alerts", len(result.alerts))
                    
                    st.info("📊 Navigate to the 'Review' page to see detailed health data.")
                    st.info("🥗 Navigate to the 'Diet Plan' page to view your personalized diet plan.")
                    
                else:
                    # Display error message (Requirement 13.4)
                    status_text.empty()
                    st.error(f"❌ Processing failed: {result.error_message}")
                    
                    # Provide resolution steps
                    st.markdown("""
                    **Troubleshooting Steps:**
                    1. Ensure the document is clear and readable
                    2. Try uploading a higher quality scan
                    3. Verify the file format is supported
                    4. Check that the document contains health metrics
                    """)
                    
            except Exception as e:
                # Display error message (Requirement 13.4)
                status_text.empty()
                progress_bar.empty()
                st.error(f"❌ An error occurred: {str(e)}")
                
                # Show detailed error in expander for debugging
                with st.expander("Error Details"):
                    st.code(str(e))
                
                st.markdown("""
                **Please try:**
                1. Refreshing the page and uploading again
                2. Using a different file format
                3. Contacting support if the issue persists
                """)
    else:
        st.info("👆 Please upload a medical report to continue.")


def render_review_page():
    """
    Render the review page for viewing extracted health data.
    
    Features:
    - Display extracted health metrics
    - Show health alerts
    - Allow data corrections
    - Highlight abnormal values
    """
    st.header("Review Health Data")
    
    if not st.session_state.report_id:
        st.warning("⚠️ No report uploaded. Please upload a report first.")
        if st.button("Go to Upload Page"):
            st.session_state.current_page = "Upload"
            st.rerun()
        return
    
    st.markdown("""
    Review the extracted health data from your medical report.
    You can verify the accuracy and make corrections if needed.
    """)
    
    # Display extracted health metrics
    if st.session_state.extracted_data:
        st.subheader("📊 Health Metrics")
        
        if st.session_state.extracted_data.metrics:
            # Create metrics table
            metrics_data = []
            for metric in st.session_state.extracted_data.metrics:
                metrics_data.append({
                    "Metric": metric.metric_type.value.replace('_', ' ').title(),
                    "Value": f"{metric.value:.1f}",
                    "Unit": metric.unit,
                    "Confidence": f"{metric.confidence * 100:.0f}%"
                })
            
            import pandas as pd
            df = pd.DataFrame(metrics_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No health metrics extracted from the report.")
        
        st.markdown("---")
    
    # Display health conditions
    if st.session_state.health_conditions:
        st.subheader("🏥 Detected Health Conditions")
        
        for condition in st.session_state.health_conditions:
            condition_name = condition.condition_type.value.replace('_', ' ').title()
            confidence_pct = condition.confidence * 100
            
            # Color code by confidence
            if confidence_pct >= 80:
                st.error(f"**{condition_name}** - Confidence: {confidence_pct:.1f}%")
            elif confidence_pct >= 60:
                st.warning(f"**{condition_name}** - Confidence: {confidence_pct:.1f}%")
            else:
                st.info(f"**{condition_name}** - Confidence: {confidence_pct:.1f}%")
        
        st.markdown("---")
    
    # Display health alerts
    if st.session_state.health_alerts:
        st.subheader("⚠️ Health Alerts")
        
        for alert in st.session_state.health_alerts:
            metric_name = alert.metric_type.value.replace('_', ' ').title()
            
            # Color code by severity
            if alert.severity.value == "critical":
                st.error(f"🔴 **{metric_name}**: {alert.message}")
            elif alert.severity.value == "warning":
                st.warning(f"🟡 **{metric_name}**: {alert.message}")
            else:
                st.info(f"🔵 **{metric_name}**: {alert.message}")
            
            if alert.recommended_action:
                st.caption(f"   Recommended: {alert.recommended_action}")
        
        st.markdown("---")
    
    # Display textual notes
    if st.session_state.textual_notes:
        st.subheader("📝 Doctor's Notes")
        
        for note in st.session_state.textual_notes:
            with st.expander(f"{note.section.replace('_', ' ').title()}", expanded=False):
                st.write(note.content)
    
    # Navigation button
    if st.button("➡️ View Diet Plan", type="primary", use_container_width=True):
        st.session_state.current_page = "Diet Plan"
        st.rerun()


def render_diet_plan_page():
    """
    Render the diet plan page for viewing personalized recommendations.
    
    Features:
    - Display daily meal plan
    - Show nutritional information
    - Visualize macronutrient balance
    - Provide export options (PDF, JSON)
    """
    st.header("Personalized Diet Plan")
    
    if not st.session_state.report_id:
        st.warning("⚠️ No report uploaded. Please upload a report first.")
        if st.button("Go to Upload Page"):
            st.session_state.current_page = "Upload"
            st.rerun()
        return
    
    if not st.session_state.diet_plan:
        st.warning("⚠️ Diet plan not yet generated.")
        if st.button("Go to Upload Page"):
            st.session_state.current_page = "Upload"
            st.rerun()
        return
    
    diet_plan = st.session_state.diet_plan
    
    # Display daily summary
    st.subheader("📈 Daily Nutritional Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Daily Calories", f"{diet_plan.daily_calories:.0f} kcal")
    with col2:
        st.metric("Protein", f"{diet_plan.macronutrient_targets.protein_percent:.0f}%")
    with col3:
        st.metric("Carbs", f"{diet_plan.macronutrient_targets.carbs_percent:.0f}%")
    with col4:
        st.metric("Fat", f"{diet_plan.macronutrient_targets.fat_percent:.0f}%")
    
    st.markdown("---")
    
    # Display meals
    st.subheader("🍽️ Daily Meal Plan")
    
    for meal in diet_plan.meals:
        meal_name = meal.meal_type.value.title()
        
        with st.expander(f"**{meal_name}** ({meal.total_calories:.0f} kcal)", expanded=True):
            # Meal summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Protein", f"{meal.total_protein_g:.1f}g")
            with col2:
                st.metric("Carbs", f"{meal.total_carbs_g:.1f}g")
            with col3:
                st.metric("Fat", f"{meal.total_fat_g:.1f}g")
            
            # Food items
            st.markdown("**Foods:**")
            for portion in meal.portions:
                st.write(f"• **{portion.food.name}** - {portion.amount:.0f} {portion.unit} "
                        f"({portion.calories:.0f} kcal)")
    
    st.markdown("---")
    
    # Display recommendations
    if diet_plan.recommendations:
        st.subheader("💡 Dietary Recommendations")
        
        for rec in diet_plan.recommendations:
            st.info(rec)
    
    st.markdown("---")
    
    # Export options
    st.subheader("📥 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.pdf_export:
            st.download_button(
                label="📄 Download PDF Report",
                data=st.session_state.pdf_export,
                file_name=f"diet_plan_{st.session_state.report_id[:8]}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.info("PDF export not available")
    
    with col2:
        if st.session_state.json_export:
            st.download_button(
                label="📋 Download JSON Data",
                data=st.session_state.json_export,
                file_name=f"diet_plan_{st.session_state.report_id[:8]}.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.info("JSON export not available")
    
    st.markdown("---")
    
    # Weekly Plan Generation
    st.subheader("📅 Weekly Diet Plan")
    st.write("Generate a complete 7-day meal plan with varied meals for the entire week.")
    
    if st.button("🗓️ Generate Weekly Plan", type="primary", use_container_width=True):
        with st.spinner("Generating 7-day meal plan..."):
            try:
                from ai_diet_planner.main import AINutriCareOrchestrator
                from ai_diet_planner.generation.diet_planner import DietPlanGenerator
                
                # Get the orchestrator components
                orchestrator = AINutriCareOrchestrator()
                
                # Get patient profile from session or create default
                if hasattr(st.session_state, 'extracted_data') and st.session_state.extracted_data:
                    # Use existing patient profile
                    patient_profile = st.session_state.diet_plan.patient_id
                    # Reconstruct patient profile from diet plan
                    from ai_diet_planner.models import PatientProfile, UserPreferences
                    
                    # Create a basic patient profile
                    patient_profile = PatientProfile(
                        patient_id=st.session_state.diet_plan.patient_id,
                        age=30,  # Default values
                        gender="male",
                        height_cm=170,
                        weight_kg=70,
                        activity_level="moderate",
                        preferences=UserPreferences(
                            dietary_style=None,
                            allergies=[],
                            dislikes=[],
                            cultural_preferences=[]
                        ),
                        created_at=datetime.now()
                    )
                
                # Generate weekly plan
                diet_generator = DietPlanGenerator()
                weekly_plans = diet_generator.generate_weekly_plan(
                    patient_profile=patient_profile,
                    health_conditions=st.session_state.health_conditions,
                    diet_rules=st.session_state.diet_rules,
                    preferences=patient_profile.preferences
                )
                
                # Store in session state
                st.session_state.weekly_plans = weekly_plans
                st.success("✅ Weekly plan generated successfully!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Failed to generate weekly plan: {e}")
    
    # Display weekly plan if generated
    if hasattr(st.session_state, 'weekly_plans') and st.session_state.weekly_plans:
        st.markdown("---")
        st.subheader("📆 7-Day Meal Plan")
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Day selector
        selected_day = st.selectbox("Select Day", days, key="day_selector")
        day_index = days.index(selected_day)
        
        daily_plan = st.session_state.weekly_plans[day_index]
        
        # Display selected day's plan
        st.markdown(f"### {selected_day}'s Plan")
        
        # Daily summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Calories", f"{daily_plan.daily_calories:.0f} kcal")
        with col2:
            st.metric("Protein", f"{daily_plan.macronutrient_targets.protein_percent:.0f}%")
        with col3:
            st.metric("Carbs", f"{daily_plan.macronutrient_targets.carbs_percent:.0f}%")
        with col4:
            st.metric("Fat", f"{daily_plan.macronutrient_targets.fat_percent:.0f}%")
        
        # Display meals for selected day
        for meal in daily_plan.meals:
            meal_name = meal.meal_type.value.title()
            
            with st.expander(f"**{meal_name}** ({meal.total_calories:.0f} kcal)", expanded=False):
                # Meal summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Protein", f"{meal.total_protein_g:.1f}g")
                with col2:
                    st.metric("Carbs", f"{meal.total_carbs_g:.1f}g")
                with col3:
                    st.metric("Fat", f"{meal.total_fat_g:.1f}g")
                
                # Food items
                st.markdown("**Foods:**")
                for portion in meal.portions:
                    st.write(f"• **{portion.food.name}** - {portion.amount:.0f} {portion.unit} "
                            f"({portion.calories:.0f} kcal)")
    
    st.markdown("---")
    
    st.markdown("""
    Your personalized diet plan based on your health analysis.
    """)
    
    # Placeholder for diet plan display
    if st.session_state.diet_plan:
        st.subheader("Daily Meal Plan")
        # TODO: Display meals organized by meal type
        st.info("Diet plan will be displayed here.")
        
        st.subheader("Nutritional Summary")
        # TODO: Display macronutrient charts
        st.info("Nutritional charts will be displayed here.")
        
        st.subheader("Export Options")
        col1, col2 = st.columns(2)
        with col1:
            st.button("📄 Export as PDF", use_container_width=True)
        with col2:
            st.button("📋 Export as JSON", use_container_width=True)
    else:
        st.info("Diet plan will be generated after health data review.")
        
        # Simulate diet plan generation
        if st.button("Generate Diet Plan"):
            with st.spinner("Generating personalized diet plan..."):
                import time
                time.sleep(2)
                st.session_state.diet_plan = {"status": "generated"}
                st.rerun()


def render_history_page():
    """
    Render the history page for viewing past reports and diet plans.
    
    Features:
    - List all past medical reports
    - Display previous diet plans
    - Allow selection and viewing of historical data
    - Show timeline of health progress
    """
    st.header("Patient History")
    
    st.markdown("""
    View your past medical reports and diet plans.
    Track your health progress over time.
    """)
    
    # Placeholder for patient history
    if st.session_state.patient_id:
        st.subheader("Past Reports")
        # TODO: Display list of past reports
        st.info("Historical reports will be displayed here.")
        
        st.subheader("Previous Diet Plans")
        # TODO: Display list of previous diet plans
        st.info("Previous diet plans will be displayed here.")
    else:
        st.info("No patient profile found. Upload a report to create a profile.")


def main():
    """
    Main application entry point.
    
    Sets up the Streamlit page configuration, initializes session state,
    and renders the appropriate page based on navigation.
    """
    # Page configuration
    st.set_page_config(
        page_title="AI NutriCare System",
        page_icon="🥗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar navigation
    render_sidebar()
    
    # Render current page
    if st.session_state.current_page == "Upload":
        render_upload_page()
    elif st.session_state.current_page == "Review":
        render_review_page()
    elif st.session_state.current_page == "Diet Plan":
        render_diet_plan_page()
    elif st.session_state.current_page == "History":
        render_history_page()


if __name__ == "__main__":
    main()
