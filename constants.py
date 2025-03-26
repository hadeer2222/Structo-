"""
Constants and default values for the Structo application
"""

# Steel Grades
EGYPTIAN_STEEL_GRADES = ["St37", "St44", "St52", "St60", "St70"]
AMERICAN_STEEL_GRADES = ["A36", "A572", "A992", "S235", "S275", "S355", "S450", "S500"]

# Steel properties (MPa)
STEEL_YIELD_STRENGTH = {
    # Egyptian code
    "St37": 240,
    "St44": 280,
    "St52": 360,
    "St60": 420,
    "St70": 490,
    # American code
    "A36": 250,
    "A572": 345,
    "A992": 345,
    "S235": 235,
    "S275": 275,
    "S355": 355,
    "S450": 440,
    "S500": 500
}

STEEL_ULTIMATE_STRENGTH = {
    # Egyptian code
    "St37": 360,
    "St44": 430,
    "St52": 520,
    "St60": 600,
    "St70": 700,
    # American code
    "A36": 400,
    "A572": 450,
    "A992": 450,
    "S235": 360,
    "S275": 430,
    "S355": 510,
    "S450": 550,
    "S500": 625
}

# Modulus of elasticity (MPa)
STEEL_MODULUS_OF_ELASTICITY = 200000

# Poisson's ratio
STEEL_POISSON_RATIO = 0.3

# Gravitational acceleration (m/s²)
GRAVITY = 9.81

# Unit conversion factors
KG_TO_KN = 0.00981  # Convert kg to kN
MM_TO_M = 0.001     # Convert mm to m
CM_TO_M = 0.01      # Convert cm to m

# Safety factors
SAFETY_FACTOR_EGYPTIAN = 1.5
SAFETY_FACTOR_AMERICAN = 1.67

# Default loads
DEFAULT_MAINTENANCE_LOAD_KG = 100  # Default maintenance load in kg

# Maximum allowable deflections
MAX_DEFLECTION_RATIO_FLOORS = 360  # L/360 for floors
MAX_DEFLECTION_RATIO_ROOFS = 240   # L/240 for roofs

# Section types
SECTION_TYPES = ["I-Beam", "Channel", "Angle", "Hollow Structural Section", "T-Section"]

# Load cases
LOAD_CASES = ["Case A", "Case B"]

# Default values for section properties
DEFAULT_SECTION_PROPERTIES = {
    "I-Beam": {
        "height": 200,  # mm
        "width": 100,   # mm
        "web_thickness": 8,  # mm
        "flange_thickness": 12  # mm
    },
    "Channel": {
        "height": 200,  # mm
        "width": 80,    # mm
        "web_thickness": 6,  # mm
        "flange_thickness": 10  # mm
    }
}
