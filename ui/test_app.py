"""
Unit tests for the Streamlit application.

Tests the session state initialization and page rendering functions.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.app import initialize_session_state


class MockSessionState:
    """Mock class that mimics Streamlit's session_state behavior."""
    
    def __init__(self):
        self._state = {}
    
    def __contains__(self, key):
        return key in self._state
    
    def __getattr__(self, key):
        if key.startswith('_'):
            return object.__getattribute__(self, key)
        return self._state.get(key)
    
    def __setattr__(self, key, value):
        if key.startswith('_'):
            object.__setattr__(self, key, value)
        else:
            self._state[key] = value
    
    def __getitem__(self, key):
        return self._state[key]
    
    def get_state(self):
        return self._state


class TestSessionState:
    """Test session state initialization and management."""
    
    def test_initialize_session_state_creates_all_variables(self):
        """
        Test that initialize_session_state creates all required session state variables.
        
        Validates: Requirements 13.1 (session state management)
        """
        # Mock streamlit session state
        mock_session_state = MockSessionState()
        
        with patch('ui.app.st') as mock_st:
            mock_st.session_state = mock_session_state
            
            # Call initialization
            initialize_session_state()
            
            # Verify all required variables are created
            required_vars = [
                "current_page",
                "uploaded_file",
                "report_id",
                "processing_status",
                "extracted_data",
                "health_alerts",
                "diet_plan",
                "patient_id",
                "patient_profile"
            ]
            
            state = mock_session_state.get_state()
            for var in required_vars:
                assert var in state, f"Missing session state variable: {var}"
    
    def test_initialize_session_state_default_values(self):
        """
        Test that session state variables have correct default values.
        """
        mock_session_state = MockSessionState()
        
        with patch('ui.app.st') as mock_st:
            mock_st.session_state = mock_session_state
            
            initialize_session_state()
            
            # Verify default values
            state = mock_session_state.get_state()
            assert state["current_page"] == "Upload"
            assert state["uploaded_file"] is None
            assert state["report_id"] is None
            assert state["processing_status"] is None
            assert state["extracted_data"] is None
            assert state["health_alerts"] == []
            assert state["diet_plan"] is None
            assert state["patient_id"] is None
            assert state["patient_profile"] is None
    
    def test_initialize_session_state_preserves_existing_values(self):
        """
        Test that initialize_session_state doesn't overwrite existing values.
        """
        mock_session_state = MockSessionState()
        mock_session_state.current_page = "Review"
        mock_session_state.report_id = "test-123"
        
        with patch('ui.app.st') as mock_st:
            mock_st.session_state = mock_session_state
            
            initialize_session_state()
            
            # Verify existing values are preserved
            state = mock_session_state.get_state()
            assert state["current_page"] == "Review"
            assert state["report_id"] == "test-123"
            
            # Verify new variables are added
            assert "uploaded_file" in state


class TestPageNavigation:
    """Test page navigation and routing."""
    
    def test_all_pages_defined(self):
        """
        Test that all required pages are defined in the navigation.
        
        Validates: Requirements 13.1 (multi-page navigation)
        """
        # Import the render_sidebar function to check page definitions
        from ui.app import render_sidebar
        
        # The pages should be: Upload, Review, Diet Plan, History
        expected_pages = ["Upload", "Review", "Diet Plan", "History"]
        
        # This is validated by the implementation in render_sidebar
        # We verify the pages list exists in the function
        import inspect
        source = inspect.getsource(render_sidebar)
        
        for page in expected_pages:
            assert page in source, f"Page '{page}' not found in navigation"


class TestFileUpload:
    """Test file upload functionality."""
    
    def test_supported_file_formats(self):
        """
        Test that the upload page supports all required file formats.
        
        Validates: Requirements 13.5 (supported file formats)
        """
        from ui.app import render_upload_page
        
        # Check that the function mentions supported formats
        import inspect
        source = inspect.getsource(render_upload_page)
        
        supported_formats = ["pdf", "jpg", "jpeg", "png", "tif", "tiff", "txt"]
        
        for fmt in supported_formats:
            assert fmt in source, f"Format '{fmt}' not mentioned in upload page"
    
    def test_file_size_limit_displayed(self):
        """
        Test that the file size limit is displayed to users.
        
        Validates: Requirements 13.5 (size limits display)
        """
        from ui.app import render_upload_page
        
        import inspect
        source = inspect.getsource(render_upload_page)
        
        # Check that 10 MB limit is mentioned
        assert "10 MB" in source or "10MB" in source, "File size limit not displayed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
