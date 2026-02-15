"""
Example usage of the AI NutriCare System UI.

This script demonstrates how to run the Streamlit application.

To run the application:
    streamlit run ui/app.py

Or from the command line:
    python -m streamlit run ui/app.py

The application will open in your default web browser at http://localhost:8501
"""

import subprocess
import sys
from pathlib import Path


def run_streamlit_app():
    """
    Run the Streamlit application.
    
    This function starts the Streamlit server and opens the application
    in the default web browser.
    """
    # Get the path to app.py
    app_path = Path(__file__).parent / "app.py"
    
    # Run streamlit
    try:
        print("Starting AI NutriCare System...")
        print("The application will open in your browser at http://localhost:8501")
        print("Press Ctrl+C to stop the server")
        print("-" * 60)
        
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path)
        ])
    except KeyboardInterrupt:
        print("\nShutting down AI NutriCare System...")
    except Exception as e:
        print(f"Error running application: {e}")
        print("\nPlease ensure Streamlit is installed:")
        print("  pip install streamlit>=1.28.0")


if __name__ == "__main__":
    run_streamlit_app()
