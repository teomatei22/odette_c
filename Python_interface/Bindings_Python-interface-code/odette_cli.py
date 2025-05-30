#!/usr/bin/env python3.8
"""
ODETTE Interactive CLI Interface
High-level text-based interface for orbit visualization and propagation
"""

import sys
import os
import json
import glob
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

# Import your ODETTE modules
try:
    from orbit_toolkit import OrbitVisualizer, OrbitPropagator
except ImportError:
    print("Error: Could not import ODETTE modules. Make sure orbit_toolkit.py is in the Python path.")
    sys.exit(1)


class ODETTEInterface:
    """Interactive CLI interface for ODETTE orbit toolkit"""
    
    def __init__(self):
        self.visualizer = OrbitVisualizer()
        self.propagator = OrbitPropagator()
        self.running = True
        self.config = self.load_default_config()
        
    def load_default_config(self):
        """Load default configuration parameters"""
        return {
            'time_span_hours': 6.0,
            'step_minutes': 0.5,
            'perturbations': {
                'j2': True,
                'third_body': False,
                'solar_radiation': False,
                'atmospheric_drag': False
            },
            'tdm_params': {
                'delta': 100.0,
                'delta_error': 30.0
            },
            'visualization': {
                'show_plot': True,
                'save_plots': False,
                'save_path': './plots/'
            }
        }
    
    def print_banner(self):
        """Print welcome banner"""
        print("=" * 70)
        print("         ODETTE - Orbit DETermination TEchnology")
        print("           Interactive Command Line Interface")
        print("=" * 70)
        print()
    
    def print_main_menu(self):
        """Print the main menu options"""
        print("\n" + "=" * 50)
        print("MAIN MENU")
        print("=" * 50)
        print("1.  TLE Operations")
        print("2.  RK45 Propagation")
        print("3.  Orbit Comparison")
        print("4.  Multiple Satellites")
        print("5.  Configuration")
        print("6.  Utilities")
        print("7.  Help")
        print("8.  Exit")
        print("-" * 50)
    
    def get_user_input(self, prompt, input_type=str, default=None, choices=None):
        """Get validated user input"""
        while True:
            try:
                if default is not None:
                    user_input = input(f"{prompt} [default: {default}]: ").strip()
                    if not user_input:
                        return default
                else:
                    user_input = input(f"{prompt}: ").strip()
                
                # Convert input to the desired type first
                if input_type == bool:
                    converted_input = user_input.lower() in ['y', 'yes', 'true', '1']
                elif input_type == float:
                    converted_input = float(user_input)
                elif input_type == int:
                    converted_input = int(user_input)
                else:
                    converted_input = user_input
                
                # Then check against choices if provided
                if choices and converted_input not in choices:
                    print(f"Invalid choice. Please select from: {choices}")
                    continue
                
                return converted_input
                    
            except ValueError:
                print(f"Invalid input. Please enter a valid {input_type.__name__}.")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return None
    
    def tle_operations_menu(self):
        """Handle TLE operations"""
        print("\n" + "=" * 40)
        print("TLE OPERATIONS")
        print("=" * 40)
        print("1. Visualize TLE orbit")
        print("2. Propagate TLE orbit")
        print("3. Load TLE from file")
        print("4. Enter TLE manually")
        print("5. Back to main menu")
        
        choice = self.get_user_input("Select option", int, choices=[1, 2, 3, 4, 5])
        if choice is None:
            return
            
        if choice == 1:
            self.visualize_tle()
        elif choice == 2:
            self.propagate_tle()
        elif choice == 3:
            self.load_tle_from_file()
        elif choice == 4:
            self.enter_tle_manually()
        elif choice == 5:
            return
    
    def visualize_tle(self):
        """Visualize TLE orbit"""
        print("\n--- TLE Orbit Visualization ---")
        
        # Get TLE data
        tle_line1, tle_line2 = self.get_tle_input()
        if not tle_line1 or not tle_line2:
            return
        
        # Get parameters
        time_span = self.get_user_input("Time span (hours)", float, self.config['time_span_hours'])
        step_minutes = self.get_user_input("Time step (minutes)", float, self.config['step_minutes'])
        
        # Visualization options
        show_plot = self.get_user_input("Show plot? (y/n)", bool, self.config['visualization']['show_plot'])
        save_plot = self.get_user_input("Save plot? (y/n)", bool, self.config['visualization']['save_plots'])
        
        save_path = None
        if save_plot:
            save_path = self.get_user_input("Save path", str, f"{self.config['visualization']['save_path']}tle_orbit.png")
        
        print("\nProcessing TLE visualization...")
        try:
            fig, ax, positions = self.visualizer.visualize_tle(
                tle_line1, tle_line2,
                time_span_hours=time_span,
                step_minutes=step_minutes,
                show_plot=show_plot,
                save_path=save_path
            )
            
            if positions is not None:
                print(f"✓ Successfully visualized orbit with {len(positions)} points")
                if save_path:
                    print(f"✓ Plot saved to: {save_path}")
            else:
                print("✗ Visualization failed")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def propagate_tle(self):
        """Propagate TLE orbit and show results"""
        print("\n--- TLE Orbit Propagation ---")
        
        # Get TLE data
        tle_line1, tle_line2 = self.get_tle_input()
        if not tle_line1 or not tle_line2:
            return
        
        # Get parameters
        time_span = self.get_user_input("Time span (hours)", float, self.config['time_span_hours'])
        step_minutes = self.get_user_input("Time step (minutes)", float, self.config['step_minutes'])
        return_vectors = self.get_user_input("Return position/velocity vectors? (y/n)", bool, True)
        
        print("\nPropagating TLE orbit...")
        try:
            results = self.propagator.propagate_tle(
                tle_line1, tle_line2,
                time_span_hours=time_span,
                step_minutes=step_minutes,
                return_vectors=return_vectors
            )
            
            if results:
                print(f"✓ Propagation completed with {len(results['epochs'])} points")
                self.display_orbital_elements_summary(results['orbital_elements'])
                
                # Option to save results
                save_results = self.get_user_input("Save results to JSON? (y/n)", bool, False)
                if save_results:
                    filename = self.get_user_input("Filename", str, "tle_propagation_results.json")
                    self.save_results_to_json(results, filename)
            else:
                print("✗ Propagation failed")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def rk45_operations_menu(self):
        """Handle RK45 operations"""
        print("\n" + "=" * 40)
        print("RK45 PROPAGATION")
        print("=" * 40)
        print("1. Visualize RK45 orbit")
        print("2. Propagate RK45 orbit")
        print("3. Configure perturbations")
        print("4. Set perturbation parameters")
        print("5. Back to main menu")
        
        choice = self.get_user_input("Select option", int, choices=[1, 2, 3, 4, 5])
        if choice is None:
            return
            
        if choice == 1:
            self.visualize_rk45()
        elif choice == 2:
            self.propagate_rk45()
        elif choice == 3:
            self.configure_perturbations()
        elif choice == 4:
            self.set_perturbation_parameters()
        elif choice == 5:
            return
    
    def visualize_rk45(self):
        """Visualize RK45 orbit"""
        print("\n--- RK45 Orbit Visualization ---")
        
        # Get TDM file pattern
        tdm_wildcard = self.get_user_input("TDM file wildcard pattern", str, "*.tdm")
        
        # Validate files exist
        if not glob.glob(tdm_wildcard):
            print(f"✗ No files found matching pattern: {tdm_wildcard}")
            return
        
        # Get TDM parameters
        delta = self.get_user_input("Delta parameter", float, self.config['tdm_params']['delta'])
        delta_error = self.get_user_input("Delta error parameter", float, self.config['tdm_params']['delta_error'])
        
        # Get time parameters
        time_span = self.get_user_input("Time span (hours)", float, self.config['time_span_hours'])
        step_minutes = self.get_user_input("Time step (minutes)", float, self.config['step_minutes'])
        
        # Show current perturbations
        print(f"\nCurrent perturbations: {self.config['perturbations']}")
        use_current = self.get_user_input("Use current perturbation settings? (y/n)", bool, True)
        
        perturbations = self.config['perturbations'] if use_current else self.configure_perturbations_interactive()
        
        # Visualization options
        show_plot = self.get_user_input("Show plot? (y/n)", bool, self.config['visualization']['show_plot'])
        save_plot = self.get_user_input("Save plot? (y/n)", bool, self.config['visualization']['save_plots'])
        
        save_path = None
        if save_plot:
            save_path = self.get_user_input("Save path", str, f"{self.config['visualization']['save_path']}rk45_orbit.png")
        
        print("\nProcessing RK45 visualization...")
        try:
            fig, ax, positions = self.visualizer.visualize_rk45(
                tdm_wildcard, delta, delta_error,
                time_span_hours=time_span,
                step_minutes=step_minutes,
                perturbations=perturbations,
                show_plot=show_plot,
                save_path=save_path
            )
            
            if positions is not None:
                print(f"✓ Successfully visualized orbit with {len(positions)} points")
                if save_path:
                    print(f"✓ Plot saved to: {save_path}")
            else:
                print("✗ Visualization failed")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def propagate_rk45(self):
        """Propagate RK45 orbit and show results"""
        print("\n--- RK45 Orbit Propagation ---")
        
        # Get TDM file pattern
        tdm_wildcard = self.get_user_input("TDM file wildcard pattern", str, "*.tdm")
        
        # Validate files exist
        if not glob.glob(tdm_wildcard):
            print(f"✗ No files found matching pattern: {tdm_wildcard}")
            return
        
        # Get parameters
        delta = self.get_user_input("Delta parameter", float, self.config['tdm_params']['delta'])
        delta_error = self.get_user_input("Delta error parameter", float, self.config['tdm_params']['delta_error'])
        time_span = self.get_user_input("Time span (hours)", float, self.config['time_span_hours'])
        step_minutes = self.get_user_input("Time step (minutes)", float, self.config['step_minutes'])
        return_vectors = self.get_user_input("Return position/velocity vectors? (y/n)", bool, True)
        
        # Show current perturbations
        print(f"\nCurrent perturbations: {self.config['perturbations']}")
        use_current = self.get_user_input("Use current perturbation settings? (y/n)", bool, True)
        
        perturbations = self.config['perturbations'] if use_current else self.configure_perturbations_interactive()
        
        print("\nPropagating RK45 orbit...")
        try:
            results = self.propagator.propagate_rk45(
                tdm_wildcard, delta, delta_error,
                time_span_hours=time_span,
                step_minutes=step_minutes,
                perturbations=perturbations,
                return_vectors=return_vectors
            )
            
            if results:
                print(f"✓ Propagation completed with {len(results['epochs'])} points")
                self.display_orbital_elements_summary(results['orbital_elements'])
                
                # Option to save results
                save_results = self.get_user_input("Save results to JSON? (y/n)", bool, False)
                if save_results:
                    filename = self.get_user_input("Filename", str, "rk45_propagation_results.json")
                    self.save_results_to_json(results, filename)
            else:
                print("✗ Propagation failed")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def orbit_comparison_menu(self):
        """Handle orbit comparison operations"""
        print("\n" + "=" * 40)
        print("ORBIT COMPARISON")
        print("=" * 40)
        print("1. Compare TLE vs RK45")
        print("2. Compare multiple RK45 configurations")
        print("3. Compare orbital elements")
        print("4. Back to main menu")
        
        choice = self.get_user_input("Select option", int, choices=[1, 2, 3, 4])
        if choice is None:
            return
            
        if choice == 1:
            self.compare_tle_vs_rk45()
        elif choice == 2:
            self.compare_multiple_rk45()
        elif choice == 3:
            self.compare_orbital_elements()
        elif choice == 4:
            return
    
    def compare_tle_vs_rk45(self):
        """Compare TLE and RK45 propagation"""
        print("\n--- TLE vs RK45 Comparison ---")
        
        # Get TLE data
        tle_line1, tle_line2 = self.get_tle_input()
        if not tle_line1 or not tle_line2:
            return
        
        # Get TDM file pattern
        tdm_wildcard = self.get_user_input("TDM file wildcard pattern", str, "*.tdm")
        
        # Validate files exist
        if not glob.glob(tdm_wildcard):
            print(f"✗ No files found matching pattern: {tdm_wildcard}")
            return
        
        # Get parameters
        delta = self.get_user_input("Delta parameter", float, self.config['tdm_params']['delta'])
        delta_error = self.get_user_input("Delta error parameter", float, self.config['tdm_params']['delta_error'])
        time_span = self.get_user_input("Time span (hours)", float, self.config['time_span_hours'])
        step_minutes = self.get_user_input("Time step (minutes)", float, self.config['step_minutes'])
        
        # Configure perturbations for RK45
        print(f"\nCurrent perturbations: {self.config['perturbations']}")
        use_current = self.get_user_input("Use current perturbation settings? (y/n)", bool, True)
        
        if use_current:
            perturbations_list = [self.config['perturbations']]
        else:
            perturbations_list = self.configure_multiple_perturbations()
        
        # Visualization options
        show_plot = self.get_user_input("Show plot? (y/n)", bool, self.config['visualization']['show_plot'])
        save_plot = self.get_user_input("Save plot? (y/n)", bool, self.config['visualization']['save_plots'])
        
        save_path = None
        if save_plot:
            save_path = self.get_user_input("Save path", str, f"{self.config['visualization']['save_path']}comparison.png")
        
        print("\nProcessing comparison...")
        try:
            fig, ax, tle_positions, rk_positions = self.visualizer.compare_orbits(
                tle_line1, tle_line2, tdm_wildcard, delta, delta_error,
                time_span_hours=time_span,
                step_minutes=step_minutes,
                perturbations_list=perturbations_list,
                show_plot=show_plot,
                save_path=save_path
            )
            
            if tle_positions is not None and rk_positions is not None:
                print(f"✓ Successfully compared orbits")
                print(f"  TLE points: {len(tle_positions)}")
                print(f"  RK45 points: {len(rk_positions)}")
                if save_path:
                    print(f"✓ Plot saved to: {save_path}")
            else:
                print("✗ Comparison failed")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def compare_multiple_rk45(self):
        """Compare multiple RK45 configurations"""
        print("\n--- Multiple RK45 Comparison ---")
        
        # Get TDM file pattern
        tdm_wildcard = self.get_user_input("TDM file wildcard pattern", str, "*.tdm")
        
        # Validate files exist
        if not glob.glob(tdm_wildcard):
            print(f"✗ No files found matching pattern: {tdm_wildcard}")
            return
        
        # Get parameters
        delta = self.get_user_input("Delta parameter", float, self.config['tdm_params']['delta'])
        delta_error = self.get_user_input("Delta error parameter", float, self.config['tdm_params']['delta_error'])
        time_span = self.get_user_input("Time span (hours)", float, self.config['time_span_hours'])
        step_minutes = self.get_user_input("Time step (minutes)", float, self.config['step_minutes'])
        
        # Configure multiple perturbations
        perturbations_list = self.configure_multiple_perturbations()
        
        # Visualization options
        show_plot = self.get_user_input("Show plot? (y/n)", bool, self.config['visualization']['show_plot'])
        save_plot = self.get_user_input("Save plot? (y/n)", bool, self.config['visualization']['save_plots'])
        
        save_path = None
        if save_plot:
            save_path = self.get_user_input("Save path", str, f"{self.config['visualization']['save_path']}rk45_comparison.png")
        
        print("\nProcessing RK45 comparison...")
        try:
            # Use visualizer to compare multiple RK45 configurations
            fig, ax, all_positions = self.visualizer.compare_multiple_rk45(
                tdm_wildcard, delta, delta_error,
                time_span_hours=time_span,
                step_minutes=step_minutes,
                perturbations_list=perturbations_list,
                show_plot=show_plot,
                save_path=save_path
            )
            
            if all_positions:
                print(f"✓ Successfully compared {len(all_positions)} RK45 configurations")
                for i, positions in enumerate(all_positions):
                    print(f"  Config {i+1}: {len(positions)} points")
                if save_path:
                    print(f"✓ Plot saved to: {save_path}")
            else:
                print("✗ Comparison failed")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def compare_orbital_elements(self):
        """Compare orbital elements between different propagation methods"""
        print("\n--- Orbital Elements Comparison ---")
        
        print("This will compare orbital elements evolution over time.")
        print("You can compare TLE vs RK45 or multiple RK45 configurations.")
        
        # Get comparison type
        print("\n1. TLE vs RK45")
        print("2. Multiple RK45 configurations only")
        comp_type = self.get_user_input("Comparison type", int, choices=[1, 2])
        
        if comp_type == 1:
            # TLE vs RK45 comparison
            tle_line1, tle_line2 = self.get_tle_input()
            if not tle_line1 or not tle_line2:
                return
        else:
            tle_line1 = tle_line2 = None
        
        # Get TDM file pattern
        tdm_wildcard = self.get_user_input("TDM file wildcard pattern", str, "*.tdm")
        
        # Validate files exist
        if not glob.glob(tdm_wildcard):
            print(f"✗ No files found matching pattern: {tdm_wildcard}")
            return
        
        # Get parameters
        delta = self.get_user_input("Delta parameter", float, self.config['tdm_params']['delta'])
        delta_error = self.get_user_input("Delta error parameter", float, self.config['tdm_params']['delta_error'])
        time_span = self.get_user_input("Time span (hours)", float, 24.0)
        step_minutes = self.get_user_input("Time step (minutes)", float, 5.0)
        
        # Configure perturbations
        perturbations_list = self.configure_multiple_perturbations()
        
        # Visualization options
        show_plot = self.get_user_input("Show plots? (y/n)", bool, True)
        save_plot = self.get_user_input("Save plots? (y/n)", bool, False)
        
        save_path = None
        if save_plot:
            save_path = self.get_user_input("Save path base", str, f"{self.config['visualization']['save_path']}orbital_elements")
        
        print("\nProcessing orbital elements comparison...")
        try:
            stats = self.propagator.compare_orbital_elements(
                tle_line1=tle_line1,
                tle_line2=tle_line2,
                tdm_wildcard=tdm_wildcard,
                delta=delta,
                delta_error=delta_error,
                time_span_hours=time_span,
                step_minutes=step_minutes,
                perturbations_list=perturbations_list,
                show_plot=show_plot,
                save_path=save_path
            )
            
            if stats:
                print(f"✓ Successfully compared orbital elements")
                self.display_comparison_statistics(stats)
                if save_path:
                    print(f"✓ Plots saved with base path: {save_path}")
            else:
                print("✗ Comparison failed")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def multiple_satellites_menu(self):
        """Handle multiple satellites visualization"""
        print("\n--- Multiple Satellites Visualization ---")
        
        satellites_data = []
        
        while True:
            print(f"\nCurrently configured satellites: {len(satellites_data)}")
            print("1. Add TLE satellite")
            print("2. Add RK45 satellite")
            print("3. Remove satellite")
            print("4. List satellites")
            print("5. Visualize all satellites")
            print("6. Back to main menu")
            
            choice = self.get_user_input("Select option", int, choices=[1, 2, 3, 4, 5, 6])
            if choice is None:
                continue
                
            if choice == 1:
                self.add_tle_satellite(satellites_data)
            elif choice == 2:
                self.add_rk45_satellite(satellites_data)
            elif choice == 3:
                self.remove_satellite(satellites_data)
            elif choice == 4:
                self.list_satellites(satellites_data)
            elif choice == 5:
                if satellites_data:
                    self.visualize_multiple_satellites(satellites_data)
                else:
                    print("No satellites configured.")
            elif choice == 6:
                break
    
    def add_tle_satellite(self, satellites_data):
        """Add a TLE satellite to the list"""
        print("\n--- Add TLE Satellite ---")
        
        name = self.get_user_input("Satellite name", str, f"TLE_Satellite_{len(satellites_data)+1}")
        tle_line1, tle_line2 = self.get_tle_input()
        
        if tle_line1 and tle_line2:
            satellite = {
                'name': name,
                'type': 'TLE',
                'tle_line1': tle_line1,
                'tle_line2': tle_line2
            }
            satellites_data.append(satellite)
            print(f"✓ Added TLE satellite: {name}")
        else:
            print("✗ Failed to add satellite")
    
    def add_rk45_satellite(self, satellites_data):
        """Add an RK45 satellite to the list"""
        print("\n--- Add RK45 Satellite ---")
        
        name = self.get_user_input("Satellite name", str, f"RK45_Satellite_{len(satellites_data)+1}")
        tdm_wildcard = self.get_user_input("TDM file wildcard pattern", str, "*.tdm")
        
        if not glob.glob(tdm_wildcard):
            print(f"✗ No files found matching pattern: {tdm_wildcard}")
            return
        
        delta = self.get_user_input("Delta parameter", float, self.config['tdm_params']['delta'])
        delta_error = self.get_user_input("Delta error parameter", float, self.config['tdm_params']['delta_error'])
        
        print(f"\nCurrent perturbations: {self.config['perturbations']}")
        use_current = self.get_user_input("Use current perturbation settings? (y/n)", bool, True)
        
        perturbations = self.config['perturbations'] if use_current else self.configure_perturbations_interactive()
        
        satellite = {
            'name': name,
            'type': 'RK45',
            'tdm_wildcard': tdm_wildcard,
            'delta': delta,
            'delta_error': delta_error,
            'perturbations': perturbations
        }
        satellites_data.append(satellite)
        print(f"✓ Added RK45 satellite: {name}")
    
    def remove_satellite(self, satellites_data):
        """Remove a satellite from the list"""
        if not satellites_data:
            print("No satellites to remove.")
            return
            
        print("\n--- Remove Satellite ---")
        self.list_satellites(satellites_data)
        
        index = self.get_user_input("Enter satellite number to remove", int)
        if index is None:
            return
            
        if 1 <= index <= len(satellites_data):
            removed = satellites_data.pop(index - 1)
            print(f"✓ Removed satellite: {removed['name']}")
        else:
            print("Invalid satellite number.")
    
    def list_satellites(self, satellites_data):
        """List all configured satellites"""
        if not satellites_data:
            print("No satellites configured.")
            return
            
        print("\n--- Configured Satellites ---")
        for i, sat in enumerate(satellites_data, 1):
            print(f"{i}. {sat['name']} ({sat['type']})")
            if sat['type'] == 'TLE':
                print(f"   TLE Line 1: {sat['tle_line1'][:50]}...")
                print(f"   TLE Line 2: {sat['tle_line2'][:50]}...")
            else:
                print(f"   TDM Pattern: {sat['tdm_wildcard']}")
                print(f"   Perturbations: {sat['perturbations']}")
    
    def visualize_multiple_satellites(self, satellites_data):
        """Visualize all configured satellites"""
        print("\n--- Visualizing Multiple Satellites ---")
        
        # Get time parameters
        time_span = self.get_user_input("Time span (hours)", float, self.config['time_span_hours'])
        step_minutes = self.get_user_input("Time step (minutes)", float, self.config['step_minutes'])
        
        # Visualization options
        show_plot = self.get_user_input("Show plot? (y/n)", bool, self.config['visualization']['show_plot'])
        save_plot = self.get_user_input("Save plot? (y/n)", bool, self.config['visualization']['save_plots'])
        
        save_path = None
        if save_plot:
            save_path = self.get_user_input("Save path", str, f"{self.config['visualization']['save_path']}multiple_satellites.png")
        
        print("\nProcessing multiple satellite visualization...")
        try:
            fig, ax = self.visualizer.visualize_multiple_satellites(
                satellites_data,
                time_span_hours=time_span,
                step_minutes=step_minutes,
                show_plot=show_plot,
                save_path=save_path
            )
            
            print(f"✓ Successfully visualized {len(satellites_data)} satellites")
            if save_path:
                print(f"✓ Plot saved to: {save_path}")
                
        except Exception as e:
            print(f"✗ Error: {e}")

    def configuration_menu(self):
            """Handle configuration settings"""
            print("\n" + "=" * 40)
            print("CONFIGURATION")
            print("=" * 40)
            print("1. View current configuration")
            print("2. Set default time parameters")
            print("3. Configure default perturbations")
            print("4. Set TDM parameters")
            print("5. Set visualization settings")
            print("6. Save configuration")
            print("7. Load configuration")
            print("8. Reset to defaults")
            print("9. Back to main menu")
            
            choice = self.get_user_input("Select option", int, choices=[1, 2, 3, 4, 5, 6, 7, 8, 9])
            if choice is None:
                return
                
            if choice == 1:
                self.view_configuration()
            elif choice == 2:
                self.set_time_parameters()
            elif choice == 3:
                self.configure_perturbations()
            elif choice == 4:
                self.set_tdm_parameters()
            elif choice == 5:
                self.set_visualization_settings()
            elif choice == 6:
                self.save_configuration()
            elif choice == 7:
                self.load_configuration()
            elif choice == 8:
                self.reset_configuration()
            elif choice == 9:
                return
        
    def view_configuration(self):
        """Display current configuration"""
        print("\n--- Current Configuration ---")
        print(json.dumps(self.config, indent=2))
    
    def set_time_parameters(self):
        """Set default time parameters"""
        print("\n--- Time Parameters ---")
        
        time_span = self.get_user_input("Default time span (hours)", float, self.config['time_span_hours'])
        if time_span is not None:
            self.config['time_span_hours'] = time_span
        
        step_minutes = self.get_user_input("Default time step (minutes)", float, self.config['step_minutes'])
        if step_minutes is not None:
            self.config['step_minutes'] = step_minutes
        
        print("✓ Time parameters updated")
    
    def configure_perturbations(self):
        """Configure default perturbations"""
        print("\n--- Perturbation Settings ---")
        print(f"Current settings: {self.config['perturbations']}")
        
        j2 = self.get_user_input("J2 perturbation? (y/n)", bool, self.config['perturbations']['j2'])
        if j2 is not None:
            self.config['perturbations']['j2'] = j2
        
        third_body = self.get_user_input("Third body perturbation? (y/n)", bool, self.config['perturbations']['third_body'])
        if third_body is not None:
            self.config['perturbations']['third_body'] = third_body
        
        solar_radiation = self.get_user_input("Solar radiation pressure? (y/n)", bool, self.config['perturbations']['solar_radiation'])
        if solar_radiation is not None:
            self.config['perturbations']['solar_radiation'] = solar_radiation
        
        atmospheric_drag = self.get_user_input("Atmospheric drag? (y/n)", bool, self.config['perturbations']['atmospheric_drag'])
        if atmospheric_drag is not None:
            self.config['perturbations']['atmospheric_drag'] = atmospheric_drag
        
        print("✓ Perturbation settings updated")
        return self.config['perturbations']
    
    def configure_perturbations_interactive(self):
        """Configure perturbations interactively and return the settings"""
        print("\n--- Configure Perturbations ---")
        
        perturbations = {}
        
        perturbations['j2'] = self.get_user_input("J2 perturbation? (y/n)", bool, True)
        perturbations['third_body'] = self.get_user_input("Third body perturbation? (y/n)", bool, False)
        perturbations['solar_radiation'] = self.get_user_input("Solar radiation pressure? (y/n)", bool, False)
        perturbations['atmospheric_drag'] = self.get_user_input("Atmospheric drag? (y/n)", bool, False)
        
        return perturbations
    
    def configure_multiple_perturbations(self):
        """Configure multiple perturbation sets for comparison"""
        print("\n--- Configure Multiple Perturbation Sets ---")
        
        perturbations_list = []
        
        while True:
            print(f"\nConfiguring perturbation set #{len(perturbations_list) + 1}")
            
            perturbations = {}
            perturbations['j2'] = self.get_user_input("J2 perturbation? (y/n)", bool, True)
            perturbations['third_body'] = self.get_user_input("Third body perturbation? (y/n)", bool, False)
            perturbations['solar_radiation'] = self.get_user_input("Solar radiation pressure? (y/n)", bool, False)
            perturbations['atmospheric_drag'] = self.get_user_input("Atmospheric drag? (y/n)", bool, False)
            
            perturbations_list.append(perturbations)
            
            add_more = self.get_user_input("Add another perturbation set? (y/n)", bool, False)
            if not add_more or len(perturbations_list) >= 5:  # Limit to 5 sets
                break
        
        return perturbations_list
    
    def set_tdm_parameters(self):
        """Set TDM parsing parameters"""
        print("\n--- TDM Parameters ---")
        
        delta = self.get_user_input("Delta parameter", float, self.config['tdm_params']['delta'])
        if delta is not None:
            self.config['tdm_params']['delta'] = delta
        
        delta_error = self.get_user_input("Delta error parameter", float, self.config['tdm_params']['delta_error'])
        if delta_error is not None:
            self.config['tdm_params']['delta_error'] = delta_error
        
        print("✓ TDM parameters updated")
    
    def set_visualization_settings(self):
        """Set visualization settings"""
        print("\n--- Visualization Settings ---")
        
        show_plot = self.get_user_input("Show plots by default? (y/n)", bool, self.config['visualization']['show_plot'])
        if show_plot is not None:
            self.config['visualization']['show_plot'] = show_plot
        
        save_plots = self.get_user_input("Save plots by default? (y/n)", bool, self.config['visualization']['save_plots'])
        if save_plots is not None:
            self.config['visualization']['save_plots'] = save_plots
        
        save_path = self.get_user_input("Default save path", str, self.config['visualization']['save_path'])
        if save_path:
            self.config['visualization']['save_path'] = save_path
        
        print("✓ Visualization settings updated")
    
    def save_configuration(self):
        """Save configuration to file"""
        filename = self.get_user_input("Configuration filename", str, "odette_config.json")
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.config, f, indent=2)
                print(f"✓ Configuration saved to: {filename}")
            except Exception as e:
                print(f"✗ Error saving configuration: {e}")
    
    def load_configuration(self):
        """Load configuration from file"""
        filename = self.get_user_input("Configuration filename", str, "odette_config.json")
        if filename and os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    self.config = json.load(f)
                print(f"✓ Configuration loaded from: {filename}")
            except Exception as e:
                print(f"✗ Error loading configuration: {e}")
        else:
            print(f"✗ Configuration file not found: {filename}")
    
    def reset_configuration(self):
        """Reset configuration to defaults"""
        confirm = self.get_user_input("Reset all settings to defaults? (y/n)", bool, False)
        if confirm:
            self.config = self.load_default_config()
            print("✓ Configuration reset to defaults")
    
    def utilities_menu(self):
        """Handle utility functions"""
        print("\n" + "=" * 40)
        print("UTILITIES")
        print("=" * 40)
        print("1. Convert TLE to orbital elements")
        print("2. Calculate orbital period")
        print("3. Validate TLE format")
        print("4. List TDM files")
        print("5. Export results to CSV")
        print("6. Set perturbation parameters")
        print("7. View current perturbation parameters")
        print("8. Back to main menu")
        
        choice = self.get_user_input("Select option", int, choices=[1, 2, 3, 4, 5, 6, 7, 8])
        if choice is None:
            return
            
        if choice == 1:
            self.convert_tle_to_elements()
        elif choice == 2:
            self.calculate_orbital_period()
        elif choice == 3:
            self.validate_tle_format()
        elif choice == 4:
            self.list_tdm_files()
        elif choice == 5:
            self.export_results_csv()
        elif choice == 6:
            self.set_perturbation_parameters_interactive()
        elif choice == 7:
            self.view_perturbation_parameters()
        elif choice == 8:
            return
    
    def convert_tle_to_elements(self):
        """Convert TLE to orbital elements"""
        print("\n--- TLE to Orbital Elements ---")
        
        tle_line1, tle_line2 = self.get_tle_input()
        if not tle_line1 or not tle_line2:
            return
        
        try:
            results = self.propagator.propagate_tle(tle_line1, tle_line2, time_span_hours=0.1, step_minutes=0.1)
            if results and results['orbital_elements']:
                oe = results['orbital_elements'][0]  # Get first epoch
                print("\n--- Orbital Elements ---")
                print(f"Semi-major axis (a):        {oe['a']:.3f} km")
                print(f"Eccentricity (e):           {oe['e']:.6f}")
                print(f"Inclination (i):            {np.degrees(oe['i']):.3f} degrees")
                print(f"RAAN (Ω):                  {np.degrees(oe['raan']):.3f} degrees")
                print(f"Argument of Perigee (ω):    {np.degrees(oe['argp']):.3f} degrees")
                print(f"True Anomaly (ν):           {np.degrees(oe['nu']):.3f} degrees")
                print(f"Mean Anomaly (M):           {np.degrees(oe['M']):.3f} degrees")
            else:
                print("✗ Failed to extract orbital elements")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def calculate_orbital_period(self):
        """Calculate orbital period from TLE"""
        print("\n--- Orbital Period Calculation ---")
        
        tle_line1, tle_line2 = self.get_tle_input()
        if not tle_line1 or not tle_line2:
            return
        
        try:
            results = self.propagator.propagate_tle(tle_line1, tle_line2, time_span_hours=0.1, step_minutes=0.1)
            if results and results['orbital_elements']:
                oe = results['orbital_elements'][0]
                # Calculate period using Kepler's third law
                # T = 2π * sqrt(a³/μ) where μ = 398600.4418 km³/s² for Earth
                mu = 398600.4418  # km³/s²
                period_seconds = 2 * np.pi * np.sqrt(oe['a']**3 / mu)
                period_minutes = period_seconds / 60
                period_hours = period_minutes / 60
                
                print(f"\n--- Orbital Period ---")
                print(f"Period: {period_seconds:.1f} seconds")
                print(f"Period: {period_minutes:.1f} minutes")
                print(f"Period: {period_hours:.2f} hours")
            else:
                print("✗ Failed to calculate period")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def validate_tle_format(self):
        """Validate TLE format"""
        print("\n--- TLE Format Validation ---")
        
        tle_line1, tle_line2 = self.get_tle_input()
        if not tle_line1 or not tle_line2:
            return
        
        # Basic TLE validation
        valid = True
        errors = []
        
        # Check line lengths
        if len(tle_line1) != 69:
            valid = False
            errors.append(f"Line 1 length: {len(tle_line1)} (should be 69)")
        
        if len(tle_line2) != 69:
            valid = False
            errors.append(f"Line 2 length: {len(tle_line2)} (should be 69)")
        
        # Check line numbers
        if tle_line1[0] != '1':
            valid = False
            errors.append("Line 1 should start with '1'")
        
        if tle_line2[0] != '2':
            valid = False
            errors.append("Line 2 should start with '2'")
        
        # Check satellite numbers match
        if len(tle_line1) >= 7 and len(tle_line2) >= 7:
            sat_num1 = tle_line1[2:7]
            sat_num2 = tle_line2[2:7]
            if sat_num1 != sat_num2:
                valid = False
                errors.append(f"Satellite numbers don't match: {sat_num1} vs {sat_num2}")
        
        if valid:
            print("✓ TLE format is valid")
            
            # Try to parse with satellite-toolkit
            try:
                tle_obj = self.visualizer.sc.TwoLineElement(tle_line1, tle_line2)
                print("✓ TLE successfully parsed by satellite-toolkit")
            except Exception as e:
                print(f"⚠ Warning: TLE parsing error: {e}")
        else:
            print("✗ TLE format errors found:")
            for error in errors:
                print(f"  - {error}")
    
    def list_tdm_files(self):
        """List available TDM files"""
        print("\n--- TDM Files ---")
        
        pattern = self.get_user_input("File pattern", str, "*.tdm")
        files = glob.glob(pattern)
        
        if files:
            print(f"Found {len(files)} TDM files:")
            for i, file in enumerate(files, 1):
                try:
                    size = os.path.getsize(file)
                    mtime = datetime.fromtimestamp(os.path.getmtime(file))
                    print(f"{i:2d}. {file} ({size} bytes, modified {mtime})")
                except Exception as e:
                    print(f"{i:2d}. {file} (error reading file info: {e})")
        else:
            print(f"No files found matching pattern: {pattern}")
    
    def export_results_csv(self):
        """Export last results to CSV"""
        print("\n--- Export Results to CSV ---")
        print("This would export the last propagation results to CSV format.")
        print("Feature not implemented yet - would need to store last results.")
    
    def set_perturbation_parameters_interactive(self):
        """Set perturbation parameters interactively"""
        print("\n--- Set Perturbation Parameters ---")
        
        # Get current parameters
        try:
            current_params = self.propagator.get_perturbation_parameters()
            print("Current parameters:")
            for key, value in current_params.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"Warning: Could not get current parameters: {e}")
            current_params = {}
        
        # Set new parameters
        params = {}
        
        print("\nSolar Radiation Pressure Parameters:")
        cr = self.get_user_input("Coefficient of reflectivity (CR)", float, current_params.get('CR', 1.3))
        if cr is not None:
            params['CR'] = cr
        
        am = self.get_user_input("Area-to-mass ratio (Am) [m²/kg]", float, current_params.get('Am', 0.01))
        if am is not None:
            params['Am'] = am
        
        print("\nAtmospheric Drag Parameters:")
        cd = self.get_user_input("Drag coefficient (CD)", float, current_params.get('CD', 2.2))
        if cd is not None:
            params['CD'] = cd
        
        # Apply parameters
        if params:
            success = self.propagator.set_perturbation_parameters(params)
            if success:
                print("✓ Perturbation parameters updated")
            else:
                print("✗ Failed to update parameters")
    
    def view_perturbation_parameters(self):
        """View current perturbation parameters"""
        print("\n--- Current Perturbation Parameters ---")
        
        try:
            params = self.propagator.get_perturbation_parameters()
            
            print("\nSolar Radiation Pressure:")
            print(f"  Coefficient of reflectivity (CR): {params['CR']}")
            print(f"  Area-to-mass ratio (Am): {params['Am']} m²/kg")
            print(f"  Solar constant (Sc): {params['Sc']} W/m²")
            print(f"  Solar flux variation (nu): {params['nu']}")
            
            print("\nAtmospheric Drag:")
            print(f"  Drag coefficient (CD): {params['CD']}")
            print(f"  Scale height (H0): {params['H0']} km")
            print(f"  Reference density (rho0): {params['rho0']} kg/m³")
            
            print("\nOther Constants:")
            print(f"  J2 coefficient: {params['J2']}")
            print(f"  Moon gravitational parameter: {params['MU_MOON']} km³/s²")
            
        except Exception as e:
            print(f"✗ Error retrieving parameters: {e}")
    
    def get_tle_input(self):
        """Get TLE input from user"""
        print("\nEnter TLE data:")
        tle_line1 = self.get_user_input("TLE Line 1", str)
        if not tle_line1:
            return None, None
        
        tle_line2 = self.get_user_input("TLE Line 2", str)
        if not tle_line2:
            return None, None
        
        return tle_line1, tle_line2
    
    def load_tle_from_file(self):
        """Load TLE from file"""
        print("\n--- Load TLE from File ---")
        
        filename = self.get_user_input("TLE filename", str, "satellite.tle")
        if not filename or not os.path.exists(filename):
            print(f"✗ File not found: {filename}")
            return
        
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            # Find TLE lines (should be exactly 2 lines starting with '1' and '2')
            tle_lines = [line.strip() for line in lines if line.strip() and line.strip()[0] in ['1', '2']]
            
            if len(tle_lines) >= 2:
                tle_line1 = tle_lines[0]
                tle_line2 = tle_lines[1]
                print(f"✓ Loaded TLE from {filename}")
                print(f"Line 1: {tle_line1}")
                print(f"Line 2: {tle_line2}")
                return tle_line1, tle_line2
            else:
                print(f"✗ Invalid TLE file format. Found {len(tle_lines)} TLE lines, need 2.")
                return None, None
                
        except Exception as e:
            print(f"✗ Error reading file: {e}")
            return None, None
    
    def enter_tle_manually(self):
        """Enter TLE data manually"""
        print("\n--- Manual TLE Entry ---")
        print("Enter the two-line element set:")
        
        return self.get_tle_input()
    
    def display_orbital_elements_summary(self, orbital_elements):
        """Display summary of orbital elements evolution"""
        if not orbital_elements:
            return
        
        print(f"\n--- Orbital Elements Summary ({len(orbital_elements)} epochs) ---")
        
        # Get first and last elements
        first = orbital_elements[0]
        last = orbital_elements[-1]
        
        print("Initial → Final:")
        print(f"Semi-major axis: {first['a']:.3f} → {last['a']:.3f} km")
        print(f"Eccentricity:    {first['e']:.6f} → {last['e']:.6f}")
        print(f"Inclination:     {np.degrees(first['i']):.3f} → {np.degrees(last['i']):.3f} deg")
        print(f"RAAN:            {np.degrees(first['raan']):.3f} → {np.degrees(last['raan']):.3f} deg")
        print(f"Arg of Perigee:  {np.degrees(first['argp']):.3f} → {np.degrees(last['argp']):.3f} deg")
        
        # Calculate changes
        da = last['a'] - first['a']
        de = last['e'] - first['e']
        di = np.degrees(last['i'] - first['i'])
        
        print(f"\nChanges:")
        print(f"Δa = {da:.3f} km")
        print(f"Δe = {de:.6f}")
        print(f"Δi = {di:.3f} deg")
    
    def display_comparison_statistics(self, stats):
        """Display comparison statistics"""
        print("\n--- Comparison Statistics ---")
        
        for comparison, data in stats.items():
            print(f"\n{comparison}:")
            print(f"  Mean position difference: {data['mean_position_diff']:.3f} km")
            print(f"  Max position difference:  {data['max_position_diff']:.3f} km")
            print(f"  Std position difference:  {data['std_position_diff']:.3f} km")
            print(f"  Mean Δa: {data['mean_semi_major_diff']:.3f} km")
            print(f"  Mean Δe: {data['mean_ecc_diff']:.6f}")
            print(f"  Mean Δi: {np.degrees(data['mean_inc_diff']):.3f} deg")
    
    def save_results_to_json(self, results, filename):
        """Save results to JSON file"""
        try:
            # Convert numpy arrays to lists for JSON serialization
            json_results = {}
            for key, value in results.items():
                if isinstance(value, np.ndarray):
                    json_results[key] = value.tolist()
                elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], np.ndarray):
                    json_results[key] = [v.tolist() for v in value]
                else:
                    json_results[key] = value
            
            with open(filename, 'w') as f:
                json.dump(json_results, f, indent=2)
            
            print(f"✓ Results saved to: {filename}")
        except Exception as e:
            print(f"✗ Error saving results: {e}")
    
    def help_menu(self):
        """Display help information"""
        print("\n" + "=" * 60)
        print("ODETTE HELP")
        print("=" * 60)
        print("""
ODETTE (Orbit Determination and Trajectory Toolkit) Interactive CLI

MAIN FEATURES:

1. TLE Operations
   - Visualize satellite orbits from Two-Line Element sets
   - Propagate orbits using SGP4/SDP4 models
   - Load TLE from files or enter manually

2. RK45 Propagation  
   - High-precision numerical integration using RK45 method
   - Support for various perturbations (J2, third body, SRP, drag)
   - Uses TDM (Tracking Data Message) files for initial conditions

3. Orbit Comparison
   - Compare TLE vs RK45 propagation methods
   - Compare different perturbation configurations
   - Statistical analysis of orbital element differences

4. Multiple Satellites
   - Visualize multiple satellites simultaneously
   - Mix TLE and RK45 satellites in same plot

5. Configuration
   - Customize default parameters
   - Save/load configuration settings
   - Set perturbation parameters

6. Utilities
   - Convert TLE to orbital elements
   - Calculate orbital periods
   - Validate TLE format
   - Manage TDM files

TIPS:
- Use Ctrl+C to cancel any input prompt
- Default values are shown in brackets [default]
- Results can be saved to JSON format
- Plots can be displayed and/or saved as PNG files

For more detailed help on specific functions, explore the menus.
        """)
    
    def run(self):
        """Main program loop"""
        self.print_banner()
        
        while self.running:
            try:
                self.print_main_menu()
                choice = self.get_user_input("Select option", int, choices=[1, 2, 3, 4, 5, 6, 7, 8])
                
                if choice is None:
                    continue
                elif choice == 1:
                    self.tle_operations_menu()
                elif choice == 2:
                    self.rk45_operations_menu()
                elif choice == 3:
                    self.orbit_comparison_menu()
                elif choice == 4:
                    self.multiple_satellites_menu()
                elif choice == 5:
                    self.configuration_menu()
                elif choice == 6:
                    self.utilities_menu()
                elif choice == 7:
                    self.help_menu()
                elif choice == 8:
                    print("\nGoodbye!")
                    self.running = False
                    
            except KeyboardInterrupt:
                print("\n\nProgram interrupted by user.")
                self.running = False
            except Exception as e:
                print(f"\nUnexpected error: {e}")
                print("Returning to main menu...")


def main():
    """Main entry point"""
    try:
        interface = ODETTEInterface()
        interface.run()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
