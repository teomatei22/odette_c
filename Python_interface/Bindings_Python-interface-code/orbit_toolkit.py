#!/usr/bin/env python3.8
"""
@file orbit_toolkit.py
@brief Orbit Toolkit - Python interface for orbit visualization and propagation

This module provides an easy-to-use interface to the odette satellite
core library, with a focus on orbit visualization and propagation with
different perturbation models.

"""

import os
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json
from datetime import datetime, timedelta
from odette import satellite_core as sc


class OrbitVisualizer:
    """
    @brief Class for visualizing satellite orbits in 3D
    @memberof OrbitVisualizer
    
    The OrbitVisualizer class provides comprehensive 3D visualization capabilities
    for satellite orbits using various propagation methods including TLE-based
    SGP4/SDP4 propagation and high-precision RK45 numerical integration.
    
    Features:
    - TLE orbit visualization with SGP4/SDP4 propagation
    - RK45 numerical integration with perturbation models
    - Comparative orbit analysis
    - Multi-satellite visualization
    - Customizable plotting options
    
    @note This class provides ONLY visualization capabilities.
    For orbit propagation and analysis, see OrbitPropagator.
    
    @example
    @code{.py}
    # Create visualizer
    visualizer = OrbitVisualizer()
    
    # Visualize TLE orbit
    tle_line1 = "1 25544U 98067A   08264.51782528 -.00002182..."
    tle_line2 = "2 25544  51.6416 247.4627 0006703 130.5360..."
    
    fig, ax, positions = visualizer.visualize_tle(
        tle_line1, tle_line2,
        time_span_hours=6,
        show_plot=True
    )
    @endcode
    """
    
    def __init__(self):
        """
        @brief Initialize the orbit visualizer
        @memberof OrbitVisualizer
        
        Sets up the visualization environment with default Earth parameters
        and initializes plot objects.
        """
        self.fig = None  ///< Matplotlib figure object
        self.ax = None   ///< Matplotlib 3D axes object
        self.earth_radius = 6378.0  ///< Earth radius in kilometers
        
    def _setup_plot(self, title="Satellite Orbit Visualization"):
        """
        @brief Set up the 3D plot with Earth visualization
        @memberof OrbitVisualizer
        
        Creates a 3D matplotlib plot with a spherical Earth representation
        and proper axis labeling.
        
        @param title Plot title string
        """
        self.fig = plt.figure(figsize=(12, 10))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Plot Earth
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x = np.cos(u) * np.sin(v)
        y = np.sin(u) * np.sin(v)
        z = np.cos(v)
        self.ax.plot_surface(x, y, z, color='blue', alpha=0.3)
        
        # Set labels and title
        self.ax.set_xlabel('X (Earth radii)')
        self.ax.set_ylabel('Y (Earth radii)')
        self.ax.set_zlabel('Z (Earth radii)')
        self.ax.set_title(title)
        
        # Set equal aspect ratio
        self.ax.set_box_aspect([1, 1, 1])
    
    def _plot_orbit(self, positions, color='red', label=None, line_width=2):
        """
        @brief Plot an orbit path on the 3D axes
        @memberof OrbitVisualizer
        
        @param positions Array of position vectors (N x 3)
        @param color Line color for the orbit
        @param label Legend label for the orbit
        @param line_width Width of the orbit line
        """
        positions = np.array(positions)
        self.ax.plot(positions[:, 0], positions[:, 1], positions[:, 2],
                    color=color, linewidth=line_width, label=label)
                    
    def _plot_x_vs_time(self, rk_positions_list, labels, step_minutes=0.5, title="X vs Time for RK45 Orbits"):
        """
        @brief Plot X-coordinate vs time for multiple trajectories
        @memberof OrbitVisualizer
        
        Creates a 2D plot showing the evolution of the X-coordinate over time
        for multiple orbit propagations, useful for analyzing orbital divergence.
        
        @param rk_positions_list List of position arrays for different trajectories
        @param labels List of labels for each trajectory
        @param step_minutes Time step between points in minutes
        @param title Plot title
        """
        # Create a new figure and axes (2D this time, not 3D)
        self.fig = plt.figure(figsize=(12, 6))
        self.ax = self.fig.add_subplot(111)  # 2D plot

        # Time array
        time_minutes = np.arange(len(rk_positions_list[0])) * step_minutes

        # Plot X vs time for each trajectory
        for rk_positions, label in zip(rk_positions_list, labels):
            self.ax.plot(time_minutes, rk_positions[:, 0], label=label)

        # Set labels and title
        self.ax.set_xlabel('Time (minutes)')
        self.ax.set_ylabel('X Position (Earth radii)')
        self.ax.set_title(title)
        self.ax.grid(True)
        self.ax.legend()
        self.fig.tight_layout()
        plt.show()
        
    def visualize_tle(self, tle_line1, tle_line2, time_span_hours=12, step_minutes=0.5,
                     show_plot=True, save_path=None):
        """
        @brief Visualize a satellite orbit using TLE data
        @memberof OrbitVisualizer
        
        Propagates and visualizes a satellite orbit using Two-Line Element (TLE) data
        with the SGP4/SDP4 analytical propagation model.
        
        @param tle_line1 First line of the TLE
        @param tle_line2 Second line of the TLE  
        @param time_span_hours Time span to propagate in hours
        @param step_minutes Time step between points in minutes
        @param show_plot Whether to display the plot
        @param save_path File path to save the plot (optional)
        
        @return Tuple containing (figure, axes, positions array)
        @retval tuple (fig, ax, positions) or (None, None, None) on error
        
        @note The positions are returned normalized by Earth radius for visualization
        
        @example
        @code{.py}
        visualizer = OrbitVisualizer()
        line1 = "1 25544U 98067A   08264.51782528 -.00002182..."
        line2 = "2 25544  51.6416 247.4627 0006703 130.5360..."
        
        fig, ax, pos = visualizer.visualize_tle(line1, line2, 
                                               time_span_hours=6,
                                               save_path="orbit.png")
        @endcode
        """
        self._setup_plot("TLE Orbit Visualization")
        
        try:
            # Create TLE object
            tle_obj = sc.TwoLineElement(tle_line1, tle_line2)
            time_jd = tle_obj.get_jd()
            
            # Initialize positions array
            positions = []
            
            # Propagate orbit
            for dt in np.arange(0, time_span_hours * 60, step_minutes):
                r_ecef = tle_obj.get_position_at(float(dt))
                
                # Convert to ECI
                r_eci = sc.frames.to_eci(r_ecef, time_jd + dt * 60 / (24 * 60 * 60))
                positions.append(r_eci / self.earth_radius)  # Normalize by Earth radius
                
            # Plot orbit
            self._plot_orbit(positions, label='TLE Orbit')
            
            # Add legend
            if self.ax.get_legend_handles_labels()[0]:
                self.ax.legend()
                
            # Save plot if requested
            if save_path:
                plt.tight_layout()
                plt.savefig(save_path)
                
            # Show plot if requested
            if show_plot:
                plt.tight_layout()
                plt.show()
                
            return self.fig, self.ax, positions
            
        except Exception as e:
            print(f"Error in TLE visualization: {e}")
            return None, None, None
        
    def visualize_rk45(self, tdm_wildcard, delta, delta_error, time_span_hours=6, step_minutes=0.5, perturbations=None, show_plot=True, save_path=None):
        """
        @brief Visualize a satellite orbit using RK45 integration
        @memberof OrbitVisualizer
        
        Performs high-precision numerical orbit propagation using the Runge-Kutta 4th/5th order
        (RK45) integration method with configurable perturbation models.
        
        @param tdm_wildcard Wildcard pattern for TDM (Tracking Data Message) files
        @param delta Delta parameter for TDM parsing tolerance
        @param delta_error Delta error parameter for TDM parsing
        @param time_span_hours Time span to propagate in hours
        @param step_minutes Time step between output points in minutes
        @param perturbations Dictionary of perturbation flags:
                             - 'j2': bool - J2 Earth oblateness perturbation
                             - 'third_body': bool - Third-body (Moon/Sun) perturbations
                             - 'solar_radiation': bool - Solar radiation pressure
                             - 'atmospheric_drag': bool - Atmospheric drag effects
        @param show_plot Whether to display the plot
        @param save_path File path to save the plot (optional)
        
        @return Tuple containing (figure, axes, positions array)
        @retval tuple (fig, ax, positions) or (None, None, None) on error
        
        @note Requires TDM files for initial orbit determination
        
        @example
        @code{.py}
        perturbations = {
            'j2': True,
            'third_body': True,
            'solar_radiation': False,
            'atmospheric_drag': False
        }
        
        fig, ax, pos = visualizer.visualize_rk45(
            "data/tracking/*.tdm",
            delta=100, delta_error=30,
            perturbations=perturbations
        )
        @endcode
        """
        self._setup_plot("RK45 Orbit Propagation")
        
        # Parse TDM data
        tdms = sc.parse_tdm_w(tdm_wildcard, delta, delta_error)
        print(f"Number of observations: {len(tdms.observations)}")
        
        # Create RADec object
        radec = sc.RADec(tdms.observations)
        r_init = radec.get_position()
        v_init = radec.get_velocity()
        jd_init = radec.epoch
        
        # Set default perturbations if not provided
        if perturbations is None:
            perturbations = {
                'j2': False,
                'third_body': False,
                'solar_radiation': False,
                'atmospheric_drag': False
            }
            
        # Create list of epochs
        epochs = []
        for dt in np.arange(0, time_span_hours * 60, step_minutes):
            jd = jd_init + dt * 60.0 / (24 * 60 * 60)
            epochs.append(jd)
            
        # Create and configure the propagator
        p = sc.propagate.Propagator(r_init, v_init, epochs, sc.propagate.rk45_eci, 1)
        
        # Set perturbation flags
        p.j2 = perturbations.get('j2', False)
        p.tb = perturbations.get('third_body', False)
        p.solar = perturbations.get('solar_radiation', False)
        p.atm_exp = perturbations.get('atmospheric_drag', False)
        
        # Compute propagation
        p.compute()
        
        # Rotate all positions to ECI
        positions_eci = []
        for pos, epoch in zip(p.ephem.positions, p.ephem.epochs):
            pos_eci = sc.frames.to_eci(pos, epoch)
            positions_eci.append(pos_eci)

        # Convert to numpy array and normalize to Earth radii
        positions = np.array(positions_eci) / self.earth_radius
        
        # Plot orbit
        self._plot_orbit(positions, label='RK45 Orbit')
            
        # Add legend
        if self.ax.get_legend_handles_labels()[0]:
            self.ax.legend()
                
        # Save plot if requested
        if save_path:
            plt.tight_layout()
            plt.savefig(save_path)
                
        # Show plot if requested
        if show_plot:
            plt.tight_layout()
            plt.show()
            
        return self.fig, self.ax, positions
        
    def compare_orbits(self, tle_line1, tle_line2, tdm_wildcard, delta, delta_error,
                       time_span_hours=6, step_minutes=0.5, time_offset_minutes=0,
                       perturbations_list=None, show_plot=True, save_path=None):
        """
        @brief Compare TLE and RK45 orbit propagation methods
        @memberof OrbitVisualizer
        
        Performs a side-by-side comparison of TLE-based SGP4/SDP4 propagation
        and high-precision RK45 numerical integration with multiple perturbation
        configurations.
        
        @param tle_line1 First line of TLE data
        @param tle_line2 Second line of TLE data
        @param tdm_wildcard Wildcard pattern for TDM files
        @param delta Delta parameter for TDM parsing
        @param delta_error Delta error parameter for TDM parsing
        @param time_span_hours Time span for comparison in hours
        @param step_minutes Time step between points in minutes
        @param time_offset_minutes Time offset between TLE epoch and observations
        @param perturbations_list List of perturbation dictionaries for multiple RK45 runs
        @param show_plot Whether to display the comparison plot
        @param save_path File path to save the plot (optional)
        
        @return Tuple containing (figure, axes, tle_positions, rk45_positions)
        @retval tuple (fig, ax, tle_pos, rk_pos) or (None, None, None, None) on error
        
        @note This method is particularly useful for validating propagation accuracy
              and understanding the impact of different perturbation models
        
        @example
        @code{.py}
        perturbations_list = [
            {'j2': True, 'third_body': False},
            {'j2': True, 'third_body': True, 'solar_radiation': True}
        ]
        
        fig, ax, tle_pos, rk_pos = visualizer.compare_orbits(
            line1, line2, "data/*.tdm", 100, 30,
            perturbations_list=perturbations_list
        )
        @endcode
        """
        self._setup_plot("TLE vs RK45 Orbit Comparison")

        # -----------------------
        # Propagate TLE
        # -----------------------
        try:
            # Create TLE object
            tle_obj = sc.TwoLineElement(tle_line1, tle_line2)
            time_jd = tle_obj.get_jd()
            
            # Initialize positions and epochs array
            tle_positions = []
            epochs = []
            
            # Parse TDM data
            tdms = sc.parse_tdm_w(tdm_wildcard, delta, delta_error)
            print(f"Number of observations: {len(tdms.observations)}")
            
            # Create RADec object
            radec = sc.RADec(tdms.observations)
            r_init = radec.get_position()
            v_init = radec.get_velocity()
            jd_init = radec.epoch
            
            # Propagate orbit
            for dt in np.arange(0, time_span_hours * 60, step_minutes):
                r_ecef = tle_obj.get_position_at(float(dt))
                
                # Convert to ECI
                r_eci = sc.frames.to_eci(r_ecef, time_jd + dt * 60 / (24 * 60 * 60))
                tle_positions.append(r_eci / self.earth_radius)  # Normalize by Earth radius
                epochs.append(jd_init + dt * 60.0 / (24 * 60 * 60))

        except Exception as e:
            print(f"Error in TLE propagation: {e}")
            return None, None, None, None

        # -----------------------
        # Propagate RK45
        # -----------------------
        
        if perturbations_list is None:
            perturbations_list = [{
                'j2': True,
                'third_body': False,
                'solar_radiation': False,
                'atmospheric_drag': False
            }]
        
        rk_positions_all = []

        for idx, perturbations in enumerate(perturbations_list):
            p = sc.propagate.Propagator(r_init, v_init, epochs, sc.propagate.rk45_eci, 1)
            p.j2 = perturbations.get('j2', True)
            p.tb = perturbations.get('third_body', False)
            p.solar = perturbations.get('solar_radiation', False)
            p.atm_exp = perturbations.get('atmospheric_drag', False)

            p.compute()

            rk_positions = []
            for pos, epoch in zip(p.ephem.positions, p.ephem.epochs):
                pos_eci = sc.frames.to_eci(pos, epoch)
                rk_positions.append(pos_eci)

            rk_positions = np.array(rk_positions) / self.earth_radius
            rk_positions_all.append(rk_positions)

            # Create label based on perturbation settings
            label = f"RK45 [j2={p.j2}, tb={p.tb}, srp={p.solar}, drag={p.atm_exp}]"
            color = plt.cm.viridis(idx / len(perturbations_list))  # for visually distinct colors
            self._plot_orbit(rk_positions, color=color, label=label)
        
        tle_positions = np.array(tle_positions)
        self._plot_orbit(tle_positions, color='red', label='TLE Propagation')

        # -----------------------
        # Finalize and Return
        # -----------------------
        if self.ax.get_legend_handles_labels()[0]:
            self.ax.legend()

        if save_path:
            plt.tight_layout()
            plt.savefig(save_path)

        if show_plot:
            plt.tight_layout()
            plt.show()

        return self.fig, self.ax, tle_positions, rk_positions
            
    def visualize_multiple_satellites(self, satellites_data, time_span_hours=6, step_minutes=0.5,
                             show_plot=True, save_path=None, title="Multiple Satellite Visualization"):
        """
        @brief Visualize multiple satellites on the same plot
        @memberof OrbitVisualizer
        
        Creates a unified visualization showing the orbits of multiple satellites,
        each potentially using different propagation methods and parameters.
        
        @param satellites_data List of satellite configuration dictionaries. Each dictionary
                              should contain one of these forms:
                              - TLE satellite: {'type': 'tle', 'tle_line1': str, 'tle_line2': str, 
                                               'color': str, 'label': str}
                              - RK45 satellite: {'type': 'rk45', 'tdm_wildcard': str, 'delta': float, 
                                                'delta_error': float, 'perturbations': dict, 
                                                'color': str, 'label': str}
                              - Custom satellite: {'type': 'custom', 'positions': list, 
                                                  'color': str, 'label': str}
        @param time_span_hours Time span to propagate in hours
        @param step_minutes Time step between points in minutes
        @param show_plot Whether to display the plot
        @param save_path File path to save the plot (optional)
        @param title Title for the plot
        
        @return Tuple containing (figure, axes)
        @retval tuple (fig, ax) for the generated plot
        
        @example
        @code{.py}
        satellites = [
            {
                'type': 'tle',
                'tle_line1': line1_iss,
                'tle_line2': line2_iss,
                'color': 'red',
                'label': 'ISS'
            },
            {
                'type': 'rk45',
                'tdm_wildcard': 'satellite_b/*.tdm',
                'delta': 100,
                'delta_error': 30,
                'perturbations': {'j2': True},
                'color': 'blue',
                'label': 'Satellite B'
            }
        ]
        
        fig, ax = visualizer.visualize_multiple_satellites(satellites)
        @endcode
        """
        # Setup the plot
        self._setup_plot(title)
        
        # Process each satellite
        for idx, sat_data in enumerate(satellites_data):
            # Set default color if not provided
            if 'color' not in sat_data:
                sat_data['color'] = plt.cm.viridis(idx / len(satellites_data))
                
            # Set default label if not provided
            if 'label' not in sat_data:
                sat_data['label'] = f"Satellite {idx+1}"
                
            # Process based on satellite type
            if sat_data['type'] == 'tle':
                # TLE satellite
                try:
                    _, _, positions = self.visualize_tle(
                        sat_data['tle_line1'],
                        sat_data['tle_line2'],
                        time_span_hours=time_span_hours,
                        step_minutes=step_minutes,
                        show_plot=False
                    )
                    
                    self._plot_orbit(positions, color=sat_data['color'], label=sat_data['label'])
                except Exception as e:
                    print(f"Error processing TLE satellite {idx}: {e}")
                    
            elif sat_data['type'] == 'rk45':
                # RK45 satellite
                try:
                    # Set default perturbations if not provided
                    if 'perturbations' not in sat_data:
                        sat_data['perturbations'] = {
                            'j2': True,
                            'third_body': False,
                            'solar_radiation': False,
                            'atmospheric_drag': False
                        }
                        
                    _, _, positions = self.visualize_rk45(
                        sat_data['tdm_wildcard'],
                        sat_data.get('delta', 100),
                        sat_data.get('delta_error', 30),
                        time_span_hours=time_span_hours,
                        step_minutes=step_minutes,
                        perturbations=sat_data['perturbations'],
                        show_plot=False
                    )
                    
                    self._plot_orbit(positions, color=sat_data['color'], label=sat_data['label'])
                except Exception as e:
                    print(f"Error processing RK45 satellite {idx}: {e}")
                    
            elif sat_data['type'] == 'custom':
                # Custom satellite with pre-computed positions
                try:
                    self._plot_orbit(sat_data['positions'], color=sat_data['color'], label=sat_data['label'])
                except Exception as e:
                    print(f"Error processing custom satellite {idx}: {e}")
        
        # Add legend if we have any labels
        if self.ax.get_legend_handles_labels()[0]:
            self.ax.legend()
            
        # Save plot if requested
        if save_path:
            plt.tight_layout()
            plt.savefig(save_path)
            
        # Show plot if requested
        if show_plot:
            plt.tight_layout()
            plt.show()
            
        return self.fig, self.ax


