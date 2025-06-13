#!/usr/bin/env python3
"""
@file orbit_toolkit_logging.py
@brief Logging module for Orbit Toolkit

@details This module provides comprehensive logging functionality including:
- Structured JSON logging
- Performance monitoring
- Error tracking
- Visualization event logging

@author Orbit Toolkit Development Team
@date 2024
@version 1.0
"""

import logging
import json
import time
import traceback
import functools
from datetime import datetime
from pathlib import Path
import os


class OrbitLogger:
    """
    @brief Comprehensive logging class for orbit toolkit operations
    
    @details Provides multiple log streams:
    - General application log (INFO level and above)
    - Structured JSON log for data analysis
    - Error-specific log
    - Performance metrics log
    
    The logger creates separate files for different types of logs, enabling
    efficient analysis and debugging of orbit toolkit operations.
    
    @note All log files are created in the specified log directory with
          component-specific naming conventions.
    """
    
    def __init__(self, component_name, log_dir="logs"):
        """
        @brief Initialize logger for a specific component
        
        @details Creates multiple specialized loggers for different purposes:
        - General logger for standard application events
        - Structured logger for JSON-formatted data
        - Error logger for exception tracking
        - Performance logger for timing metrics
        
        @param component_name Name of the component (visualizer, propagator, etc.)
        @type component_name str
        @param log_dir Directory to store log files
        @type log_dir str
        
        @pre log_dir must be writable
        @post All loggers are initialized and ready for use
        
        @throws OSError If log directory cannot be created
        """
        self.component_name = component_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create multiple loggers for different purposes
        self.general_logger = self._create_general_logger()
        self.structured_logger = self._create_structured_logger()
        self.error_logger = self._create_error_logger()
        self.performance_logger = self._create_performance_logger()
        
    def _create_general_logger(self):
        """
        @brief Create general application logger
        
        @details Sets up a logger for general application events with:
        - File handler for persistent logging
        - Console handler for immediate feedback
        - Appropriate formatters for readability
        
        @return Configured general logger instance
        @retval logging.Logger Logger configured for general use
        
        @note Console output is limited to WARNING level and above
        @note File output includes INFO level and above
        """
        logger = logging.getLogger(f"orbit_{self.component_name}_general")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # File handler
            file_handler = logging.FileHandler(
                self.log_dir / f"Orbit{self.component_name.title()}_all.log"
            )
            file_handler.setLevel(logging.INFO)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
        return logger
    
    def _create_structured_logger(self):
        """
        @brief Create structured JSON logger
        
        @details Creates a logger specifically for structured data output.
        Uses JSON Lines format for easy parsing and analysis.
        
        @return Configured structured logger instance
        @retval logging.Logger Logger configured for JSON output
        
        @note No formatter is applied as JSON is written directly
        @note Output file uses .jsonl extension for JSON Lines format
        """
        logger = logging.getLogger(f"orbit_{self.component_name}_structured")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler(
                self.log_dir / f"Orbit{self.component_name.title()}_structured.jsonl"
            )
            handler.setLevel(logging.INFO)
            
            # No formatter - we'll write JSON directly
            logger.addHandler(handler)
            
        return logger
    
    def _create_error_logger(self):
        """
        @brief Create error-specific logger
        
        @details Sets up a dedicated logger for error tracking with:
        - ERROR level filtering
        - Exception information capture
        - Detailed error formatting
        
        @return Configured error logger instance
        @retval logging.Logger Logger configured for error tracking
        
        @note Includes exception traceback information
        @note Only ERROR level and above are logged
        """
        logger = logging.getLogger(f"orbit_{self.component_name}_errors")
        logger.setLevel(logging.ERROR)
        
        if not logger.handlers:
            handler = logging.FileHandler(
                self.log_dir / f"Orbit{self.component_name.title()}_errors.log"
            )
            handler.setLevel(logging.ERROR)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s\n%(exc_info)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _create_performance_logger(self):
        """
        @brief Create performance metrics logger
        
        @details Specialized logger for tracking performance metrics:
        - Execution times
        - Resource usage
        - Operation success/failure rates
        
        @return Configured performance logger instance
        @retval logging.Logger Logger configured for performance tracking
        
        @note Uses custom formatter to highlight performance data
        @note All entries are prefixed with "PERFORMANCE"
        """
        logger = logging.getLogger(f"orbit_{self.component_name}_performance")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler(
                self.log_dir / f"Orbit{self.component_name.title()}_performance.log"
            )
            handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - PERFORMANCE - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def get_logger(self):
        """
        @brief Get the general logger for basic logging needs
        
        @details Provides access to the general-purpose logger for
        standard application logging requirements.
        
        @return General logger instance
        @retval logging.Logger The general application logger
        
        @see _create_general_logger()
        """
        return self.general_logger
    
    def log_structured_event(self, event_type, data):
        """
        @brief Log a structured event as JSON
        
        @details Creates a structured log entry in JSON format containing:
        - Timestamp (UTC ISO format)
        - Component name
        - Event type
        - Associated data
        
        @param event_type Type of event being logged
        @type event_type str
        @param data Event-specific data to log
        @type data dict
        
        @pre data must be JSON serializable
        @post Event is written to structured log file
        
        @code{.py}
        logger.log_structured_event('computation_start', {
            'algorithm': 'RK45',
            'parameters': {'step_size': 0.1}
        })
        @endcode
        """
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'component': self.component_name,
            'event_type': event_type,
            'data': data
        }
        
        self.structured_logger.info(json.dumps(event))
    
    def log_propagation_start(self, method, parameters):
        """
        @brief Log the start of a propagation operation
        
        @details Records the initiation of an orbit propagation with:
        - Propagation method used
        - Input parameters
        - Start timestamp
        
        @param method Propagation method name (e.g., 'TLE', 'RK45')
        @type method str
        @param parameters Dictionary of propagation parameters
        @type parameters dict
        
        @post Both general and structured logs contain start event
        
        @see log_propagation_end()
        """
        self.general_logger.info(f"Starting {method} propagation with parameters: {parameters}")
        self.log_structured_event('propagation_start', {
            'method': method,
            'parameters': parameters,
            'start_time': time.time()
        })
    
    def log_propagation_end(self, method, duration, success=True):
        """
        @brief Log the end of a propagation operation
        
        @details Records the completion of an orbit propagation with:
        - Propagation method used
        - Total execution time
        - Success/failure status
        
        @param method Propagation method name (e.g., 'TLE', 'RK45')
        @type method str
        @param duration Execution time in seconds
        @type duration float
        @param success Whether operation completed successfully
        @type success bool
        
        @post Both general and structured logs contain completion event
        
        @see log_propagation_start()
        """
        status = "successful" if success else "failed"
        self.general_logger.info(f"Completed {method} propagation in {duration:.2f}s - {status}")
        self.log_structured_event('propagation_end', {
            'method': method,
            'duration_seconds': duration,
            'success': success
        })
    
    def log_visualization_start(self, viz_type, parameters):
        """
        @brief Log the start of a visualization operation
        
        @details Records the initiation of a visualization with:
        - Visualization type
        - Configuration parameters
        - Start timestamp
        
        @param viz_type Type of visualization (e.g., '3D_orbit', 'ground_track')
        @type viz_type str
        @param parameters Dictionary of visualization parameters
        @type parameters dict
        
        @post Both general and structured logs contain start event
        
        @see log_visualization_end()
        """
        self.general_logger.info(f"Starting {viz_type} visualization with parameters: {parameters}")
        self.log_structured_event('visualization_start', {
            'type': viz_type,
            'parameters': parameters,
            'start_time': time.time()
        })
    
    def log_visualization_end(self, viz_type, duration, success=True):
        """
        @brief Log the end of a visualization operation
        
        @details Records the completion of a visualization with:
        - Visualization type
        - Total execution time
        - Success/failure status
        
        @param viz_type Type of visualization (e.g., '3D_orbit', 'ground_track')
        @type viz_type str
        @param duration Execution time in seconds
        @type duration float
        @param success Whether operation completed successfully
        @type success bool
        
        @post Both general and structured logs contain completion event
        
        @see log_visualization_start()
        """
        status = "successful" if success else "failed"
        self.general_logger.info(f"Completed {viz_type} visualization in {duration:.2f}s - {status}")
        self.log_structured_event('visualization_end', {
            'type': viz_type,
            'duration_seconds': duration,
            'success': success
        })
    
    def log_orbital_elements(self, elements, context):
        """
        @brief Log orbital elements data
        
        @details Records calculated orbital elements with context information.
        Useful for tracking orbital state computations and validations.
        
        @param elements Dictionary containing orbital elements
        @type elements dict
        @param context Description of when/why elements were calculated
        @type context str
        
        @post Orbital elements are logged in both general and structured formats
        
        @code{.py}
        elements = {'a': 6778.137, 'e': 0.001, 'i': 51.6}
        logger.log_orbital_elements(elements, 'Initial state from TLE')
        @endcode
        """
        self.general_logger.info(f"Orbital elements calculated: {context}")
        self.log_structured_event('orbital_elements', {
            'context': context,
            'elements': elements
        })
    
    def log_error(self, operation, error, context=None):
        """
        @brief Log an error with full context
        
        @details Comprehensive error logging including:
        - Operation where error occurred
        - Error type and message
        - Full traceback
        - Optional context information
        
        @param operation Name of operation that failed
        @type operation str
        @param error Exception object or error message
        @type error Exception or str
        @param context Additional context information
        @type context str or dict or None
        
        @post Error is logged to general, error, and structured logs
        @post Full traceback is captured for debugging
        
        @warning This method should be called from exception handlers
        """
        error_msg = f"Error in {operation}: {str(error)}"
        
        if context:
            error_msg += f" | Context: {context}"
            
        self.general_logger.error(error_msg)
        self.error_logger.error(error_msg, exc_info=True)
        
        self.log_structured_event('error', {
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        })
    
    def log_performance_metrics(self, operation, metrics):
        """
        @brief Log performance metrics
        
        @details Records performance data for analysis and optimization:
        - Operation name
        - Execution metrics (time, memory, etc.)
        - Success rates
        - Resource utilization
        
        @param operation Name of operation being measured
        @type operation str
        @param metrics Dictionary of performance metrics
        @type metrics dict
        
        @post Metrics are logged to performance and structured logs
        
        @code{.py}
        metrics = {
            'duration_seconds': 1.23,
            'memory_mb': 45.6,
            'cpu_percent': 78.9
        }
        logger.log_performance_metrics('orbit_propagation', metrics)
        @endcode
        """
        metrics_str = ", ".join([f"{k}: {v}" for k, v in metrics.items()])
        self.performance_logger.info(f"{operation} - {metrics_str}")
        
        self.log_structured_event('performance_metrics', {
            'operation': operation,
            'metrics': metrics
        })


