#!/usr/bin/env python3
"""
Build script for AtlasMogo using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_app():
    """Build the AtlasMogo application using PyInstaller."""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    icon_path = project_root / "resources" / "icons" / "icon.ico"
    main_script = project_root / "main.py"
    
    # Check if icon file exists
    if not icon_path.exists():
        print(f"Warning: Icon file not found at {icon_path}")
        print("Building without custom icon...")
        icon_arg = []
    else:
        print(f"Using icon: {icon_path}")
        icon_arg = ["--icon", str(icon_path)]
    
    # PyInstaller command
    cmd = [
        "python", "-m", "PyInstaller",
        "--noconsole",  # No console window
        "--onefile",    # Single executable
        "--name", "AtlasMogo",  # Executable name
        "--add-data", f"{project_root}/resources{os.pathsep}resources",  # Include resources
        "--add-data", f"{project_root}/config{os.pathsep}config",  # Include config
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtWidgets", 
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "qtawesome",
        "--hidden-import", "pymongo",
        "--hidden-import", "bson",
        "--clean",  # Clean cache
    ] + icon_arg + [str(main_script)]
    
    print("Building AtlasMogo with PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        print("Output:", result.stdout)
        
        # Check if executable was created
        dist_dir = project_root / "dist"
        exe_path = dist_dir / "AtlasMogo.exe"
        
        if exe_path.exists():
            print(f"\nExecutable created: {exe_path}")
            print(f"Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        else:
            print("Warning: Executable not found in dist directory")
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: PyInstaller not found. Please install it with: pip install pyinstaller")
        print("Or run with: python -m PyInstaller")
        return False
    
    return True

def clean_build():
    """Clean build artifacts."""
    project_root = Path(__file__).parent
    
    # Directories to clean
    dirs_to_clean = ["build", "dist", "__pycache__"]
    
    for dir_name in dirs_to_clean:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"Cleaning {dir_path}...")
            shutil.rmtree(dir_path)
    
    # Clean .spec files
    for spec_file in project_root.glob("*.spec"):
        print(f"Removing {spec_file}...")
        spec_file.unlink()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean_build()
        print("Build artifacts cleaned.")
    else:
        build_app()
