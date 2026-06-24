#!/usr/bin/env python3
"""Environment validation for the Musicom Framework."""
import sys
import importlib

REQUIRED_LIBS = [
    "music21", 
    "musicpy", 
    "mido", 
    "numpy", 
    "pedalboard",
    "soundfile"
]

def check_lib(lib):
    try:
        importlib.import_module(lib)
        return True
    except ImportError:
        return False

def main():
    print("=== Musicom Environment Validation ===")
    all_pass = True
    for lib in REQUIRED_LIBS:
        status = "PASSED" if check_lib(lib) else "FAILED"
        if status == "FAILED":
            all_pass = False
        print(f"  {lib:12s}: {status}")
    
    print("\nVerification Result: ", end="")
    if all_pass:
        print("OK - Environment is ready for composition.")
        sys.exit(0)
    else:
        print("ERROR - Missing dependencies. Please check your Docker/venv setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()