class OrbitPropagator(OrbitVisualizer):
    """
    @brief Class for propagating satellite orbits with analysis capabilities
    @memberof OrbitPropagator
    
    The OrbitPropagator class extends OrbitVisualizer to provide advanced orbit
    propagation capabilities with detailed analysis of orbital elements evolution,
    statistical comparisons between different propagation methods, and
    comprehensive perturbation modeling.
    
    Key Features:
    - High-precision RK45 numerical integration
    - TLE-based SGP4/SDP4 analytical propagation  
    - Orbital elements evolution tracking
    - Statistical comparison between propagation methods
    - Configurable perturbation parameters
    - Export capabilities for analysis results
    
    @note This class adds propagation methods to the visualization base class
    @see OrbitVisualizer for inherited visualization methods
    
    @example
    @code{.py}
    propagator = OrbitPropagator()
    
    # Propagate TLE orbit
    results = propagator.propagate_tle(line1, line2, time_span_hours=24)
    
    # Compare with RK45
    stats = propagator.compare_orbital_elements(
        tle_line1=line1, tle_line2=line2,
        tdm_wildcard="data/*.tdm",
        perturbations_list=[{'j2': True}, {'j2': True, 'third_body': True}]
    )
    @endcode
    """
    
    def __init__(self):
        """
        @brief Initialize the orbit propagator
        @memberof OrbitPropagator
        
        Inherits from OrbitVisualizer and sets up additional propagation-specific
        parameters and constants.
        """
        # Call the parent class constructor
        super().__init__()
        self.earth_radius = 6378.0  ///< Earth radius in kilometers
                
    def propagate_tle(self, tle_line1, tle_line2, time_span_hours=6, step_minutes=0.5,
                         return_vectors=True):
        """
        @brief Propagate orbit using TLE data with detailed analysis
        @memberof OrbitPropagator
        
        Performs TLE-based orbit propagation using SGP4/SDP4 models and returns
        comprehensive orbital state information including position/velocity vectors
        and classical orbital elements evolution.
        
        @param tle_line1 First line of TLE data
        @param tle_line2 Second line of TLE data  
        @param time_span_hours Time span for propagation in hours
        @param step_minutes Time step between output points in minutes
        @param return_vectors Whether to include position and velocity vectors in output
        
        @return Dictionary containing propagation results with keys:
                - 'epochs': List of Julian dates
                - 'orbital_elements': List of orbital element dictionaries
                - 'positions': List of position vectors (if return_vectors=True)
                - 'velocities': List of velocity vectors (if return_vectors=True)
        @retval dict Propagation results or None on error
        
        @note Orbital elements include: a (semi-major axis), e (eccentricity), 
              i (inclination), raan (RAAN), argp (argument of perigee), 
              nu (true anomaly), M (mean anomaly)
        
        @example
        @code{.py}
        results = propagator.propagate_tle(line1, line2, time_span_hours=12)
        
        # Access orbital elements
        initial_sma = results['orbital_elements'][0]['a']
        final_sma = results['orbital_elements'][-1]['a']
        
        print(f"Semi-major axis change: {final_sma - initial_sma:.3f} km")
        @endcode
        """
        try:
            # Create TLE object
            tle_obj = sc.TwoLineElement(tle_line1, tle_line2)
            time_jd = tle_obj.get_jd()
            
            # Initialize arrays
            epochs = []
            positions = []
            velocities = []
            orbital_elements = []
            
            # Propagate orbit
            for dt in np.arange(0, time_span_hours * 60, step_minutes):
                # Current epoch
                current_epoch = time_jd + dt * 60 / (24 * 60 * 60)
                epochs.append(current_epoch)
                
                # Get position and velocity in ECEF
                r_ecef = tle_obj.get_position_at(float(dt))
                v_ecef = tle_obj.get_velocity_at(float(dt))
                
                # Convert to ECI, matching the visualization function approach
                r_eci = sc.frames.to_eci(r_ecef, current_epoch)
                v_eci = sc.frames.to_eci(v_ecef, current_epoch)
                
                # Store position and velocity if requested
                if return_vectors:
                    positions.append(r_eci)
                    velocities.append(v_eci)
                
                # Calculate orbital elements using ECI vectors
                oe = sc.orbmath.compute_orbital_elements(r_eci, v_eci)
                
                # Store orbital elements
                orbital_elements.append({
                    'a': oe.a,          # Semi-major axis (km)
                    'e': oe.ecc,        # Eccentricity
                    'i': oe.incl,       # Inclination (rad)
                    'raan': oe.Omega,   # Right Ascension of Ascending Node (rad)
                    'argp': oe.omega,   # Argument of Perigee (rad)
                    'nu': oe.nu,        # True Anomaly (rad)
                    'M': oe.m           # Mean Anomaly (rad)
                })
            
            # Prepare results
            results = {
                'epochs': epochs,
                'orbital_elements': orbital_elements
            }
            
            # Add position and velocity vectors if requested
            if return_vectors:
                results['positions'] = positions
                results['velocities'] = velocities
                
            return results
            
        except Exception as e:
            print(f"Error in TLE propagation: {e}")
            return None
                
    def propagate_rk45(self, tdm_wildcard, delta, delta_error, time_span_hours=6, step_minutes=0.5,
                      perturbations=None, return_vectors=True):
        """
        @brief Propagate orbit using RK45 integration with perturbation analysis
        @memberof OrbitPropagator
        
        Performs high-precision numerical orbit propagation using Runge-Kutta 4th/5th order
        integration with comprehensive perturbation modeling and detailed orbital analysis.
        
        @param tdm_wildcard Wildcard pattern for TDM observation files
        @param delta Delta parameter for TDM parsing tolerance
        @param delta_error Delta error parameter for TDM parsing
        @param time_span_hours Time span for propagation in hours
        @param step_minutes Time step between output points in minutes
        @param perturbations Dictionary of perturbation flags:
                            - 'j2': bool - J2 Earth oblateness perturbation
                            - 'third_body': bool - Third-body (Moon/Sun) effects
                            - 'solar_radiation': bool - Solar radiation pressure
                            - 'atmospheric_drag': bool - Atmospheric drag modeling
        @param return_vectors Whether to include position and velocity vectors in output
        
        @return Dictionary containing propagation results with same structure as propagate_tle()
        @retval dict Propagation results or None on error
        
        @note This method provides higher accuracy than TLE propagation but requires
              observation data for initial orbit determination
        
        @example
        @code{.py}
        perturbations = {
            'j2': True,
            'third_body': True,
            'solar_radiation': True,
            'atmospheric_drag': False
        }
        
        results = propagator.propagate_rk45(
            "tracking_data/*.tdm", 100, 30,
            time_span_hours=24,
            perturbations=perturbations
        )
        @endcode
        """

        # Set default perturbations if not provided
        if perturbations is None:
            perturbations = {
                'j2': False,
                'third_body': False,
                'solar_radiation': False,
                'atmospheric_drag': False
            }
            
        try:
            # Parse TDM data
            tdms = sc.parse_tdm_w(tdm_wildcard, delta, delta_error)
            print(f"Number of observations: {len(tdms.observations)}")
            
            # Create RADec object
            radec = sc.RADec(tdms.observations)
            
            # Use TDM for initial conditions if not explicitly provided
            r_init = radec.get_position()
            v_init = radec.get_velocity()
            jd_init = radec.epoch
                
            print(f"Initial position: {r_init}")
            print(f"Initial velocity: {v_init}")
            print(f"Initial epoch: {jd_init}")
                
            # Create list of epochs
            epochs = []
            for dt in np.arange(0, time_span_hours * 60, step_minutes):
                epochs.append(jd_init + dt * 60.0 / (24 * 60 * 60))
                
            # Create and configure the propagator
            p = sc.propagate.Propagator(r_init, v_init, epochs, sc.propagate.rk45_eci, 1)
            
            # Set perturbation flags
            p.j2 = perturbations.get('j2', False)
            p.tb = perturbations.get('third_body', False)
            p.solar = perturbations.get('solar_radiation', False)
            p.atm_exp = perturbations.get('atmospheric_drag', False)
            
            # Compute propagation
            p.compute()
            
            # Rotate all positions to ECI
            r_rk45_eci = []
            v_rk45_eci = []
            
            for pos, epoch in zip(p.ephem.positions, p.ephem.epochs):
                r_rk45_eci.append(sc.frames.to_eci(pos, epoch))
                
            for vel, epoch in zip(p.ephem.velocities, p.ephem.epochs):
                v_rk45_eci.append(sc.frames.to_eci(vel, epoch))

            # Convert to numpy array and normalize to Earth radii
            r_rk45_eci = np.array(r_rk45_eci) / self.earth_radius
            v_rk45_eci = np.array(v_rk45_eci)
            
            # Calculate orbital elements using ECI vectors
            orbital_elements = []
            for i in range(len(epochs)):
                oe = sc.orbmath.compute_orbital_elements(r_rk45_eci[i], v_rk45_eci[i])
                
                # Store orbital elements
                orbital_elements.append({
                    'a': oe.a,          # Semi-major axis (km)
                    'e': oe.ecc,        # Eccentricity
                    'i': oe.incl,       # Inclination (rad)
                    'raan': oe.Omega,   # Right Ascension of Ascending Node (rad)
                    'argp': oe.omega,   # Argument of Perigee (rad)
                    'nu': oe.nu,        # True Anomaly (rad)
                    'M': oe.m           # Mean Anomaly (rad)
                })
            
            # Prepare results
            results = {
                'epochs': epochs,
                'orbital_elements': orbital_elements
            }
            
            # Add position and velocity vectors if requested
            if return_vectors:
                results['positions'] = r_rk45_eci
                results['velocities'] = v_rk45_eci
                
            return results
            
        except Exception as e:
            print(f"Error in RK45 propagation: {e}")
            return None
            
    def compare_orbital_elements(self, tle_line1=None, tle_line2=None, tdm_wildcard=None, delta=100, delta_error=30,
                             time_span_hours=24, step_minutes=5, time_offset_minutes=28.5,
                             r_init=None, v_init=None, jd_init=None, perturbations_list=None,
                             show_plot=True, save_path=None):
        """
        @brief Compare orbital elements between different propagation methods
        @memberof OrbitPropagator
        
        Performs comprehensive comparison of orbital element evolution between
        TLE-based and RK45 propagation methods, or between multiple RK45 
        configurations with different perturbation settings.
        
        @param tle_line1 First line of TLE (optional)
        @param tle_line2 Second line of TLE (optional)
        @param tdm_wildcard Wildcard pattern for TDM files (optional)
        @param delta Delta parameter for TDM parsing
        @param delta_error Delta error parameter for TDM parsing
        @param time_span_hours Time span for comparison in hours
        @param step_minutes Time step between analysis points in minutes
        @param time_offset_minutes Time offset between TLE and observations
        @param r_init Initial position vector [x, y, z] in km (optional)
        @param v_init Initial velocity vector [vx, vy, vz] in km/s (optional)
        @param jd_init Initial Julian date (optional)
        @param perturbations_list List of perturbation configuration dictionaries
        @param show_plot Whether to generate comparison plots
        @param save_path Base path for saving plots (optional)
        
        @return Dictionary containing statistical comparison results
        @retval dict Statistics including mean/max/std differences in position and orbital elements
        
        @note This method generates multiple plots showing:
              - Individual orbital element evolution
              - Position differences over time
              - Statistical summaries of propagation differences
        
        @example
        @code{.py}
        perturbations_list = [
            {'j2': True, 'third_body': False},
            {'j2': True, 'third_body': True, 'solar_radiation': True}
        ]
        
        stats = propagator.compare_orbital_elements(
            tle_line1=line1, tle_line2=line2,
            tdm_wildcard="data/*.tdm",
            time_span_hours=48,
            perturbations_list=perturbations_list,
            save_path="comparison_plots"
        )
        
        # Access statistics
        print(f"Mean position difference: {stats['TLE_vs_RK45']['mean_position_diff']:.3f} km")
        @endcode
        """
        
        # Initialize inputs and epochs
        epochs = []
        
        # Define default perturbations list if not provided
        if perturbations_list is None:
            perturbations_list = [
                {'j2': True, 'third_body': False, 'solar_radiation': False, 'atmospheric_drag': False},
                {'j2': True, 'third_body': True, 'solar_radiation': False, 'atmospheric_drag': False},
                {'j2': True, 'third_body': True, 'solar_radiation': True, 'atmospheric_drag': False},
                {'j2': True, 'third_body': True, 'solar_radiation': True, 'atmospheric_drag': True}
            ]
        
        # Track all trajectories for comparison
        trajectories = []
        labels = []
        
        # ---------------------------
        # Step 1: Process TLE if provided
        # ---------------------------
        if tle_line1 and tle_line2:
            try:
                # Create TLE object
                tle_obj = sc.TwoLineElement(tle_line1, tle_line2)
                jd0 = tle_obj.get_jd()
                
                # Initialize arrays
                epochs = []
                r_tle = []
                v_tle = []
                
                # Propagate TLE
                for dt in np.arange(0, time_span_hours * 60, step_minutes):
                    # Current epoch
                    current_epoch = jd0 + dt * 60 / (24 * 60 * 60)
                    epochs.append(current_epoch)
                    
                    # Get position and velocity at current time
                    r_ecef = tle_obj.get_position_at(time_offset_minutes + dt)
                    v_ecef = tle_obj.get_velocity_at(time_offset_minutes + dt)
                    
                    # Store for later processing
                    r_tle.append(r_ecef)
                    v_tle.append(v_ecef)
                
                # Add to trajectories
                trajectories.append({
                    'epochs': epochs,
                    'positions': r_tle,
                    'velocities': v_tle,
                    'type': 'TLE'
                })
                
                labels.append('TLE')
                
            except Exception as e:
                print(f"Error in TLE processing: {e}")
        
        # ---------------------------
        # Step 2: Process TDM data if provided
        # ---------------------------
        if tdm_wildcard:
            try:
                # Parse TDM data
                tdms = sc.parse_tdm_w(tdm_wildcard, delta, delta_error)
                print(f"Number of observations: {len(tdms.observations)}")
                
                # Create RADec object
                radec = sc.RADec(tdms.observations)
                
                # Use TDM for initial conditions if not explicitly provided
                r_init = radec.get_position()
                v_init = radec.get_velocity()
                jd_init = radec.epoch
                
                print(f"Initial position: {r_init}")
                print(f"Initial velocity: {v_init}")
                print(f"Initial epoch: {jd_init}")
                
                # If TLE is given, calculate time difference
                if tle_line1 and tle_line2:
                    print(f"Time difference (minutes): {abs(jd_init - jd0) * 24 * 60 * 60 / 60.0}")
            
            except Exception as e:
                print(f"Error in TDM processing: {e}")
                if r_init is None or v_init is None or jd_init is None:
                    print("Error: Initial conditions not available.")
                    return None
        
        # Create epochs if they don't exist yet
        if not epochs and jd_init is not None:
            for dt in np.arange(0, time_span_hours * 60, step_minutes):
                epochs.append(jd_init + dt * 60.0 / (24 * 60 * 60))
        
        # ---------------------------
        # Step 3: Process RK45 propagations with different perturbations
        # ---------------------------
        if r_init is not None and v_init is not None and epochs:
            for perturb_idx, perturbations in enumerate(perturbations_list):
                try:
                    # Create propagator
                    p = sc.propagate.Propagator(r_init, v_init, epochs, sc.propagate.rk45_eci, 1)
                    
                    # Set perturbation flags
                    p.j2 = perturbations.get('j2', False)
                    p.tb = perturbations.get('third_body', False)
                    p.solar = perturbations.get('solar_radiation', False)
                    p.atm_exp = perturbations.get('atmospheric_drag', False)
                    
                    # Compute propagation
                    p.compute()
                    
                    # Extract positions and velocities
                    r_rk45 = p.ephem.positions
                    v_rk45 = p.ephem.velocities
                    
                    # Create label for this propagation
                    label = f"RK45 [j2={p.j2}, tb={p.tb}, srp={p.solar}, drag={p.atm_exp}]"
                    
                    # Add to trajectories
                    trajectories.append({
                        'epochs': epochs,
                        'positions': r_rk45,
                        'velocities': v_rk45,
                        'type': 'RK45',
                        'perturbations': perturbations.copy()
                    })
                    
                    labels.append(label)
                    
                except Exception as e:
                    print(f"Error in RK45 propagation {perturb_idx}: {e}")
        
        # ---------------------------
        # Step 4: Convert positions to ECI and calculate orbital elements
        # ---------------------------
        for traj in trajectories:
            # Convert positions and velocities to ECI
            r_eci = []
            v_eci = []
            
            for i, epoch in enumerate(traj['epochs']):
                r_eci.append(sc.frames.to_eci(traj['positions'][i], epoch))
                v_eci.append(sc.frames.to_eci(traj['velocities'][i], epoch))
            
            traj['positions_eci'] = r_eci
            traj['velocities_eci'] = v_eci
            
            # Calculate orbital elements
            orbital_elements = []
            for i in range(len(r_eci)):
                oe = sc.orbmath.compute_orbital_elements(r_eci[i], v_eci[i])
                orbital_elements.append([oe.a, oe.ecc, oe.incl, oe.Omega, oe.omega, oe.m])
            
            traj['orbital_elements'] = np.array(orbital_elements)
        
        # ---------------------------
        # Step 5: Calculate differences between trajectories
        # ---------------------------
        # Use the first trajectory as the reference if we have multiple
        if len(trajectories) > 1:
            reference = trajectories[0]
            
            for traj_idx in range(1, len(trajectories)):
                traj = trajectories[traj_idx]
                
                # Calculate position differences
                position_diffs = []
                for i in range(len(reference['positions_eci'])):
                    r_ref = np.array(reference['positions_eci'][i])
                    r_traj = np.array(traj['positions_eci'][i])
                    
                    # Compute componentwise and magnitude differences
                    diff = [
                        abs(r_ref[0] - r_traj[0]),
                        abs(r_ref[1] - r_traj[1]),
                        abs(r_ref[2] - r_traj[2]),
                        np.linalg.norm(r_ref - r_traj)
                    ]
                    position_diffs.append(diff)
                
                traj['position_diffs'] = np.array(position_diffs)
                
                # Calculate velocity differences
                velocity_diffs = []
                for i in range(len(reference['velocities_eci'])):
                    v_ref = np.array(reference['velocities_eci'][i])
                    v_traj = np.array(traj['velocities_eci'][i])
                    
                    # Compute componentwise and magnitude differences
                    diff = [
                        abs(v_ref[0] - v_traj[0]),
                        abs(v_ref[1] - v_traj[1]),
                        abs(v_ref[2] - v_traj[2]),
                        np.linalg.norm(v_ref - v_traj)
                    ]
                    velocity_diffs.append(diff)
                
                traj['velocity_diffs'] = np.array(velocity_diffs)
                
                # Calculate orbital element differences
                element_diffs = []
                for i in range(len(reference['orbital_elements'])):
                    oe_ref = reference['orbital_elements'][i]
                    oe_traj = traj['orbital_elements'][i]
                    
                    # Compute differences for each orbital element
                    diff = [
                        abs(oe_ref[0] - oe_traj[0]),  # Semi-major axis
                        abs(oe_ref[1] - oe_traj[1]),  # Eccentricity
                        abs(oe_ref[2] - oe_traj[2]),  # Inclination
                        abs(oe_ref[3] - oe_traj[3]),  # RAAN
                        abs(oe_ref[4] - oe_traj[4]),  # Arg of perigee
                        abs(oe_ref[5] - oe_traj[5])   # Mean anomaly
                    ]
                    element_diffs.append(diff)
                
                traj['element_diffs'] = np.array(element_diffs)
        
        # ---------------------------
        # Step 6: Plotting (Modified to save plots separately)
        # ---------------------------
        if show_plot or save_path:
            # Time array for plotting (hours from start)
            plot_times = np.arange(len(epochs)) * step_minutes / 60.0
            
            # Plot orbital elements for all trajectories
            element_names = ['Semi-major axis (a)', 'Eccentricity (e)', 'Inclination (i)',
                             'RAAN (Ω)', 'Argument of Perigee (ω)', 'Mean Anomaly (M)']
            
            # Create separate plots for each orbital element
            for i, element_name in enumerate(element_names):
                fig, ax = plt.subplots(1, 1, figsize=(10, 6))
                
                for traj_idx, traj in enumerate(trajectories):
                    ax.plot(plot_times, traj['orbital_elements'][:, i], label=labels[traj_idx])
                
                ax.set_title(element_name)
                ax.set_xlabel('Time (hours)')
                ax.grid(True)
                ax.legend()
                
                plt.tight_layout()
                
                if save_path:
                    # Create filename-safe version of element name
                    safe_name = element_name.replace(' ', '_').replace('(', '').replace(')', '').replace('Ω', 'RAAN').replace('ω', 'omega')
                    plt.savefig(f"{save_path}_{safe_name}.png", dpi=300, bbox_inches='tight')
                
                if show_plot:
                    plt.show()
                
                plt.close()  # Close figure to free memory

        # ---------------------------
        # Step 7: Prepare statistics
        # ---------------------------
        stats = {}

        # Calculate mean, max, and std for each trajectory comparison
        if len(trajectories) > 1:
            for traj_idx in range(1, len(trajectories)):
                traj = trajectories[traj_idx]
                stats_key = f"{labels[0]}_vs_{labels[traj_idx]}"
                
                stats[stats_key] = {
                    'mean_position_diff': np.mean(traj['position_diffs'][:, 3]),
                    'max_position_diff': np.max(traj['position_diffs'][:, 3]),
                    'std_position_diff': np.std(traj['position_diffs'][:, 3]),
                    'mean_semi_major_diff': np.mean(traj['element_diffs'][:, 0]),
                    'mean_ecc_diff': np.mean(traj['element_diffs'][:, 1]),
                    'mean_inc_diff': np.mean(traj['element_diffs'][:, 2]),
                    'mean_raan_diff': np.mean(traj['element_diffs'][:, 3]),
                    'mean_argp_diff': np.mean(traj['element_diffs'][:, 4]),
                    'mean_mean_anomaly_diff': np.mean(traj['element_diffs'][:, 5])
                }

        return stats
    
    def set_perturbation_parameters(self, params):
        """
        @brief Set perturbation model parameters
        @memberof OrbitPropagator
        
        Configures the physical parameters used in perturbation force modeling,
        including solar radiation pressure and atmospheric drag coefficients.
        
        @param params Dictionary of perturbation parameters:
                     - 'CR': float - Coefficient of reflectivity for SRP (typically 1.0-2.0)
                     - 'Am': float - Area-to-mass ratio in m²/kg
                     - 'CD': float - Drag coefficient (typically 2.0-2.5)
                     - 'Sc': float - Solar constant in W/m²
                     - 'nu': float - Solar flux variation factor
                     - 'H0': float - Atmospheric scale height in km
                     - 'rho0': float - Reference atmospheric density in kg/m³
                          
        @return Success status
        @retval bool True if parameters were set successfully, False otherwise
        
        @note These parameters significantly affect the accuracy of perturbation modeling.
              Default values are provided but should be adjusted based on specific
              satellite characteristics and mission requirements.
        
        @example
        @code{.py}
        # Configure for a typical CubeSat
        params = {
            'CR': 1.8,     # Radiation pressure coefficient
            'Am': 0.01,    # Area-to-mass ratio (m²/kg)
            'CD': 2.2      # Drag coefficient
        }
        
        success = propagator.set_perturbation_parameters(params)
        if success:
            print("Parameters updated successfully")
        @endcode
        """
        perturbation = sc.orbmath.perturbation
        try:
            # Set SRP parameters
            if 'CR' in params:
                perturbation.CR = float(params['CR'])
            if 'Am' in params:
                perturbation.Am = float(params['Am'])
            if 'Sc' in params:
                perturbation.Sc = float(params['Sc'])
            if 'nu' in params:
                perturbation.nu = float(params['nu'])
                
            # Set atmospheric drag parameters
            if 'CD' in params:
                perturbation.C_D = float(params['CD'])
            if 'H0' in params:
                perturbation.H0 = float(params['H0'])
            if 'rho0' in params:
                perturbation.rho0 = float(params['rho0'])
                
            return True
        except Exception as e:
            print(f"Error setting perturbation parameters: {e}")
            return False
            
    def get_perturbation_parameters(self):
        """
        @brief Get current perturbation model parameters
        @memberof OrbitPropagator
        
        Retrieves the current values of all perturbation model parameters
        used in force modeling calculations.
        
        @return Dictionary of current perturbation parameters
        @retval dict Parameters including SRP, drag, and gravitational constants
        
        @note Useful for verifying parameter settings and documenting
              the configuration used in specific propagation runs.
        
        @example
        @code{.py}
        params = propagator.get_perturbation_parameters()
        
        print(f"Current CR coefficient: {params['CR']}")
        print(f"Area-to-mass ratio: {params['Am']} m²/kg")
        print(f"Drag coefficient: {params['CD']}")
        @endcode
        """
        perturbation = sc.orbmath.perturbation
        return {
            # SRP parameters
            'CR': float(perturbation.CR),
            'Am': float(perturbation.Am),
            'Sc': float(perturbation.Sc),
            'nu': float(perturbation.nu),
            
            # Atmospheric drag parameters
            'CD': float(perturbation.C_D),
            'H0': float(perturbation.H0),
            'rho0': float(perturbation.rho0),
            
            # Other constants
            'J2': float(perturbation.J2),
            'MU_MOON': float(perturbation.MU_MOON)
        }


