#!/usr/bin/env python3.8
"""
Orbit Toolkit - Python interface for orbit visualization and propagation

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
    """Class for visualizing satellite orbits in 3D"""
    
    def __init__(self):
        """Initialize the orbit visualizer"""
        self.fig = None
        self.ax = None
        self.earth_radius = 6378.0  # km
        
    def _setup_plot(self, title="Satellite Orbit Visualization"):
        """Set up the 3D plot"""
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
        """Plot an orbit path"""
        positions = np.array(positions)
        self.ax.plot(positions[:, 0], positions[:, 1], positions[:, 2],
                    color=color, linewidth=line_width, label=label)
                    
    def _plot_x_vs_time(self, rk_positions_list, labels, step_minutes=0.5, title="X vs Time for RK45 Orbits"):
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
        Visualize a satellite orbit using TLE data
        
        Args:
            tle_line1 (str): First line of TLE
            tle_line2 (str): Second line of TLE
            time_span_hours (float): Time span to propagate in hours
            step_minutes (float): Time step in minutes
            show_plot (bool): Whether to show the plot
            save_path (str): Path to save the plot, if None the plot is not saved
            
        Returns:
            tuple: (fig, ax, positions) - The figure, axis and positions array
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
        Visualize a satellite orbit using RK45 integration
        
        Args:
            tdm_wildcard (str): Wildcard pattern for TDM files
            delta (float): Delta parameter for TDM parsing
            delta_error (float): Delta error parameter for TDM parsing
            time_span_hours (float): Time span to propagate in hours
            step_minutes (float): Time step in minutes
            perturbations (dict): Dictionary of perturbation flags
                                 {'j2': bool, 'third_body': bool, 
                                  'solar_radiation': bool, 'atmospheric_drag': bool}
            show_plot (bool): Whether to show the plot
            save_path (str): Path to save the plot, if None the plot is not saved
            
        Returns:
            tuple: (fig, ax, positions) - The figure, axis and positions array
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
            Compare TLE and RK45 orbit propagation by plotting both on the same 3D plot.

            Args:
                tle_line1 (str): First line of TLE
                tle_line2 (str): Second line of TLE
                tdm_wildcard (str): Wildcard pattern for TDM files of RK45
                delta (float): Delta parameter for TDM parsing
                delta_error (float): Delta error parameter for TDM parsing
                time_span_hours (float): Time span to propagate in hours
                step_minutes (float): Time step in minutes
                perturbations_list (list): List of dictionaries with perturbation flags for RK45 propagations.
                show_plot (bool): Whether to show the plot
                save_path (str): Path to save the plot, if any

            Returns:
                tuple: (fig, ax, tle_positions, rk_positions) - The figure, axis, and position arrays
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
            
#            # Plot X vs Time to visualize divergence
#            labels = [
#                f"RK45 [j2={p.get('j2', True)}, tb={p.get('third_body', False)}, "
#                f"srp={p.get('solar_radiation', False)}, drag={p.get('atmospheric_drag', False)}]"
#                for p in perturbations_list
#            ]
#            self._plot_x_vs_time(rk_positions_all, labels, step_minutes)

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

class OrbitPropagator(OrbitVisualizer):
    """Class for propagating satellite orbits"""
    
    def __init__(self):
        """Initialize the orbit propagator"""
        # Call the parent class constructor
        
        self.earth_radius = 6378.0
        
    def propagate_tle(self, tle_line1, tle_line2, time_span_hours=6, step_minutes=0.5,
                         return_vectors=True):
            """
            Propagate orbit using TLE data
            
            Args:
                tle_line1 (str): First line of TLE
                tle_line2 (str): Second line of TLE
                time_span_hours (float): Time span to propagate in hours
                step_minutes (float): Time step in minutes
                return_vectors (bool): Whether to return position and velocity vectors
                
            Returns:
                dict: Dictionary containing propagation results
                     {'epochs': list, 'positions': list, 'velocities': list (if return_vectors),
                      'orbital_elements': list}
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
        Propagate orbit using RK45 integration
        
        Args:
            tdm_wildcard (str, optional): Wildcard pattern for TDM files
            delta (float): Delta parameter for TDM parsing (default: 100)
            delta_error (float): Delta error parameter for TDM parsing (default: 30)
            time_span_hours (float): Time span to propagate in hours
            step_minutes (float): Time step in minutes
            perturbations (dict): Dictionary of perturbation flags
            return_vectors (bool): Whether to return position and velocity vectors
            
        Returns:
            dict: Dictionary containing propagation results
                 {'epochs': list, 'positions': list (if return_vectors), 
                  'velocities': list (if return_vectors), 'orbital_elements': list}
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
        Compare orbital elements between TLE and RK45 propagation or between multiple RK45 propagations
        with different perturbation settings.
        
        Args:
            tle_line1 (str, optional): First line of TLE
            tle_line2 (str, optional): Second line of TLE
            tdm_wildcard (str, optional): Wildcard pattern for TDM files
            delta (float): Delta parameter for TDM parsing (default: 100)
            delta_error (float): Delta error parameter for TDM parsing (default: 30)
            time_span_hours (float): Time span for propagation in hours (default: 24)
            step_minutes (float): Time step in minutes (default: 5)
            time_offset_minutes (float): Time offset between TLE and observations in minutes (default: 28.5)
            r_init (array, optional): Initial position vector [x, y, z] in km
            v_init (array, optional): Initial velocity vector [vx, vy, vz] in km/s
            jd_init (float, optional): Initial Julian date
            perturbations_list (list): List of perturbation dictionaries for different RK45 propagations
                                      [{'j2': bool, 'third_body': bool, 'solar_radiation': bool, 'atmospheric_drag': bool}, ...]
            show_plot (bool): Whether to show the plots (default: True)
            save_path (str, optional): Base path to save the plots, if None the plots are not saved
        
        Returns:
            dict: Dictionary containing statistics of the comparisons
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
        # Step 6: Plotting
        # ---------------------------
        if show_plot or save_path:
            # Time array for plotting (hours from start)
            plot_times = np.arange(len(epochs)) * step_minutes / 60.0
            
            # Plot orbital elements for all trajectories
            element_names = ['Semi-major axis (a)', 'Eccentricity (e)', 'Inclination (i)',
                             'RAAN (Ω)', 'Argument of Perigee (ω)', 'Mean Anomaly (M)']
            
            fig, axs = plt.subplots(3, 2, figsize=(16, 12))
            for traj_idx, traj in enumerate(trajectories):
                for i, (name, ax) in enumerate(zip(element_names, axs.flat)):
                    ax.plot(plot_times, traj['orbital_elements'][:, i], label=labels[traj_idx])
                    ax.set_title(name)
                    ax.set_xlabel('Time (hours)')
                    ax.grid(True)
                    ax.legend()
            
            plt.tight_layout()
            if save_path:
                plt.savefig(f"{save_path}_orbital_elements.png")
            if show_plot:
                plt.show()
            
            # Plot position differences if we have reference trajectory
            if len(trajectories) > 1:
                fig, axs = plt.subplots(len(trajectories)-1, 2, figsize=(16, 4*(len(trajectories)-1)))
                
                # If there's only one comparison, axs won't be a 2D array
                if len(trajectories) == 2:
                    axs = np.array([axs])
                
                for traj_idx in range(1, len(trajectories)):
                    traj = trajectories[traj_idx]
                    
                    # First subplot: Position magnitude difference
                    ax = axs[traj_idx-1, 0]
                    ax.plot(plot_times, traj['position_diffs'][:, 3])
                    ax.set_title(f"Position Difference: {labels[0]} vs {labels[traj_idx]}")
                    ax.set_xlabel('Time (hours)')
                    ax.set_ylabel('Distance (km)')
                    ax.grid(True)
                    
                    # Second subplot: Semi-major axis difference
                    ax = axs[traj_idx-1, 1]
                    ax.plot(plot_times, traj['element_diffs'][:, 0])
                    ax.set_title(f"Semi-major axis Difference: {labels[0]} vs {labels[traj_idx]}")
                    ax.set_xlabel('Time (hours)')
                    ax.set_ylabel('Difference (km)')
                    ax.grid(True)
                
                plt.tight_layout()
                if save_path:
                    plt.savefig(f"{save_path}_differences.png")
                if show_plot:
                    plt.show()
        
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
        Set perturbation parameters
        
        Args:
            params (dict): Dictionary of perturbation parameters
                          {'CR': float, 'Am': float, 'CD': float, ...}
                          
        Returns:
            bool: True if successful, False otherwise
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
        Get current perturbation parameters
        
        Returns:
            dict: Dictionary of perturbation parameters
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
    Bridge class for Java-Python interface for the Orbit Toolkit.
    
    This class provides a clean, standardized interface for Java code to interact with
    the Orbit Toolkit Python code. It handles serialization, error handling, and 
    provides status updates for long-running operations.
    """
    
    def __init__(self):
        """Initialize the Java bridge with visualization and propagation tools"""
        self.visualizer = OrbitVisualizer()
        self.propagator = OrbitPropagator()
        self.status_callback = None
        
    def set_status_callback(self, callback_func):
        """
        Set a callback function to receive status updates
        
        Args:
            callback_func: A function that accepts (progress_percent, status_message)
        """
        self.status_callback = callback_func
        
    def _update_status(self, progress, message):
        """Internal method to update status if callback is registered"""
        if self.status_callback:
            try:
                self.status_callback(progress, message)
            except Exception as e:
                print(f"Error in status callback: {e}")
    
    def execute_command(self, command_json):
        """
        Execute a command from the Java GUI
        
        Args:
            command_json (str): JSON string containing the command and parameters
            
        Returns:
            str: JSON string with results
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
    
    def _create_success_response(self, data):
        """Create a standardized success response"""
        return json.dumps({
            'status': 'success',
            'data': data
        })
    
    def _create_error_response(self, message, error_code=None):
        """Create a standardized error response"""
        response = {
            'status': 'error',
            'message': message
        }
        if error_code:
            response['error_code'] = error_code
        return json.dumps(response)
    
    def _convert_to_serializable(self, obj):
        """Convert numpy arrays, lists, and other objects to JSON-serializable formats"""
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
        """Handle visualize_tle command"""
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
        """Handle visualize_rk45 command"""
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
        """Handle compare_orbits command"""
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
        """Handle propagate_tle command"""
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
        """Handle propagate_rk45 command"""
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
        """Handle compare_orbital_elements command"""
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
        """Handle set_perturbation_params command"""
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
        """Handle get_perturbation_params command"""
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

    # Additional methods for direct (non-JSON) access from Java bridge libraries

    def get_version(self):
        """Return version information about the toolkit"""
        return {
            'name': 'Orbit Toolkit',
            'version': '1.0.0',
            'python_interface': 'JavaBridge 1.0'
        }
    
    def shutdown(self):
        """Perform any necessary cleanup before shutting down"""
        # Add any cleanup code here if needed
        plt.close('all')  # Close all matplotlib figures
        self._update_status(100, "Bridge shutdown complete")
        return True


