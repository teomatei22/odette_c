#!/usr/bin/env python3

import os
import time
from datetime import datetime, timedelta
import numpy as np
from odette import satellite_core as sc
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math

def gauss_tle_altitude_test():
    """
    Python implementation of gauss_tle_altitude_test from C++
    Tests the Gauss method for orbit determination compared to TLE data
    """
    # Open file for test outputs
    with open("tle_altitude_test.txt", "w") as test_outputs:
        
        t1 = time.time()
        cntr = 0
        lim = ((300 - 10) // 10) * ((30 - 5) // 5)
        
        for delta in range(10, 60 * 5 + 1, 10):
            for delta_error in range(5, 31, 5):
                cntr += 1
                
                try:
                    # Parse TDM files - assuming we have the same directory structure
                    tdms = sc.parse_tdm_w("data/Jason/20240318_16002A_A*", delta, delta_error)
                    
                    # Create RADec object from observations
                    radec = sc.RADec(tdms.observations)
                    
                    # TLE data
                    line1 = "1 41240U 16002A   24078.93311235 -.00000041  00000-0  88455-4 0  9998"
                    line2 = "2 41240  66.0433  38.7934 0008217 275.1931  84.8147 12.80929479381943"
                    
                    # Create TLE object
                    tle = sc.TwoLineElement(line1, line2)
                    
                    # Get position and velocity from TLE
                    pos_tle = tle.get_position()
                    vel_tle = tle.get_velocity()
                    
                    # Calculate altitude from RADec
                    position = radec.get_position()
                    altitude = np.linalg.norm(position) - 6378
                    
                    results = []
                    results.append(f"TLE Altitude: {altitude} at delta: {delta} delta_error: {delta_error}")
                    results.append(f"for {len(tdms.observations)} observations, speed: {np.linalg.norm(radec.get_velocity())}")
                    results.append("")
                    
                    # Calculate TLE altitude difference
                    altitude_tle = np.linalg.norm(pos_tle) - 6378
                    results.append(f"TDM Altitude difference: {abs(altitude_tle - altitude)}")
                    results.append(f"speed difference: {abs(np.linalg.norm(vel_tle) - np.linalg.norm(radec.get_velocity()))}")
                    results.append("")
                    
                    # Calculate orbital elements for both methods
                    elems = sc.orbmath.compute_orbital_elements(position, radec.get_velocity())
                    tle_elems = sc.orbmath.compute_orbital_elements(pos_tle, vel_tle)
                    
                    # Compare orbital elements
                    results.append("ORBITAL ELEMENTS:")
                    results.append(f"[a: {elems.a}, a_tle: {tle_elems.a}]")
                    results.append(f"[e: {elems.ecc}, e_tle: {tle_elems.ecc}]")
                    results.append(f"[i: {elems.incl}, i_tle: {tle_elems.incl}]")
                    results.append(f"[raan: {elems.Omega}, raan_tle: {tle_elems.Omega}]")
                    results.append(f"[argp: {elems.omega}, argp_tle: {tle_elems.omega}]")
                    results.append(f"[nu: {elems.nu}, nu_tle: {tle_elems.nu}]")
                    results.append(f"[M: {elems.m}, M_tle: {tle_elems.m}]")
                    results.append("=============================================================================")
                    
                    # Check if the result is successful
                    if 1330 < altitude < 1345:
                        results.append("[SUCCESS]")
                    else:
                        results.append("[FAILURE]")
                    
                    # Write all results to file
                    test_outputs.write("\n".join(results) + "\n")
                    
                except Exception as ex:
                    # Just continue on exception like in the C++ version
                    continue
            
            # Print progress
            print(f"{cntr}/{lim}")
        
        t2 = time.time()
        
        # Write execution time
        test_outputs.write(f"Executed {cntr} operations in {int((t2 - t1) * 1000)} ms\n")
    
    return True
    
def propagate_tle_3d(line1=None, line2=None, time_span_hours=6, step_minutes=0.5):
    """
    Visualize satellite orbit using TLE data with matplotlib
    
    Args:
        line1 (str): First line of TLE
        line2 (str): Second line of TLE
        time_span_hours (float): Time span to propagate in hours
        step_minutes (float): Time step in minutes
    """
    if line1 is None:
        line1 = "1 41240U 16002A   24078.54273252 -.00000041  00000-0  87212-4 0  9991"
    if line2 is None:
        line2 = "2 41240  66.0433  39.6041 0008216 275.2526  84.7552 12.80929447381890"
    
    # Propagate orbit
    try:
        # From the bindings we can see that TwoLineElement is the actual implementation class
        # that has the get_position_at method
        print("Using TwoLineElement class...")
        
        tle_obj = sc.TwoLineElement(line1, line2)
        
        # Get epoch time in Julian date
        time_jd = tle_obj.get_jd()
        
        # Initialize positions array
        positions = []
        
        # Propagate orbit
        for dt in np.arange(0, time_span_hours * 60, step_minutes):
            # Get position at current time using get_position_at (which is bound as "get_position_at")
            # The bindings show this takes minutes as an argument, just like in the C++ code
            r_ecef = tle_obj.get_position_at(float(dt))
            
            # Convert to ECI
            r_eci = sc.frames.to_eci(r_ecef, time_jd + dt * 60 / (24 * 60 * 60))
            positions.append(r_eci / 6378.0)  # Normalize by Earth radius
        
    except AttributeError as e:
        print(f"Error: {e}")
        print("It seems we're using a different version of the odette library.")
        print("Let's try an alternative approach.")
        
        try:
            # Create a TLE object using the older interface
            print("Using TLE class...")
            tle = sc.TLE()
            sc.parse_tle_lines(tle, line1, line2)
            
            # Get epoch time in Julian date
            time_jd = tle.epoch
            
            # Create TwoLineElement using a different constructor if available
            try:
                tle_obj = sc.TwoLineElement(line1, line2)
                
                # Propagate orbit
                for dt in np.arange(0, time_span_hours * 60, step_minutes):
                    r_ecef = tle_obj.get_position_at(float(dt))
                    r_eci = sc.frames.to_eci(r_ecef, time_jd + dt * 60 / (24 * 60 * 60))
                    positions.append(r_eci / 6378.0)
            
            except Exception as e2:
                print(f"Error creating TwoLineElement: {e2}")
                
                # If that fails, try using the old get_rv function
                for dt in np.arange(0, time_span_hours * 60, step_minutes):
                    # Based on the bindings, get_rv expects (tle, minutes_after_epoch, r, v)
                    # where r and v are likely C++ vectors or arrays that get filled
                    
                    # Try using ctypes arrays
                    import ctypes
                    
                    # Create ctypes arrays for r and v
                    r_array = (ctypes.c_double * 3)()
                    v_array = (ctypes.c_double * 3)()
                    
                    # Call get_rv
                    sc.get_rv(tle, float(dt), r_array, v_array)
                    
                    # Convert to numpy array
                    r_vec = np.array([r_array[0], r_array[1], r_array[2]])
                    
                    # Convert to ECI
                    r_eci = sc.frames.to_eci(r_vec, time_jd + dt * 60 / (24 * 60 * 60))
                    positions.append(r_eci / 6378.0)
                
        except Exception as e:
            print(f"All approaches failed: {e}")
            print("Based on the bindings file, you should be able to use TwoLineElement class with")
            print("get_position_at method, or possibly TLE class with get_rv function.")
            return
    
    # Only continue if we have positions data
    if not positions:
        print("Failed to calculate orbit positions.")
        return
    
    # Convert positions list to numpy array
    positions = np.array(positions)
    
    # Setup 3D plot
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot Earth
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)
    ax.plot_surface(x, y, z, color='blue', alpha=0.3)
    
    # Plot orbit
    if len(positions) > 0:
        ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], color='red', linewidth=2)
    
    # Set labels and title
    ax.set_xlabel('X (Earth radii)')
    ax.set_ylabel('Y (Earth radii)')
    ax.set_zlabel('Z (Earth radii)')
    ax.set_title('Satellite Orbit Visualization')
    
    # Set equal aspect ratio
    ax.set_box_aspect([1, 1, 1])
    
    plt.tight_layout()
    plt.show()