def create_orbit_logger(component_name, log_dir="logs"):
    """
    @brief Factory function to create an OrbitLogger instance
    
    @details Convenience function for creating properly configured
    OrbitLogger instances with consistent settings.
    
    @param component_name Name of the component
    @type component_name str
    @param log_dir Directory for log files
    @type log_dir str
        
    @return Configured logger instance
    @retval OrbitLogger Ready-to-use logger
    
    @throws OSError If log directory cannot be created
    
    @code{.py}
    logger = create_orbit_logger('propagator', '/tmp/logs')
    logger.get_logger().info('Component initialized')
    @endcode
    """
    return OrbitLogger(component_name, log_dir)


def performance_monitor(logger=None):
    """
    @brief Decorator to monitor function performance
    
    @details Provides automatic performance monitoring for any function:
    - Records execution time
    - Logs success/failure status
    - Captures exceptions
    - Reports metrics to logger
    
    @param logger OrbitLogger instance, if None will create one
    @type logger OrbitLogger or None
        
    @return Decorated function with performance monitoring
    @retval function Function wrapper with monitoring
    
    @post Function execution is automatically logged
    @post Performance metrics are captured
    
    @code{.py}
    @performance_monitor()
    def compute_orbit():
        # Your orbit computation code
        return result
    @endcode
    
    @see visualization_monitor() for visualization-specific monitoring
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create logger
            if logger is None:
                monitor_logger = create_orbit_logger('performance')
            else:
                monitor_logger = logger
                
            # Record start time
            start_time = time.time()
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Calculate metrics
                duration = time.time() - start_time
                
                # Log success
                monitor_logger.log_performance_metrics(func.__name__, {
                    'duration_seconds': duration,
                    'success': True
                })
                
                return result
                
            except Exception as e:
                # Calculate metrics for failed operation
                duration = time.time() - start_time
                
                # Log failure
                monitor_logger.log_performance_metrics(func.__name__, {
                    'duration_seconds': duration,
                    'success': False,
                    'error': str(e)
                })
                
                # Log the error
                monitor_logger.log_error(func.__name__, e)
                
                # Re-raise the exception
                raise
                
        return wrapper
    return decorator


def visualization_monitor(logger=None, viz_type="unknown"):
    """
    @brief Decorator to monitor visualization operations
    
    @details Specialized monitoring for visualization functions:
    - Tracks visualization type and parameters
    - Records rendering performance
    - Logs success/failure with context
    - Provides detailed visualization metrics
    
    @param logger OrbitLogger instance
    @type logger OrbitLogger or None
    @param viz_type Type of visualization being monitored
    @type viz_type str
        
    @return Decorated function with visualization monitoring
    @retval function Function wrapper with visualization monitoring
    
    @post Visualization operations are automatically logged
    @post Start and end events are recorded
    
    @code{.py}
    @visualization_monitor(viz_type="3D_orbit")
    def plot_orbit_3d(data):
        # Your visualization code
        return figure
    @endcode
    
    @see performance_monitor() for general performance monitoring
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create logger
            if logger is None:
                monitor_logger = create_orbit_logger('visualization')
            else:
                monitor_logger = logger
                
            # Log start
            start_time = time.time()
            monitor_logger.log_visualization_start(viz_type, {
                'function': func.__name__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys())
            })
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Log success
                duration = time.time() - start_time
                monitor_logger.log_visualization_end(viz_type, duration, True)
                
                return result
                
            except Exception as e:
                # Log failure
                duration = time.time() - start_time
                monitor_logger.log_visualization_end(viz_type, duration, False)
                monitor_logger.log_error(f"{func.__name__}_{viz_type}", e)
                
                # Re-raise the exception
                raise
                
        return wrapper
    return decorator


# Example usage and testing
if __name__ == "__main__":
    """
    @brief Example usage and testing of the logging module
    
    @details Demonstrates:
    - Logger creation
    - Basic logging
    - Structured event logging
    - Error handling
    - Performance monitoring
    """
    # Create a test logger
    test_logger = create_orbit_logger('test')
    
    # Test basic logging
    test_logger.get_logger().info("Test message")
    
    # Test structured logging
    test_logger.log_structured_event('test_event', {'data': 'value'})
    
    # Test error logging
    try:
        raise ValueError("Test error")
    except Exception as e:
        test_logger.log_error('test_operation', e, {'context': 'testing'})
    
    # Test performance monitoring decorator
    @performance_monitor(logger=test_logger)
    def test_function():
        """
        @brief Test function for performance monitoring
        @return Success message
        """
        time.sleep(0.1)  # Simulate work
        return "success"
    
    result = test_function()
    print("Logging test completed successfully")
