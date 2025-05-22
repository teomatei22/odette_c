from odette import satellite_core

# Print the module structure
print(dir(satellite_core))

# Print the structure of submodules
print("\nRADec:")
print(dir(satellite_core.RADec))

print("\nTLE:")
print(dir(satellite_core.TLE))

print("\nTwoLineElements:")
print(dir(satellite_core.TwoLineElement))

print("\nOrbmath:")
print(dir(satellite_core.orbmath))

print("\nPropagate:")
print(dir(satellite_core.propagate))

print("\nFrames:")
print(dir(satellite_core.frames))