def propagate_rk45_3d(time_span_hours=6, step_minutes=0.5):
    """
    Visualize RK45 integration 
    """
#    time_span_hours=6
#    step_minutes=0.5
#    time_offset_minutes=28.5
    
    # Parse TDM data
    tdms = sc.parse_tdm_w("data/Jason/20240318_16002A_A*", 130, 5)
    
    # Create RADec object from observations
    radec = sc.RADec(tdms.observations)
    
    # Extract initial state and epoch
    r_init = radec.get_position()
    v_init = radec.get_velocity()
    jd_init = radec.epoch
    
    # Create list of epochs
    epochs = []
    for dt in np.arange(0, time_span_hours * 60, step_minutes):
        jd = jd_init + dt * 60.0 / (24 * 60 * 60)
        epochs.append(jd)
    
    # Create and compute the propagator
    p = sc.propagate.Propagator(r_init, v_init, epochs, sc.propagate.rk45_eci, 1)
    p.compute()
    
    # Print results: epochs, positions, velocities
    for i in range(len(p.ephem.epochs)):
        print(p.ephem.epochs[i], p.ephem.positions[i].T, "|", p.ephem.velocities[i].T)

    # Rotate all positions to ECI
    positions_eci = []
    for pos, epoch in zip(p.ephem.positions, p.ephem.epochs):
        pos_eci = sc.frames.to_eci(pos, epoch)
        positions_eci.append(pos_eci)

    # Convert to numpy array and normalize to Earth radii
    positions_eci = np.array(positions_eci) / 6378.0
    
    positions = positions_eci
        
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    # Plot satellite path as a 3D line
    ax.plot(positions[:, 0], positions[:, 1], positions[:, 2], color='red', label='Trajectory')

    # Plot a sphere at the origin to mimic the Earth or a satellite