# Example usage of the Orbit Toolkit
if __name__ == "__main__":
    # Example TLE for Jason-3
    line1 = "1 41240U 16002A   24078.54273252 -.00000041  00000-0  87212-4 0  9991"
    line2 = "2 41240  66.0433  39.6041 0008216 275.2526  84.7552 12.80929447381890"
    tdm_data = "data/Jason/20240318_16002A_A*"
    
    print("==== Orbit Toolkit Example Usage ====")
    
    # Create visualizer
    visualizer = OrbitVisualizer()
    
#    print("\n1. Basic TLE Visualization")

#    # Visualize TLE orbit
#    fig, ax, positions = visualizer.visualize_tle(
#        line1, line2,
#        time_span_hours=6,
#        step_minutes=0.5,
#        show_plot=True
#    )
    
    print("\n2. RK45 Propagation Example")
    
    # Set perturbation flags
    perturbations = {
        'j2': True,              # J2 perturbation (Earth oblateness)
        'third_body': True,      # Third-body perturbations (Moon, Sun)
        'solar_radiation': True, # Solar radiation pressure
        'atmospheric_drag': True # Atmospheric drag
    }
    
#     # Visualize RK45 orbit
#    fig, ax, positions = visualizer.visualize_rk45(
#        tdm_wildcard=tdm_data,
#        delta=130,
#        delta_error=5,
#        time_span_hours=6,
#        perturbations=perturbations,
#        step_minutes=0.5,
#        show_plot=True
#    )
    
