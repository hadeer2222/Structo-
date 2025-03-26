"""
Structural calculations for floor beams and purlins according to
Egyptian and American code standards.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from .constants import (
    STEEL_YIELD_STRENGTH, STEEL_ULTIMATE_STRENGTH,
    STEEL_MODULUS_OF_ELASTICITY, GRAVITY,
    SAFETY_FACTOR_EGYPTIAN, SAFETY_FACTOR_AMERICAN,
    KG_TO_KN
)

def convert_to_kn(value: float, unit: str) -> float:
    """
    Convert various units to kN
    
    Args:
        value: The numerical value
        unit: The unit (kg, kN, N, etc.)
        
    Returns:
        float: Value in kN
    """
    unit = unit.lower()
    if unit == "kn":
        return value
    elif unit == "kg":
        return value * KG_TO_KN
    elif unit == "n":
        return value / 1000
    elif unit == "kn/m":
        return value  # Already in kN unit
    elif unit == "kg/m":
        return value * KG_TO_KN
    elif unit == "n/m":
        return value / 1000
    else:
        raise ValueError(f"Unsupported unit: {unit}")

def calculate_dead_load(span: float, weight_per_meter: float) -> float:
    """
    Calculate the dead load based on span and weight per meter
    
    Args:
        span: The span in meters
        weight_per_meter: The weight per meter in kN/m
        
    Returns:
        float: Total dead load in kN
    """
    return weight_per_meter * span

def calculate_live_load(span: float, load_per_sqm: float, width: float = 1.0) -> float:
    """
    Calculate the live load based on span and load per square meter
    
    Args:
        span: The span in meters
        load_per_sqm: The load per square meter in kN/m²
        width: The width of the beam in meters (default: 1.0)
        
    Returns:
        float: Total live load in kN
    """
    return load_per_sqm * span * width

def calculate_total_load(loads: List[Dict[str, Any]]) -> float:
    """
    Calculate the total load from all load components
    
    Args:
        loads: List of load dictionaries with 'value' and 'unit' keys
        
    Returns:
        float: Total load in kN
    """
    total = 0.0
    for load in loads:
        total += convert_to_kn(load['value'], load['unit'])
    return total

def calculate_moment(span: float, total_load: float, load_type: str = "uniform") -> float:
    """
    Calculate the maximum moment for a simply supported beam
    
    Args:
        span: The span in meters
        total_load: The total load in kN (or kN/m for uniform)
        load_type: The load type ("uniform", "point_center", etc.)
        
    Returns:
        float: Maximum moment in kNm
    """
    if load_type == "uniform":
        # For uniformly distributed load: M = wL²/8
        return (total_load * span**2) / 8
    elif load_type == "point_center":
        # For point load at center: M = PL/4
        return (total_load * span) / 4
    else:
        raise ValueError(f"Unsupported load type: {load_type}")

def calculate_shear_force(span: float, total_load: float, load_type: str = "uniform") -> float:
    """
    Calculate the maximum shear force for a simply supported beam
    
    Args:
        span: The span in meters
        total_load: The total load in kN (or kN/m for uniform)
        load_type: The load type ("uniform", "point_center", etc.)
        
    Returns:
        float: Maximum shear force in kN
    """
    if load_type == "uniform":
        # For uniformly distributed load: V = wL/2
        return (total_load * span) / 2
    elif load_type == "point_center":
        # For point load at center: V = P/2
        return total_load / 2
    else:
        raise ValueError(f"Unsupported load type: {load_type}")

def calculate_deflection(span: float, moment: float, modulus: float = STEEL_MODULUS_OF_ELASTICITY, 
                         inertia: float = None, load_type: str = "uniform") -> float:
    """
    Calculate the maximum deflection for a simply supported beam
    
    Args:
        span: The span in meters
        moment: The maximum moment in kNm
        modulus: The modulus of elasticity in MPa
        inertia: The moment of inertia in mm⁴
        load_type: The load type ("uniform", "point_center", etc.)
        
    Returns:
        float: Maximum deflection in mm
    """
    if inertia is None:
        # Return a formula representation if inertia is not provided
        return "5wL⁴/(384EI)" if load_type == "uniform" else "PL³/(48EI)"
    
    # Convert units: span from m to mm, modulus from MPa to N/mm²
    span_mm = span * 1000
    
    if load_type == "uniform":
        # For uniformly distributed load: δ = 5wL⁴/(384EI)
        # Convert moment to equivalent uniform load: w = 8M/L²
        w = 8 * moment / (span**2)  # kN/m
        w_n_mm = w / 1000000  # Convert kN/m to N/mm
        return (5 * w_n_mm * span_mm**4) / (384 * modulus * inertia)
    elif load_type == "point_center":
        # For point load at center: δ = PL³/(48EI)
        # Convert moment to equivalent point load: P = 4M/L
        p = 4 * moment / span  # kN
        p_n = p * 1000  # Convert kN to N
        return (p_n * span_mm**3) / (48 * modulus * inertia)
    else:
        raise ValueError(f"Unsupported load type: {load_type}")

def check_section_capacity(moment: float, section_modulus: float, steel_grade: str, 
                          code: str = "egyptian") -> Dict[str, Any]:
    """
    Check if the section has sufficient capacity for the given moment
    
    Args:
        moment: The design moment in kNm
        section_modulus: The section modulus in mm³
        steel_grade: The steel grade (e.g., "St37", "A36")
        code: The design code ("egyptian" or "american")
        
    Returns:
        dict: Result dictionary with status and utilization
    """
    # Get yield strength based on steel grade
    fy = STEEL_YIELD_STRENGTH.get(steel_grade)
    if fy is None:
        raise ValueError(f"Unknown steel grade: {steel_grade}")
    
    # Convert units: moment from kNm to Nmm, fy from MPa to N/mm²
    moment_nmm = moment * 1000000
    
    # Calculate moment capacity: M = fy * Z / safety_factor
    safety_factor = SAFETY_FACTOR_EGYPTIAN if code.lower() == "egyptian" else SAFETY_FACTOR_AMERICAN
    moment_capacity = (fy * section_modulus) / safety_factor
    
    # Calculate utilization ratio
    utilization = moment_nmm / moment_capacity
    
    return {
        "status": "Safe" if utilization <= 1.0 else "Unsafe",
        "utilization": utilization,
        "moment_capacity": moment_capacity / 1000000,  # Convert back to kNm
        "safety_factor": safety_factor
    }

def check_deflection(span: float, deflection: float, load_type: str, is_accessible: bool = True) -> Dict[str, Any]:
    """
    Check if the deflection is within allowable limits
    
    Args:
        span: The span in meters
        deflection: The calculated deflection in mm
        load_type: The load type ("floor" or "roof")
        is_accessible: Whether the area is accessible
        
    Returns:
        dict: Result dictionary with status and details
    """
    # Convert span to mm
    span_mm = span * 1000
    
    # Determine allowable deflection limit based on load type and accessibility
    if load_type.lower() == "floor" or is_accessible:
        # For floors or accessible areas: L/360
        allowable_deflection = span_mm / 360
    else:
        # For roofs or non-accessible areas: L/240
        allowable_deflection = span_mm / 240
    
    # Calculate utilization ratio
    utilization = deflection / allowable_deflection
    
    return {
        "status": "Safe" if utilization <= 1.0 else "Unsafe",
        "utilization": utilization,
        "allowable_deflection": allowable_deflection,
        "limit_ratio": "L/360" if load_type.lower() == "floor" or is_accessible else "L/240"
    }

def check_compactness(section_properties: Dict[str, Any], steel_grade: str, 
                     code: str = "egyptian") -> Dict[str, Any]:
    """
    Check the compactness of the steel section according to code requirements
    
    Args:
        section_properties: Dictionary of section properties
        steel_grade: The steel grade
        code: The design code ("egyptian" or "american")
        
    Returns:
        dict: Result dictionary with compactness classification
    """
    # Get steel properties
    fy = STEEL_YIELD_STRENGTH.get(steel_grade)
    if fy is None:
        raise ValueError(f"Unknown steel grade: {steel_grade}")
    
    # Extract section dimensions
    flange_width = section_properties.get("width")
    flange_thickness = section_properties.get("flange_thickness")
    web_height = section_properties.get("height") - 2 * flange_thickness
    web_thickness = section_properties.get("web_thickness")
    
    if None in (flange_width, flange_thickness, web_height, web_thickness):
        raise ValueError("Missing section properties")
    
    # Calculate width-to-thickness ratios
    flange_ratio = (flange_width / 2) / flange_thickness
    web_ratio = web_height / web_thickness
    
    # Determine limits based on code
    if code.lower() == "egyptian":
        # Egyptian code limits (simplified)
        flange_compact_limit = 0.38 * np.sqrt(STEEL_MODULUS_OF_ELASTICITY / fy)
        web_compact_limit = 3.76 * np.sqrt(STEEL_MODULUS_OF_ELASTICITY / fy)
    else:  # American code
        # AISC limits (simplified)
        flange_compact_limit = 0.38 * np.sqrt(STEEL_MODULUS_OF_ELASTICITY / fy)
        web_compact_limit = 3.76 * np.sqrt(STEEL_MODULUS_OF_ELASTICITY / fy)
    
    # Determine classification
    flange_compact = flange_ratio <= flange_compact_limit
    web_compact = web_ratio <= web_compact_limit
    
    # Overall classification
    if flange_compact and web_compact:
        classification = "Compact"
    else:
        classification = "Non-Compact"
    
    return {
        "classification": classification,
        "flange_ratio": flange_ratio,
        "web_ratio": web_ratio,
        "flange_compact_limit": flange_compact_limit,
        "web_compact_limit": web_compact_limit,
        "flange_status": "Compact" if flange_compact else "Non-Compact",
        "web_status": "Compact" if web_compact else "Non-Compact"
    }

def check_lateral_torsional_buckling(span: float, section_properties: Dict[str, Any], 
                                    steel_grade: str, moment: float, 
                                    code: str = "egyptian") -> Dict[str, Any]:
    """
    Check the lateral torsional buckling capacity of the section
    
    Args:
        span: The unbraced length in meters
        section_properties: Dictionary of section properties
        steel_grade: The steel grade
        moment: The design moment in kNm
        code: The design code ("egyptian" or "american")
        
    Returns:
        dict: Result dictionary with status and details
    """
    # Get steel properties
    fy = STEEL_YIELD_STRENGTH.get(steel_grade)
    E = STEEL_MODULUS_OF_ELASTICITY
    
    if fy is None:
        raise ValueError(f"Unknown steel grade: {steel_grade}")
    
    # Extract section properties
    Iy = section_properties.get("Iy")  # Moment of inertia about y-axis (mm⁴)
    J = section_properties.get("J")    # Torsional constant (mm⁴)
    Cw = section_properties.get("Cw")  # Warping constant (mm⁶)
    
    if None in (Iy, J, Cw):
        # If properties are not provided, return a simplified check
        return {
            "status": "Cannot determine - missing section properties",
            "utilization": None,
            "note": "Detailed section properties (Iy, J, Cw) required for LTB check"
        }
    
    # Convert span to mm
    Lb = span * 1000
    
    # Calculate critical moment for LTB (simplified formula)
    # Mcr = (π/Lb) * √(EIy * GJ)
    G = E / (2 * (1 + 0.3))  # Shear modulus
    Mcr_nmm = (np.pi/Lb) * np.sqrt(E * Iy * G * J)
    Mcr = Mcr_nmm / 1000000  # Convert to kNm
    
    # Apply safety factor
    safety_factor = SAFETY_FACTOR_EGYPTIAN if code.lower() == "egyptian" else SAFETY_FACTOR_AMERICAN
    design_capacity = Mcr / safety_factor
    
    # Check utilization
    utilization = moment / design_capacity
    
    return {
        "status": "Safe" if utilization <= 1.0 else "Unsafe",
        "utilization": utilization,
        "critical_moment": Mcr,
        "design_capacity": design_capacity
    }

def select_optimal_section(
    moment: float, 
    span: float, 
    load_type: str, 
    steel_grade: str,
    code: str = "egyptian",
    section_type: str = "I-Beam"
) -> Dict[str, Any]:
    """
    Select the optimal section based on the design requirements
    
    This is a simplified approach that would be expanded with a real section database
    
    Args:
        moment: The design moment in kNm
        span: The span in meters
        load_type: The load type
        steel_grade: The steel grade
        code: The design code
        section_type: The type of section to select
        
    Returns:
        dict: Selected section properties and check results
    """
    # This is a simplified implementation that would normally use a database of standard sections
    # For this demo, we'll create a parametric section based on the moment
    
    # Get yield strength
    fy = STEEL_YIELD_STRENGTH.get(steel_grade, 250)  # Default to 250 MPa if not found
    
    # Safety factor
    safety_factor = SAFETY_FACTOR_EGYPTIAN if code.lower() == "egyptian" else SAFETY_FACTOR_AMERICAN
    
    # Required section modulus (Zx) in mm³
    # M = fy * Zx / safety_factor
    # Zx = M * safety_factor / fy
    required_Z = (moment * 1000000 * safety_factor) / fy
    
    # Parametrically size a section (very simplified)
    if section_type == "I-Beam":
        # For I-beam, we'll use a simplified sizing approach
        height = max(160, int(np.ceil(np.sqrt(required_Z / 20))))  # mm
        width = max(82, int(np.ceil(height / 2)))  # mm
        web_thickness = max(5, int(np.ceil(height / 40)))  # mm
        flange_thickness = max(7, int(np.ceil(height / 25)))  # mm
        
        # Round to standard increments
        height = int(np.ceil(height / 10) * 10)
        width = int(np.ceil(width / 5) * 5)
        web_thickness = max(5, int(np.ceil(web_thickness / 1) * 1))
        flange_thickness = max(7, int(np.ceil(flange_thickness / 1) * 1))
        
        # Calculate section properties (simplified)
        area = 2 * width * flange_thickness + web_thickness * (height - 2 * flange_thickness)  # mm²
        Ix = (width * height**3) / 12 - ((width - web_thickness) * (height - 2 * flange_thickness)**3) / 12  # mm⁴
        Zx = Ix / (height / 2)  # mm³
        Iy = (height * width**3) / 12 - ((height - 2 * flange_thickness) * (width - web_thickness)**3) / 12  # mm⁴
        J = (1/3) * (2 * width * flange_thickness**3 + (height - 2 * flange_thickness) * web_thickness**3)  # mm⁴ (torsional constant)
        Cw = (Iy * (height - flange_thickness)**2) / 4  # mm⁶ (warping constant, simplified)
        
        # Create section description
        section_name = f"I-{height}x{width}x{web_thickness}x{flange_thickness}"
    
    elif section_type == "Channel":
        # For channel section
        height = max(100, int(np.ceil(np.sqrt(required_Z / 8))))  # mm
        width = max(50, int(np.ceil(height / 3)))  # mm
        web_thickness = max(4, int(np.ceil(height / 50)))  # mm
        flange_thickness = max(5, int(np.ceil(height / 30)))  # mm
        
        # Round to standard increments
        height = int(np.ceil(height / 10) * 10)
        width = int(np.ceil(width / 5) * 5)
        web_thickness = max(4, int(np.ceil(web_thickness / 1) * 1))
        flange_thickness = max(5, int(np.ceil(flange_thickness / 1) * 1))
        
        # Calculate section properties (simplified)
        area = 2 * width * flange_thickness + web_thickness * (height - 2 * flange_thickness)  # mm²
        Ix = (web_thickness * height**3) / 12 + 2 * (width * flange_thickness**3 / 12 + width * flange_thickness * (height/2 - flange_thickness/2)**2)  # mm⁴
        Zx = Ix / (height / 2)  # mm³
        
        # Simplified estimates for other properties
        Iy = (height * web_thickness**3) / 12 + 2 * (flange_thickness * width**3 / 12)  # mm⁴
        J = (1/3) * (web_thickness**3 * height + 2 * width * flange_thickness**3)  # mm⁴
        Cw = (Iy * (height - flange_thickness)**2) / 4  # mm⁶ (simplified)
        
        # Create section description
        section_name = f"C-{height}x{width}x{web_thickness}x{flange_thickness}"
    
    else:
        raise ValueError(f"Unsupported section type: {section_type}")
    
    # Section properties dictionary
    section_properties = {
        "name": section_name,
        "type": section_type,
        "height": height,
        "width": width,
        "web_thickness": web_thickness,
        "flange_thickness": flange_thickness,
        "area": area,
        "Ix": Ix,
        "Iy": Iy,
        "Zx": Zx,
        "J": J,
        "Cw": Cw
    }
    
    # Calculate deflection
    # For uniform load: δ = 5wL⁴/(384EI)
    # Convert moment to equivalent uniform load: w = 8M/L²
    if load_type == "uniform":
        w = 8 * moment / (span**2)  # kN/m
        w_n_mm = w / 1000000  # Convert kN/m to N/mm
        span_mm = span * 1000  # Convert m to mm
        deflection = (5 * w_n_mm * span_mm**4) / (384 * STEEL_MODULUS_OF_ELASTICITY * Ix)
    else:  # Point load
        p = 4 * moment / span  # kN
        p_n = p * 1000  # Convert kN to N
        span_mm = span * 1000  # Convert m to mm
        deflection = (p_n * span_mm**3) / (48 * STEEL_MODULUS_OF_ELASTICITY * Ix)
    
    # Run design checks
    capacity_check = check_section_capacity(moment, Zx, steel_grade, code)
    deflection_check = check_deflection(span, deflection, "floor" if load_type == "uniform" else "roof", True)
    compactness_check = check_compactness(section_properties, steel_grade, code)
    ltb_check = check_lateral_torsional_buckling(span, section_properties, steel_grade, moment, code)
    
    # Overall status
    if (
        capacity_check["status"] == "Safe" and
        deflection_check["status"] == "Safe" and
        ltb_check["status"] == "Safe"
    ):
        overall_status = "Safe"
    else:
        overall_status = "Unsafe"
    
    return {
        "section_properties": section_properties,
        "required_section_modulus": required_Z,
        "provided_section_modulus": Zx,
        "deflection": deflection,
        "capacity_check": capacity_check,
        "deflection_check": deflection_check,
        "compactness_check": compactness_check,
        "ltb_check": ltb_check,
        "overall_status": overall_status
    }

# Additional functions for purlin calculations

def calculate_wind_load(span: float, wind_pressure: float, purlin_spacing: float = 1.0) -> float:
    """
    Calculate the wind load on a purlin
    
    Args:
        span: The span in meters
        wind_pressure: The wind pressure in kN/m²
        purlin_spacing: The spacing between purlins in meters
        
    Returns:
        float: Wind load in kN/m
    """
    return wind_pressure * purlin_spacing

def calculate_critical_moment(loads: Dict[str, float], span: float) -> Dict[str, float]:
    """
    Calculate the critical moment from various load combinations
    
    Args:
        loads: Dictionary of loads (dead, live, wind, etc.) in kN/m
        span: The span in meters
        
    Returns:
        dict: Critical moment values for different combinations
    """
    # Basic load combinations (simplified)
    # 1. Dead + Live
    combo1 = loads.get("dead", 0) + loads.get("live", 0)
    
    # 2. Dead + Wind (upward)
    combo2 = loads.get("dead", 0) - loads.get("wind", 0)
    
    # 3. Dead + Live + Maintenance
    combo3 = loads.get("dead", 0) + loads.get("live", 0) + loads.get("maintenance", 0)
    
    # Calculate moments for each combination (assuming uniform load)
    moment1 = (combo1 * span**2) / 8 if combo1 > 0 else 0
    moment2 = (combo2 * span**2) / 8 if combo2 > 0 else 0
    moment3 = (combo3 * span**2) / 8 if combo3 > 0 else 0
    
    # For maintenance load as point load at center
    moment_point = (loads.get("maintenance", 0) * span) / 4 if "maintenance" in loads else 0
    
    # Get the critical (maximum) value
    critical_moment = max(moment1, moment2, moment3, moment_point)
    critical_case = "Dead + Live"
    if critical_moment == moment2:
        critical_case = "Dead + Wind (upward)"
    elif critical_moment == moment3:
        critical_case = "Dead + Live + Maintenance"
    elif critical_moment == moment_point:
        critical_case = "Maintenance (point load)"
    
    return {
        "critical_moment": critical_moment,
        "critical_case": critical_case,
        "combinations": {
            "Dead + Live": moment1,
            "Dead + Wind": moment2,
            "Dead + Live + Maintenance": moment3,
            "Maintenance (point load)": moment_point
        }
    } 