#    ax.scatter([0], [0], [0], color='blue', s=100, label='Earth Center')

    # Optionally draw a sphere to represent Earth (approximate)
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)
    ax.plot_surface(x, y, z, color='skyblue', alpha=0.3)

    # Set camera perspective
#    ax.view_init(elev=30, azim=45)  # adjust as needed

    # Labels and grid
    ax.set_xlabel('X (Earth radii)')
    ax.set_ylabel('Y (Earth radii)')
    ax.set_zlabel('Z (Earth radii)')
    ax.grid(True)
    ax.legend()

    plt.title("3D Satellite Orbit Visualization")
    plt.tight_layout()
    plt.show()
    
def draw_combined_orbits(tdm_wildcard="data/Jason/20240318_16002A_A*", delta=130, delta_error=5,
                         time_span_hours=6, step_minutes=0.5, time_offset_minutes=28.5):
    """
    Visualize and compare TLE propagation and RK45 integration
    
    Args:
        tdm_wildcard (str): Wildcard pattern for TDM files
        delta (float): Delta parameter for TDM parsing
        delta_error (float): Delta error parameter for TDM parsing
        time_span_hours (float): Time span for propagation in hours
        step_minutes (float): Time step in minutes
        time_offset_minutes (float): Time offset between TLE and observations in minutes
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from odette import satellite_core as sc
    
    # TLE for Jason-3 from 2024-03-19
    line1 = "1 41240U 16002A   24078.54273252 -.00000041  00000-0  87212-4 0  9991"
    line2 = "2 41240  66.0433  39.6041 0008216 275.2526  84.7552 12.80929447381890"
    
    # Create TLE object
    tle_obj = sc.TwoLineElement(line1, line2)
    time_jd = tle_obj.get_jd()
    
    # Parse TDM data
    tdms = sc.parse_tdm_w(tdm_wildcard, delta, delta_error)
    print(f"Number of observations: {len(tdms.observations)}")
    
    # Create RADec object
    radec = sc.RADec(tdms.observations)
    r_init = radec.get_position()
    v_init = radec.get_velocity()
    jd_init = radec.epoch
    
    # Initialize arrays
    epochs = []
    tle_positions = []
    
    # Propagate TLE
    for dt in np.arange(0, time_span_hours * 60, step_minutes):
        # Get position at current time
        r_ecef = tle_obj.get_position_at(float(dt + time_offset_minutes))
        
        # Convert to ECI
        jd = time_jd + dt * 60 / (24 * 60 * 60)
        r_eci = sc.frames.to_eci(r_ecef, jd)
        
        # Store normalized position and epoch
        tle_positions.append(r_eci / 6378.0)  # Normalize by Earth radius
        epochs.append(jd_init + dt * 60.0 / (24 * 60 * 60))
    
    # Create propagator for RK45
    p = sc.propagate.Propagator(r_init, v_init, epochs, sc.propagate.rk45_eci, 1)
    
    # Compute propagation
    p.compute()
    
    # Rotate all positions to ECI
    rk45_positions = []
    for pos, epoch in zip(p.ephem.positions, p.ephem.epochs):
        pos_eci = sc.frames.to_eci(pos, epoch)
        rk45_positions.append(pos_eci)
    
    # Extract RK45 positions and normalize
    tle_positions = np.array(tle_positions)
    rk45_positions = np.array(rk45_positions) / 6378.0
    
    # Setup 3D plot
    fig = plt.figure(figsize=(14, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot Earth
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)
    ax.plot_surface(x, y, z, color='blue', alpha=0.3)
    
    # Plot TLE orbit (red)
    ax.plot(tle_positions[:, 0], tle_positions[:, 1], tle_positions[:, 2], color='red', linewidth=2, label='TLE')
    
    # Plot RK45 orbit (green)
    ax.plot(rk45_positions[:, 0], rk45_positions[:, 1], rk45_positions[:, 2], color='green', linewidth=2, label='RK45')
    
    # Set labels and title
    ax.set_xlabel('X (Earth radii)')
    ax.set_ylabel('Y (Earth radii)')
    ax.set_zlabel('Z (Earth radii)')
    ax.set_title('TLE vs RK45 Orbit Comparison')
    
    # Set equal aspect ratio
    ax.set_box_aspect([1, 1, 1])
    
    # Add legend
    ax.legend()
    
    plt.tight_layout()
    plt.show()


def compare_orbital_elements(tdm_wildcard="data/Jason/20240318_16002A_A*", delta=100, delta_error=30,
                             time_span_hours=24, step_minutes=5, time_offset_minutes=28.5,
                             use_perturbations=True):
    """
    Compare orbital elements between TLE and RK45 propagation
    
    Args:
        tdm_wildcard (str): Wildcard pattern for TDM files
        delta (float): Delta parameter for TDM parsing
        delta_error (float): Delta error parameter for TDM parsing
        time_span_hours (float): Time span for propagation in hours
        step_minutes (float): Time step in minutes
        time_offset_minutes (float): Time offset between TLE and observations in minutes
        use_perturbations (bool): Whether to use perturbations in RK45 propagation
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from odette import satellite_core as sc
    
    # TLE for Jason-3
    line1 = "1 41240U 16002A   24078.93311235 -.00000041  00000-0  88455-4 0  9998"
    line2 = "2 41240  66.0433  38.7934 0008217 275.1931  84.8147 12.80929479381943"
    
    # Create TLE object
    tle_obj = sc.TwoLineElement(line1, line2)
    jd0 = tle_obj.get_jd()
    
    # Parse TDM data
    tdms = sc.parse_tdm_w(tdm_wildcard, delta, delta_error)
    print(f"Number of observations: {len(tdms.observations)}")
    
    # Create RADec object
    radec = sc.RADec(tdms.observations)
    r_init = radec.get_position()
    v_init = radec.get_velocity()
    jd_init = radec.epoch
    
    print(f"Time difference (minutes): {abs(jd_init - jd0) * 24 * 60 * 60 / 60.0}")
    
    # Initialize arrays
    epochs = []
    r_tle = []
    v_tle = []
    
    # Propagate TLE
    for dt in np.arange(0, time_span_hours * 60, step_minutes):
        # Get position and velocity at current time
        r_ecef = tle_obj.get_position_at(time_offset_minutes + dt)
        v_ecef = tle_obj.get_velocity_at(time_offset_minutes + dt)
        
        # Store for later processing
        r_tle.append(r_ecef)
        v_tle.append(v_ecef)
        
        # Store epoch
        epochs.append(jd_init + dt * 60.0 / (24 * 60 * 60))
    
    # Create propagator for RK45
    p = sc.propagate.Propagator(r_init, v_init, epochs, sc.propagate.rk45_eci, 1)
    
    # Set perturbation flags
    if use_perturbations:
        p.j2 = True      # J2 perturbation
        p.tb = True      # Third-body (Moon)
        p.solar = True   # Solar radiation pressure
        p.atm_exp = True # Atmospheric drag
    
    # Compute propagation
    p.compute()
    
    # Extract positions and velocities from propagator
    r_rk45_orig = p.ephem.positions
    v_rk45_orig = p.ephem.velocities
    
    # Convert positions and velocities to ECI frame
    r_tle_eci = []
    v_tle_eci = []
    r_rk45_eci = []
    v_rk45_eci = []
    
    for i, epoch in enumerate(epochs):
        # Convert TLE position/velocity to ECI
        r_tle_eci.append(sc.frames.to_eci(r_tle[i], epoch))
        v_tle_eci.append(sc.frames.to_eci(v_tle[i], epoch))
        
        # Convert RK45 position/velocity to ECI
        r_rk45_eci.append(sc.frames.to_eci(r_rk45_orig[i], epoch))
        v_rk45_eci.append(sc.frames.to_eci(v_rk45_orig[i], epoch))
    
    # Create output arrays for orbital elements
    tle_elements = []
    rk45_elements = []
    element_diffs = []
    position_diffs = []
    velocity_diffs = []
    
    # Calculate orbital elements and differences
    for i in range(len(epochs)):
        # Compute orbital elements in ECI frame
        oe_tle = sc.orbmath.compute_orbital_elements(r_tle_eci[i], v_tle_eci[i])
        oe_rk45 = sc.orbmath.compute_orbital_elements(r_rk45_eci[i], v_rk45_eci[i])
        
        # Store elements
        tle_elements.append([oe_tle.a, oe_tle.ecc, oe_tle.incl, oe_tle.Omega, oe_tle.omega, oe_tle.m])
        rk45_elements.append([oe_rk45.a, oe_rk45.ecc, oe_rk45.incl, oe_rk45.Omega, oe_rk45.omega, oe_rk45.m])
        
        # Calculate differences
        element_diff = [abs(oe_tle.a - oe_rk45.a),
                        abs(oe_tle.ecc - oe_rk45.ecc),
                        abs(oe_tle.incl - oe_rk45.incl),
                        abs(oe_tle.Omega - oe_rk45.Omega),
                        abs(oe_tle.omega - oe_rk45.omega),
                        abs(oe_tle.m - oe_rk45.m)]
        
        element_diffs.append(element_diff)
        
        # Calculate position and velocity differences
        r_tle_norm = np.linalg.norm(r_tle_eci[i])
        v_tle_norm = np.linalg.norm(v_tle_eci[i])
        r_rk45_norm = np.linalg.norm(r_rk45_eci[i])
        v_rk45_norm = np.linalg.norm(v_rk45_eci[i])
        
        position_diff = [abs(r_tle_eci[i][0] - r_rk45_eci[i][0]),
                         abs(r_tle_eci[i][1] - r_rk45_eci[i][1]),
                         abs(r_tle_eci[i][2] - r_rk45_eci[i][2]),
                         abs(r_tle_norm - r_rk45_norm)]
        
        velocity_diff = [abs(v_tle_eci[i][0] - v_rk45_eci[i][0]),
                         abs(v_tle_eci[i][1] - v_rk45_eci[i][1]),
                         abs(v_tle_eci[i][2] - v_rk45_eci[i][2]),
                         abs(v_tle_norm - v_rk45_norm)]
        
        position_diffs.append(position_diff)
        velocity_diffs.append(velocity_diff)
    
    # Convert to numpy arrays for easier plotting
    tle_elements = np.array(tle_elements)
    rk45_elements = np.array(rk45_elements)
    element_diffs = np.array(element_diffs)
    position_diffs = np.array(position_diffs)
    velocity_diffs = np.array(velocity_diffs)
    
    # Time array for plotting (hours from start)
    plot_times = np.arange(len(tle_elements)) * step_minutes / 60.0
    
    # Plot orbital element differences
    fig, axs = plt.subplots(3, 2, figsize=(16, 12))
    element_names = ['Semi-major axis (a)', 'Eccentricity (e)', 'Inclination (i)',
                     'RAAN (Ω)', 'Argument of Perigee (ω)', 'Mean Anomaly (M)']
    
    for i, (name, ax) in enumerate(zip(element_names, axs.flat)):
        ax.plot(plot_times, tle_elements[:, i], 'r-', label='TLE')
        ax.plot(plot_times, rk45_elements[:, i], 'g-', label='RK45')
        ax.set_title(name)
        ax.set_xlabel('Time (hours)')
        ax.grid(True)
        ax.legend()
    
    plt.tight_layout()
    plt.show()
    
    # Plot element differences
    fig, axs = plt.subplots(3, 2, figsize=(16, 12))
    for i, (name, ax) in enumerate(zip(element_names, axs.flat)):
        ax.plot(plot_times, element_diffs[:, i], 'b-')
        ax.set_title(f'{name} Difference')
        ax.set_xlabel('Time (hours)')
        ax.set_ylabel('Absolute Difference')
        ax.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # Plot position differences
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    pos_diff_names = ['X Position', 'Y Position', 'Z Position', 'Radius']
    
    for i, (name, ax) in enumerate(zip(pos_diff_names, axs.flat)):
        ax.plot(plot_times, position_diffs[:, i], 'b-')
        ax.set_title(f'{name} Difference')
        ax.set_xlabel('Time (hours)')
        ax.set_ylabel('Difference (m)')
        ax.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # Return statistics
    return {
        'mean_position_diff': np.mean(position_diffs[:, 3]),
        'max_position_diff': np.max(position_diffs[:, 3]),
        'mean_semi_major_diff': np.mean(element_diffs[:, 0]),
        'mean_ecc_diff': np.mean(element_diffs[:, 1]),
        'mean_inc_diff': np.mean(element_diffs[:, 2])
    }