#    print("\n3. Orbit Comparison Example")
#    
#    perturbations_list = [
#        {'j2': True, 'third_body': False, 'solar_radiation': False, 'atmospheric_drag': False},
#        {'j2': True, 'third_body': True, 'solar_radiation': False, 'atmospheric_drag': False},
#        {'j2': True, 'third_body': True, 'solar_radiation': True, 'atmospheric_drag': False},
#        {'j2': True, 'third_body': True, 'solar_radiation': True, 'atmospheric_drag': True}
#    ]
#    
#    # Compare TLE and RK45 orbits
#    fig, ax, tle_pos, rk45_pos_list = visualizer.compare_orbits(
#        line1, line2,
#        tdm_wildcard=tdm_data,
#        delta=130,
#        delta_error=5,
#        time_span_hours=24,
#        step_minutes=1.0,
#        perturbations_list=perturbations_list,
#        show_plot=True
#    )
    
    print("\n4.1 Orbital Elements Comparison Example with statistics")
    
    # Create propagator
    propagator = OrbitPropagator()
    
#    # Compare TLE with multiple RK45 propagations with different perturbations
#    stats = propagator.compare_orbital_elements(
#        tle_line1=line1,
#        tle_line2=line2,
#        tdm_wildcard=tdm_data,
#        time_span_hours=12,
#        perturbations_list=[
#            {'j2': True, 'third_body': False, 'solar_radiation': False, 'atmospheric_drag': False},
#            {'j2': True, 'third_body': True, 'solar_radiation': True, 'atmospheric_drag': True}
#        ]
#    )
#
#    # Print statistics
#    for comparison, values in stats.items():
#        print(f"Comparison: {comparison}")
#        print(f"Mean position difference: {values['mean_position_diff']:.3f} km")
#        print(f"Max position difference: {values['max_position_diff']:.3f} km")
#        print(f"Mean semi-major axis difference: {values['mean_semi_major_diff']:.6f} km")
#
    print("\n4.2 TLE Propagation Example")
