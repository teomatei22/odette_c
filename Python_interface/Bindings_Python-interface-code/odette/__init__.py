"""
ODETTE - Orbital Determination and Tracking for Earth-orbiting Satellites
"""

# Import the satellite_core module to make it available as odette.satellite_core
try:
    from .satellite_core import *
except ImportError:
    # If the module is not yet built, provide a helpful message
    import sys
    print("Error: The satellite_core module could not be imported.")
    print("Please make sure the C++ extension has been built correctly.")
    sys.exit(1)

__version__ = "0.1.0"
