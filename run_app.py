"""
Startup script to run the Streamlit Notice Board application.
"""

import subprocess
import sys
import os

def run_streamlit_app():
    """Run the Streamlit application."""
    
    print("Starting Notice Board Streamlit Application...")
    print("=" * 50)
    
    # Ensure we're in the correct directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    
    # Run the Streamlit app
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port=8501",
            "--server.address=localhost"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    run_streamlit_app()