#
#    # Propagate TLE orbit
#    tle_results = propagator.propagate_tle(
#        line1, line2,
#        time_span_hours=6,
#        step_minutes=0.5
#    )
#    
#    # Print orbital elements at the beginning and end
#    print("Initial orbital elements:")
#    print(f"  Semi-major axis: {tle_results['orbital_elements'][0]['a']:.2f} km")
#    print(f"  Eccentricity: {tle_results['orbital_elements'][0]['e']:.6f}")
#    print(f"  Inclination: {np.degrees(tle_results['orbital_elements'][0]['i']):.2f} deg")
#    
#    print("Final orbital elements:")
#    print(f"  Semi-major axis: {tle_results['orbital_elements'][-1]['a']:.2f} km")
#    print(f"  Eccentricity: {tle_results['orbital_elements'][-1]['e']:.6f}")
#    print(f"  Inclination: {np.degrees(tle_results['orbital_elements'][-1]['i']):.2f} deg")
#    
#    print("\n5. RK45 Propagation with Different Perturbation Models")
#    
#    # Set perturbation parameters
#    propagator.set_perturbation_parameters({
#        'CR': 1.8,     # Radiation pressure coefficient
#        'Am': 0.01,    # Area-to-mass ratio (m²/kg)
#        'CD': 2.2      # Drag coefficient
#    })
#    
#    # Define custom perturbation configurations (optional)
#    # You can customize this based on what you want to compare
#    custom_configs = [
#        {'j2': True, 'third_body': False, 'solar_radiation': False, 'atmospheric_drag': False,
#         'name': 'J2 only', 'color': 'green'},
#        {'j2': True, 'third_body': False, 'solar_radiation': True, 'atmospheric_drag': False,
#         'name': 'J2 + SRP', 'color': 'orange'},
#        {'j2': True, 'third_body': False, 'solar_radiation': False, 'atmospheric_drag': True,
#         'name': 'J2 + Drag', 'color': 'red'},
#    ]
#    
#    # Compare different perturbation models visually
#    fig, ax, tle_pos, rk45_pos_list = visualizer.compare_orbits(
#        line1, line2,
#        tdm_wildcard=tdm_data,
#        delta=130,
#        delta_error=5,
#        time_span_hours=6,
#        step_minutes=0.5,
#        perturbations_list=custom_configs,  # Use custom configs
#        show_plot=True,
#        save_path="perturbation_comparison.png"
#    )
#
#    print("\nComparison completed. Results saved to 'perturbation_comparison.png'")
#
    print("\n7. Analyzing Orbit Evolution By Hand")