class JavaGUIBridge:
    """
    @brief Bridge class for Java-Python interface
    @memberof JavaGUIBridge
    
    The JavaGUIBridge class provides a clean, standardized interface for Java
    applications to interact with the Orbit Toolkit Python code. It handles
    JSON serialization, error handling, and provides status updates for
    long-running operations.
    
    Key Features:
    - JSON-based command interface for cross-language compatibility
    - Comprehensive error handling with structured error responses
    - Progress callbacks for long-running operations
    - Automatic data type conversion for Java compatibility
    - Support for all core Orbit Toolkit functionality
    
    @note This class is specifically designed for integration with Java GUIs
          and provides a stable API that can be called from Java using
          Python bridge libraries such as Jep or Py4J.
    
    @example
    @code{.py}
    # Create bridge instance
    bridge = JavaGUIBridge()
    
    # Set up progress callback
    def progress_callback(percent, message):
        print(f"Progress: {percent}% - {message}")
    
    bridge.set_status_callback(progress_callback)
    
    # Execute command from Java
    command = {
        'command': 'visualize_tle',
        'tle_line1': line1,
        'tle_line2': line2,
        'time_span_hours': 6,
        'save_path': 'output.png'
    }
    
    result = bridge.execute_command(json.dumps(command))
    response = json.loads(result)
    @endcode
    """
    
    def __init__(self):
        """
        @brief Initialize the Java bridge
        @memberof JavaGUIBridge
        
        Creates instances of the core Orbit Toolkit classes and sets up
        the bridge infrastructure for Java communication.
        """
        self.visualizer = OrbitVisualizer()  ///< Orbit visualization instance
        self.propagator = OrbitPropagator()  ///< Orbit propagation instance
        self.status_callback = None          ///< Progress callback function
        
    def set_status_callback(self, callback_func):
        """
        @brief Set a callback function for progress updates
        @memberof JavaGUIBridge
        
        @param callback_func Function that accepts (progress_percent, status_message)
                            where progress_percent is 0-100 and status_message is a string
        
        @note The callback function will be called periodically during long-running
              operations to provide progress feedback to the Java GUI.
        """
        self.status_callback = callback_func
        
    def _update_status(self, progress, message):
        """
        @brief Internal method to update status if callback is registered
        @memberof JavaGUIBridge
        
        @param progress Progress percentage (0-100)
        @param message Status message string
        """
        if self.status_callback:
            try:
                self.status_callback(progress, message)
            except Exception as e:
                print(f"Error in status callback: {e}")
    
    def execute_command(self, command_json):
        """
        @brief Execute a command from the Java GUI
        @memberof JavaGUIBridge
        
        Main entry point for Java applications to execute Orbit Toolkit commands.
        Commands are specified in JSON format and results are returned as JSON.
        
        @param command_json JSON string containing the command and parameters
        
        @return JSON string with structured results or error information
        @retval str JSON response with 'status' field ('success' or 'error')
        
        Supported commands:
        - 'visualize_tle': TLE orbit visualization
        - 'visualize_rk45': RK45 orbit visualization  
        - 'compare_orbits': Compare TLE vs RK45 propagation
        - 'propagate_tle': TLE orbit propagation with analysis
        - 'propagate_rk45': RK45 orbit propagation with analysis
        - 'compare_orbital_elements': Comprehensive orbital elements comparison
        - 'set_perturbation_params': Set perturbation model parameters
        - 'get_perturbation_params': Get current perturbation parameters
        
        @example
        @code{.py}
        command = {
            'command': 'compare_orbits',
            'tle_line1': line1,
            'tle_line2': line2,
            'tdm_wildcard': 'data/*.tdm',
            'delta': 100,
            'delta_error': 30,
            'time_span_hours': 12,
            'save_path': 'comparison.png'
        }
        
        result_json = bridge.execute_command(json.dumps(command))
        result = json.loads(result_json)
        
        if result['status'] == 'success':
            print("Command executed successfully")
        else:
            print(f"Error: {result['message']}")
        @endcode
        """
        try:
            # Parse command
            command = json.loads(command_json)
            
            # Get command type
            cmd_type = command.get('command', '')
            
            # Execute command based on type
            command_handlers = {
                'visualize_tle': self._handle_visualize_tle,
                'visualize_rk45': self._handle_visualize_rk45,
                'compare_orbits': self._handle_compare_orbits,
                'propagate_tle': self._handle_propagate_tle,
                'propagate_rk45': self._handle_propagate_rk45,
                'compare_orbital_elements': self._handle_compare_orbital_elements,
                'set_perturbation_params': self._handle_set_perturbation_params,
                'get_perturbation_params': self._handle_get_perturbation_params
            }
            
            if cmd_type in command_handlers:
                self._update_status(0, f"Starting {cmd_type} operation")
                result = command_handlers[cmd_type](command)
                self._update_status(100, f"Completed {cmd_type} operation")
                return result
            else:
                error_msg = f'Unknown command: {cmd_type}'
                self._update_status(100, f"Error: {error_msg}")
                return self._create_error_response(error_msg)
                
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format: {str(e)}"
            self._update_status(100, f"Error: {error_msg}")
            return self._create_error_response(error_msg)
        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            self._update_status(100, f"Error: {error_msg}")
            return self._create_error_response(error_msg)
    
    def _create_success_response(self, data=None):
        """
        @brief Create a standardized success response
        @memberof JavaGUIBridge
        
        @param data Data to include in the response
        @return JSON string with success status
        """
        return json.dumps({
            'status': 'success',
            'data': data
        })

    def _create_error_response(self, message, error_code=None):
        """
        @brief Create a standardized error response
        @memberof JavaGUIBridge
        
        @param message Error message
        @param error_code Optional error code
        @return JSON string with error status
        """
        response = {
            'status': 'error',
            'message': message
        }
        if error_code:
            response['error_code'] = error_code
        return json.dumps(response)

    def _convert_to_serializable(self, obj):
        """
        @brief Convert numpy arrays and other objects to JSON-serializable formats
        @memberof JavaGUIBridge
        
        @param obj Object to convert
        @return JSON-serializable version of the object
        """
        if obj is None:
            return None

        if hasattr(obj, 'tolist'):  # numpy arrays and similar
            return obj.tolist()
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (int, float, str, bool)):
            return obj
        else:
            # If we can't directly serialize it, convert to string
            return str(obj)

    def _handle_visualize_tle(self, command):
        """
        @brief Handle visualize_tle command
        @memberof JavaGUIBridge
        
        @param command Command dictionary
        @return JSON response string
        """
        try:
            # Extract parameters
            tle_line1 = command.get('tle_line1', '')
            tle_line2 = command.get('tle_line2', '')
            time_span_hours = float(command.get('time_span_hours', 12))
            step_minutes = float(command.get('step_minutes', 0.5))
            save_path = command.get('save_path', None)

            # Validate required parameters
            if not tle_line1 or not tle_line2:
                return self._create_error_response("TLE lines are required", "MISSING_PARAMETERS")

            self._update_status(10, "Parameters validated, beginning TLE visualization")

            # Execute visualization
            fig, ax, positions = self.visualizer.visualize_tle(
                tle_line1, tle_line2,
                time_span_hours=time_span_hours,
                step_minutes=step_minutes,
                show_plot=False,
                save_path=save_path
            )

            self._update_status(90, "TLE visualization complete, processing results")

            # Check if visualization was successful
            if positions is None:
                return self._create_error_response("Failed to visualize TLE orbit", "VISUALIZATION_FAILED")

            # Return result
            result = {
                'save_path': save_path,
                'positions': self._convert_to_serializable(positions)
            }

            return self._create_success_response(result)

        except Exception as e:
            error_msg = f"Error in TLE visualization: {str(e)}"
            return self._create_error_response(error_msg, "TLE_VISUALIZATION_ERROR")

    def _handle_visualize_rk45(self, command):
        """
        @brief Handle visualize_rk45 command
        @memberof JavaGUIBridge
        
        @param command Command dictionary
        @return JSON response string
        """
        try:
            # Extract parameters
            tdm_wildcard = command.get('tdm_wildcard')
            delta = float(command.get('delta', 100))
            delta_error = float(command.get('delta_error', 30))
            time_span_hours = float(command.get('time_span_hours', 12))
            step_minutes = float(command.get('step_minutes', 0.5))
            perturbations = command.get('perturbations', None)
            save_path = command.get('save_path', None)

            # Validate required parameters
            if not tdm_wildcard:
                return self._create_error_response("TDM wildcard is required", "MISSING_PARAMETERS")

            self._update_status(10, "Parameters validated, beginning RK45 visualization")

            # Execute visualization
            fig, ax, positions = self.visualizer.visualize_rk45(
                tdm_wildcard=tdm_wildcard,
                delta=delta,
                delta_error=delta_error,
                time_span_hours=time_span_hours,
                step_minutes=step_minutes,
                perturbations=perturbations,
                show_plot=False,
                save_path=save_path
            )

            self._update_status(90, "RK45 visualization complete, processing results")

            # Check if visualization was successful
            if positions is None:
                return self._create_error_response("Failed to visualize RK45 orbit", "VISUALIZATION_FAILED")

            # Return result
            result = {
                'save_path': save_path,
                'positions': self._convert_to_serializable(positions)
            }

            return self._create_success_response(result)

        except Exception as e:
            error_msg = f"Error in RK45 visualization: {str(e)}"
            return self._create_error_response(error_msg, "RK45_VISUALIZATION_ERROR")

    def _handle_compare_orbits(self, command):
        """
        @brief Handle compare_orbits command
        @memberof JavaGUIBridge
        
        @param command Command dictionary
        @return JSON response string
        """
        try:
            # Extract parameters
            tle_line1 = command.get('tle_line1', '')
            tle_line2 = command.get('tle_line2', '')
            tdm_wildcard = command.get('tdm_wildcard')
            delta = float(command.get('delta', 100))
            delta_error = float(command.get('delta_error', 30))
            time_span_hours = float(command.get('time_span_hours', 6))
            step_minutes = float(command.get('step_minutes', 0.5))
            time_offset_minutes = float(command.get('time_offset_minutes', 0))
            perturbations_list = command.get('perturbations_list', None)
            save_path = command.get('save_path', None)

            # Validate required parameters
            if (not tle_line1 or not tle_line2) and not tdm_wildcard:
                return self._create_error_response(
                    "Either TLE lines or TDM wildcard must be provided",
                    "MISSING_PARAMETERS"
                )

            self._update_status(10, "Parameters validated, beginning orbit comparison")

            # Execute comparison
            fig, ax, tle_pos, rk_positions = self.visualizer.compare_orbits(
                tle_line1=tle_line1,
                tle_line2=tle_line2,
                tdm_wildcard=tdm_wildcard,
                delta=delta,
                delta_error=delta_error,
                time_span_hours=time_span_hours,
                step_minutes=step_minutes,
                time_offset_minutes=time_offset_minutes,
                perturbations_list=perturbations_list,
                show_plot=False,
                save_path=save_path
            )

            self._update_status(90, "Orbit comparison complete, processing results")

            # Check if comparison was successful
            if tle_pos is None or rk_positions is None:
                return self._create_error_response("Failed to compare orbits", "COMPARISON_FAILED")

            # Return result
            result = {
                'save_path': save_path,
                'tle_positions': self._convert_to_serializable(tle_pos),
                'rk_positions': self._convert_to_serializable(rk_positions)
            }

            return self._create_success_response(result)

        except Exception as e:
            error_msg = f"Error in orbit comparison: {str(e)}"
            return self._create_error_response(error_msg, "ORBIT_COMPARISON_ERROR")

    def _handle_propagate_tle(self, command):
        """
        @brief Handle propagate_tle command
        @memberof JavaGUIBridge
        
        @param command Command dictionary
        @return JSON response string
        """
        try:
            # Extract parameters
            tle_line1 = command.get('tle_line1', '')
            tle_line2 = command.get('tle_line2', '')
            time_span_hours = float(command.get('time_span_hours', 12))
            step_minutes = float(command.get('step_minutes', 0.5))
            return_vectors = bool(command.get('return_vectors', True))

            # Validate required parameters
            if not tle_line1 or not tle_line2:
                return self._create_error_response("TLE lines are required", "MISSING_PARAMETERS")

            self._update_status(10, "Parameters validated, beginning TLE propagation")

            # Execute propagation
            results = self.propagator.propagate_tle(
                tle_line1=tle_line1,
                tle_line2=tle_line2,
                time_span_hours=time_span_hours,
                step_minutes=step_minutes,
                return_vectors=return_vectors
            )

            self._update_status(90, "TLE propagation complete, processing results")

            # Check if propagation was successful
            if results is None:
                return self._create_error_response("Failed to propagate TLE orbit", "PROPAGATION_FAILED")

            # Convert to serializable format
            serialized_results = self._convert_to_serializable(results)

            return self._create_success_response(serialized_results)

        except Exception as e:
            error_msg = f"Error in TLE propagation: {str(e)}"
            return self._create_error_response(error_msg, "TLE_PROPAGATION_ERROR")

    def _handle_propagate_rk45(self, command):
        """
        @brief Handle propagate_rk45 command
        @memberof JavaGUIBridge
        
        @param command Command dictionary
        @return JSON response string
        """
        try:
            # Extract parameters
            tdm_wildcard = command.get('tdm_wildcard')
            delta = float(command.get('delta', 100))
            delta_error = float(command.get('delta_error', 30))
            time_span_hours = float(command.get('time_span_hours', 12))
            step_minutes = float(command.get('step_minutes', 0.5))
            perturbations = command.get('perturbations', None)
            return_vectors = bool(command.get('return_vectors', True))

            # Validate required parameters
            if not tdm_wildcard:
                return self._create_error_response("TDM wildcard is required", "MISSING_PARAMETERS")

            self._update_status(10, "Parameters validated, beginning RK45 propagation")

            # Execute propagation
            results = self.propagator.propagate_rk45(
                tdm_wildcard=tdm_wildcard,
                delta=delta,
                delta_error=delta_error,
                time_span_hours=time_span_hours,
                step_minutes=step_minutes,
                perturbations=perturbations,
                return_vectors=return_vectors
            )

            self._update_status(90, "RK45 propagation complete, processing results")

            # Check if propagation was successful
            if results is None:
                return self._create_error_response("Failed to propagate RK45 orbit", "PROPAGATION_FAILED")

            # Convert to serializable format
            serialized_results = self._convert_to_serializable(results)

            return self._create_success_response(serialized_results)

        except Exception as e:
            error_msg = f"Error in RK45 propagation: {str(e)}"
            return self._create_error_response(error_msg, "RK45_PROPAGATION_ERROR")

    def _handle_compare_orbital_elements(self, command):
        """
        @brief Handle compare_orbital_elements command
        @memberof JavaGUIBridge
        
        @param command Command dictionary
        @return JSON response string
        """
        try:
            # Extract parameters with defaults
            tle_line1 = command.get('tle_line1')
            tle_line2 = command.get('tle_line2')
            tdm_wildcard = command.get('tdm_wildcard')
            delta = float(command.get('delta', 100))
            delta_error = float(command.get('delta_error', 30))
            time_span_hours = float(command.get('time_span_hours', 24))
            step_minutes = float(command.get('step_minutes', 5))
            time_offset_minutes = float(command.get('time_offset_minutes', 28.5))
            r_init = command.get('r_init')
            v_init = command.get('v_init')
            jd_init = command.get('jd_init')
            perturbations_list = command.get('perturbations_list')
            show_plot = bool(command.get('show_plot', False))
            save_path = command.get('save_path')

            # Validate that we have at least minimum required data
            if (not tle_line1 or not tle_line2) and not tdm_wildcard and not (r_init and v_init and jd_init):
                return self._create_error_response(
                    "Either TLE lines, TDM wildcard, or initial position/velocity/epoch must be provided",
                    "MISSING_PARAMETERS"
                )

            self._update_status(10, "Parameters validated, beginning orbital elements comparison")

            # Execute comparison
            stats = self.propagator.compare_orbital_elements(
                tle_line1=tle_line1,
                tle_line2=tle_line2,
                tdm_wildcard=tdm_wildcard,
                delta=delta,
                delta_error=delta_error,
                time_span_hours=time_span_hours,
                step_minutes=step_minutes,
                time_offset_minutes=time_offset_minutes,
                r_init=r_init,
                v_init=v_init,
                jd_init=jd_init,
                perturbations_list=perturbations_list,
                show_plot=show_plot,
                save_path=save_path
            )

            self._update_status(90, "Orbital elements comparison complete, processing results")

            # Check if comparison was successful
            if stats is None:
                return self._create_error_response("Failed to compare orbital elements", "COMPARISON_FAILED")

            # Convert to serializable format
            serialized_stats = self._convert_to_serializable(stats)

            return self._create_success_response(serialized_stats)

        except Exception as e:
            error_msg = f"Error in orbital elements comparison: {str(e)}"
            return self._create_error_response(error_msg, "ORBITAL_ELEMENTS_COMPARISON_ERROR")

    def _handle_set_perturbation_params(self, command):
        """
        @brief Handle set_perturbation_params command
        @memberof JavaGUIBridge
        
        @param command Command dictionary
        @return JSON response string
        """
        try:
            # Extract parameters
            params = command.get('params', {})

            if not params:
                return self._create_error_response("Perturbation parameters are required", "MISSING_PARAMETERS")

            self._update_status(10, "Setting perturbation parameters")

            # Set parameters
            success = self.propagator.set_perturbation_parameters(params)

            self._update_status(90, "Finished setting perturbation parameters")

            # Return result
            if success:
                return self._create_success_response({"message": "Perturbation parameters set successfully"})
            else:
                return self._create_error_response("Failed to set perturbation parameters", "PARAMETER_SETTING_FAILED")

        except Exception as e:
            error_msg = f"Error setting perturbation parameters: {str(e)}"
            return self._create_error_response(error_msg, "PERTURBATION_PARAMS_ERROR")

    def _handle_get_perturbation_params(self, command):
        """
        @brief Handle get_perturbation_params command
        @memberof JavaGUIBridge
        
        @param command Command dictionary
        @return JSON response string
        """
        try:
            self._update_status(10, "Getting perturbation parameters")

            # Get parameters
            params = self.propagator.get_perturbation_parameters()

            self._update_status(90, "Finished getting perturbation parameters")

            # Convert to serializable format if needed
            serialized_params = self._convert_to_serializable(params)

            return self._create_success_response(serialized_params)

        except Exception as e:
            error_msg = f"Error getting perturbation parameters: {str(e)}"
            return self._create_error_response(error_msg, "PERTURBATION_PARAMS_ERROR")

    def get_version(self):
        """
        @brief Return version information about the toolkit
        @memberof JavaGUIBridge
        
        @return Dictionary with version information
        """
        return {
            'name': 'Orbit Toolkit',
            'version': '1.0.0',
            'python_interface': 'JavaBridge 1.0'
        }

    def shutdown(self):
        """
        @brief Perform any necessary cleanup before shutting down
        @memberof JavaGUIBridge
        
        @return Success status
        """
        # Add any cleanup code here if needed
        plt.close('all')  # Close all matplotlib figures
        self._update_status(100, "Bridge shutdown complete")
        return True
