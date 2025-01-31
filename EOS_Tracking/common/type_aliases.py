from typing import Union, Optional, Dict, List, Tuple
from numpy.typing import NDArray

"""
Type aliases used in the package
"""

Config      = Dict[ str, Optional[ Union[ float , str ]]]
Joints      = Union[ List[ float ], NDArray ]
Resolution  = Tuple[ int, int ]