def test_orbital_element_err():
    """
    Tests orbital element errors between TLE and RK45 propagation
    Saves results to CSV files for further analysis
    """
    import os
    import numpy as np
    from odette import satellite_core as sc
    
    # Create output directory if it doesn't exist
    os.makedirs("log_orbital_elem", exist_ok=True)
    
    # TLE lines for Jason-3
    line1 = "1 41240U 16002A   24078.93311235 -.00000041  00000-0  88455-4 0  9998"
    line2 = "2 41240  66.0433  38.7934 0008217 275.1931  84.8147 12.80929479381943"
    
    for combi in range(16):
        print(f"Test combination {combi}/16 using TwoLineElement class...")
        
        # Create TLE object
        tle_obj = sc.TwoLineElement(line1, line2)
        jd0 = tle_obj.get_jd()
        
        # Parse TDM files
        tdms = sc.parse_tdm_w("data/Jason/20240318_16002A_A*", 100, 30)
        print(f"Number of observations: {len(tdms.observations)}")
        
        # Create RADec object from observations
        radec = sc.RADec(tdms.observations)
        
        # Initialize state vector with r, v from Gauss method
        r_init = radec.get_position()
        v_init = radec.get_velocity()
        jd_init = radec.epoch
        print(f"Time difference: {abs(jd_init - jd0) * sc.orbmath.SECONDS_PER_DAY / 60.0} minutes")
        
        # Time of integration variables
        epochs = []  # time of integration of RK45
        offmins = 28.5
        
        # Storage for positions and velocities
        r_tle = []
        v_tle = []
        
        # Propagate TLE with SGP4 for 10 orbits of Jason3
        for dt in np.arange(0, 112.5 * 10 + 0.1, 0.5):
            # Get position and velocity from TLE
            r_ecef = tle_obj.get_position_at(offmins + dt)
            v_ecef = tle_obj.get_velocity_at(offmins + dt)
            
            # Store position and velocity
            r_tle.append(r_ecef)
            v_tle.append(v_ecef)
            
            # Store epoch
            epochs.append(jd_init + dt * 60.0 / sc.orbmath.SECONDS_PER_DAY)
        
        # Create propagator - calculations are done in ECI frame
        propagator = sc.propagate.Propagator(r_init, v_init, epochs, sc.propagate.rk45_eci, 1)
        
        # Set perturbation flags based on binary combination
        propagator.j2 = bool(combi & 0b0001)
        propagator.tb = bool(combi & 0b0010)
        propagator.solar = bool(combi & 0b0100)
        propagator.atm_exp = bool(combi & 0b1000)
        
        # Log active perturbations
        perturb_str = []
        if propagator.j2: perturb_str.append("J2")
        if propagator.tb: perturb_str.append("ThirdBody")
        if propagator.solar: perturb_str.append("SolarRadiation")
        if propagator.atm_exp: perturb_str.append("AtmDrag")
        
        print(f"Active perturbations: {', '.join(perturb_str) if perturb_str else 'None'}")
        
        # Compute propagation
        propagator.compute()
        
        # Extract positions and velocities
        r_rk45_orig = propagator.ephem.positions
        v_rk45_orig = propagator.ephem.velocities
        
        # Convert positions and velocities to ECI frame
        r_tle_eci = []
        v_tle_eci = []
        r_rk45_eci = []
        v_rk45_eci = []
        
        for i, epoch in enumerate(epochs):
            # Convert TLE position/velocity to ECI
            r_tle_eci.append(sc.frames.to_eci(r_tle[i], epoch))
            v_tle_eci.append(sc.frames.to_eci(v_tle[i], epoch))
            
            # Convert RK45 position/velocity to ECI
            r_rk45_eci.append(sc.frames.to_eci(r_rk45_orig[i], epoch))
            v_rk45_eci.append(sc.frames.to_eci(v_rk45_orig[i], epoch))
        
        # Create output files
        oe_csv_name = f"log_orbital_elem/_oe_err_{combi}.csv"
        oe_log_name = f"log_orbital_elem/_oe_err_{combi}.log"
        
        with open(oe_csv_name, "w") as oe_csv, open(oe_log_name, "w") as oe_log:
            # Write CSV header
            oe_csv.write("Epoch,tle_a,tle_e,tle_i,tle_O,tle_omega,tle_m," +
                         "rk45_a,rk45_e,rk45_i,rk45_O,rk45_omega,rk45_m," +
                         "a_err,e_err,i_err,O_err,omega_err,m_err," +
                         "x_tle,y_tle,z_tle,vx_tle,vy_tle,vz_tle,alt_tle,speed_tle," +
                         "x_rk45,y_rk45,z_rk45,vx_rk45,vy_rk45,vz_rk45,alt_rk45,speed_rk45," +
                         "x_err,y_err,z_err,alt_err,speed_err\n")
            
            # Write perturbation info to log
            oe_log.write(f"Perturbation configuration {combi}: {', '.join(perturb_str) if perturb_str else 'None'}\n")
            oe_log.write(f"TLE: {line1}\n{line2}\n")
            oe_log.write(f"Initial state: r={r_init}, v={v_init}, jd={jd_init}\n\n")
            
            # Process each epoch
            for i in range(len(epochs)):
                # Log state vectors for debugging
                oe_log.write(f"Epoch {i}, t={epochs[i]}:\n")
                oe_log.write(f"  TLE_ECI: r={r_tle_eci[i]}, v={v_tle_eci[i]}\n")
                oe_log.write(f"  RK45_ECI: r={r_rk45_eci[i]}, v={v_rk45_eci[i]}\n")
                
                # Compute orbital elements in ECI frame
                oe_tle = sc.orbmath.compute_orbital_elements(r_tle_eci[i], v_tle_eci[i])
                oe_rk45 = sc.orbmath.compute_orbital_elements(r_rk45_eci[i], v_rk45_eci[i])
                
                # Calculate norms and differences
                r_tle_norm = np.linalg.norm(r_tle_eci[i])
                v_tle_norm = np.linalg.norm(v_tle_eci[i])
                r_rk45_norm = np.linalg.norm(r_rk45_eci[i])
                v_rk45_norm = np.linalg.norm(v_rk45_eci[i])
                
                # Write data to CSV
                oe_csv.write(f"{epochs[i]:.14e},"
                            f"{oe_tle.a:.14e},{oe_tle.ecc:.14e},{oe_tle.incl:.14e},"
                            f"{oe_tle.Omega:.14e},{oe_tle.omega:.14e},{oe_tle.m:.14e},"
                            f"{oe_rk45.a:.14e},{oe_rk45.ecc:.14e},{oe_rk45.incl:.14e},"
                            f"{oe_rk45.Omega:.14e},{oe_rk45.omega:.14e},{oe_rk45.m:.14e},"
                            f"{abs(oe_tle.a - oe_rk45.a):.14e},{abs(oe_tle.ecc - oe_rk45.ecc):.14e},"
                            f"{abs(oe_tle.incl - oe_rk45.incl):.14e},{abs(oe_tle.Omega - oe_rk45.Omega):.14e},"
                            f"{abs(oe_tle.omega - oe_rk45.omega):.14e},{abs(oe_tle.m - oe_rk45.m):.14e},"
                            f"{r_tle_eci[i][0]:.14e},{r_tle_eci[i][1]:.14e},{r_tle_eci[i][2]:.14e},"
                            f"{v_tle_eci[i][0]:.14e},{v_tle_eci[i][1]:.14e},{v_tle_eci[i][2]:.14e},"
                            f"{r_tle_norm-6378.0:.14e},{v_tle_norm:.14e},"
                            f"{r_rk45_eci[i][0]:.14e},{r_rk45_eci[i][1]:.14e},{r_rk45_eci[i][2]:.14e},"
                            f"{v_rk45_eci[i][0]:.14e},{v_rk45_eci[i][1]:.14e},{v_rk45_eci[i][2]:.14e},"
                            f"{r_rk45_norm-6378.0:.14e},{v_rk45_norm:.14e},"
                            f"{abs(r_tle_eci[i][0] - r_rk45_eci[i][0]):.14e},{abs(r_tle_eci[i][1] - r_rk45_eci[i][1]):.14e},"
                            f"{abs(r_tle_eci[i][2] - r_rk45_eci[i][2]):.14e},"
                            f"{abs(r_tle_norm - r_rk45_norm):.14e},{abs(v_tle_norm - v_rk45_norm):.14e}\n")
            
            # Calculate and write summary statistics
            oe_log.write("\nSummary Statistics:\n")
            pos_diffs = [np.linalg.norm(np.array(r_tle_eci[i]) - np.array(r_rk45_eci[i])) for i in range(len(epochs))]
            vel_diffs = [np.linalg.norm(np.array(v_tle_eci[i]) - np.array(v_rk45_eci[i])) for i in range(len(epochs))]
            
            oe_log.write(f"Mean position difference: {np.mean(pos_diffs):.3f} m\n")
            oe_log.write(f"Max position difference: {np.max(pos_diffs):.3f} m\n")
            oe_log.write(f"Mean velocity difference: {np.mean(vel_diffs):.3f} m/s\n")
            oe_log.write(f"Max velocity difference: {np.max(vel_diffs):.3f} m/s\n")


if __name__ == "__main__":
    # Run the tests
#    gauss_tle_altitude_test()
    
    # Visualize orbit from TLE
#    print("Visualizing orbit from TLE...")
#    propagate_tle_3d()
    
    # Test RK45 integration
    print("\nTesting RK45 integration...")
    propagate_rk45_3d()
    
     # Compare TLE and RK45 orbits
#    print("\nComparing TLE and RK45 orbits...")
#    draw_combined_orbits()
    
    # Compare orbital elements
#    print("\nComparing orbital elements...")
#    stats = compare_orbital_elements()
#    print("Statistics:", stats)

#    test_orbital_element_err()
