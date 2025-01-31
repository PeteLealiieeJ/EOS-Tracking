from dataclasses import dataclass, field

from typing import Optional, Union, List, Dict, Any
from EOS_Tracking.common.type_aliases import Config
from EOS_Tracking.common.base_cameras import BaseCamera
from EOS_Tracking.common.base_controllers import BaseController
from EOS_Tracking.common.base_networks import BaseNetwork

@dataclass
class StackConfiguration:
    """
    Configuration dataclass for stacks to load 
    """
    log_filename         : Optional[str]                                                                        = None
    network_configs      : Union[ Config, List[Config], Dict[Any,Config] ]                                      = field(default_factory=dict)
    camera_configs       : Union[ Config, List[Config], Dict[Any,Config] ]                                      = field(default_factory=dict)
    controller_configs   : Union[ Config, List[Config], Dict[Any,Config] ]                                      = field(default_factory=dict)
    network_classes      : Optional[ Union[ BaseNetwork, List[BaseNetwork], Dict[Any,BaseNetwork] ] ]           = None
    camera_classes       : Optional[ Union[ BaseCamera, List[BaseCamera], Dict[Any,BaseCamera] ] ]              = None
    controller_classes   : Optional[ Union[ BaseController, List[BaseController], Dict[Any,BaseController] ] ]  = None