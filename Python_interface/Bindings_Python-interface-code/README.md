# ODETTE - Satellite Tracking Core Library

Python bindings for the C++ core library of the ODETTE project, providing satellite tracking, orbit determination, and propagation functionality.

## Features

- TLE parsing and SGP4 propagation
- Orbit determination from optical observations (RA/Dec)
- Advanced orbit propagation with various perturbation models
- Frame transformations (ECEF, ECI)
- TDM file parsing
- Orbital mathematics utilities

## Installation

### Prerequisites

- CMake (>= 3.12)
- C++ compiler with C++17 support
- Python (>= 3.8)
- Eigen3
- pybind11

### Building from source

```bash
# Clone the repository
git clone https://github.com/yourusername/odette.git
cd odette

# Install using pip
pip install .
```

## Usage Example

```python
import numpy as np
from odette import satellite_core as sc

# Parse a TLE
tle = sc.TwoLineElement()
sc.parse_tle_lines(tle, 
    "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927",
    "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537")

# Get position and velocity
r = np.zeros(3)
v = np.zeros(3)
sc.get_rv(tle, 0.0, r, v)  # At TLE epoch
print(f"Position: {r} km")
print(f"Velocity: {v} km/s")
```

## Documentation

For detailed documentation, please refer to the [project wiki](https://github.com/yourusername/odette/wiki).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