#
#    # Propagate for longer duration to see orbital element evolution
#    tle_results = propagator.propagate_tle(
#        line1, line2,
#        time_span_hours=24,
#        step_minutes=30.0
#    )
#
#    # Extract orbital elements evolution
#    times = np.array(tle_results['epochs'])
#    times = (times - times[0]) * 24.0  # Convert to hours from start
#    
#    semi_major_axis = np.array([oe['a'] for oe in tle_results['orbital_elements']])
#    eccentricity = np.array([oe['e'] for oe in tle_results['orbital_elements']])
#    inclination = np.array([np.degrees(oe['i']) for oe in tle_results['orbital_elements']])
#    raan = np.array([np.degrees(oe['raan']) for oe in tle_results['orbital_elements']])
#    
#    # Plot orbital element evolution
#    plt.figure(figsize=(12, 10))
#    
#    # Semi-major axis
#    plt.subplot(2, 2, 1)
#    plt.plot(times, semi_major_axis)
#    plt.xlabel('Time (hours)')
#    plt.ylabel('Semi-major axis (km)')
#    plt.title('Semi-major axis evolution')
#    plt.grid(True)
#    
#    # Eccentricity
#    plt.subplot(2, 2, 2)
#    plt.plot(times, eccentricity)
#    plt.xlabel('Time (hours)')
#    plt.ylabel('Eccentricity')
#    plt.title('Eccentricity evolution')
#    plt.grid(True)
#    
#    # Inclination
#    plt.subplot(2, 2, 3)
#    plt.plot(times, inclination)
#    plt.xlabel('Time (hours)')
#    plt.ylabel('Inclination (deg)')
#    plt.title('Inclination evolution')
#    plt.grid(True)
#    
#    # RAAN
#    plt.subplot(2, 2, 4)
#    plt.plot(times, raan)
#    plt.xlabel('Time (hours)')
#    plt.ylabel('RAAN (deg)')
#    plt.title('RAAN evolution')
#    plt.grid(True)
#    
#    plt.tight_layout()
#    plt.savefig('orbital_elements_evolution.png')
#    plt.show()
#    
#    print("\nExamples completed. Results saved to 'jason3_orbit.png' and 'orbital_elements_evolution.png'")
