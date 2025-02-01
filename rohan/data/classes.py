from dataclasses                    import dataclass, field
from typing                         import Optional, Union, List, Dict, Any
from rohan.common.type_aliases      import Config
from rohan.common.base_cameras      import CameraBase
from rohan.common.base_controllers  import ControllerBase
from rohan.common.base_networks     import NetworkBase

@dataclass
class StackConfiguration:
    """
    Configuration dataclass for stacks to load 
    """
    log_filename         : Optional[str]                                                                        = None
    network_configs      : Union[ Config, List[Config], Dict[Any,Config] ]                                      = field(default_factory=dict)
    camera_configs       : Union[ Config, List[Config], Dict[Any,Config] ]                                      = field(default_factory=dict)
    controller_configs   : Union[ Config, List[Config], Dict[Any,Config] ]                                      = field(default_factory=dict)
    network_classes      : Optional[ Union[ NetworkBase, List[NetworkBase], Dict[Any,NetworkBase] ] ]           = None
    camera_classes       : Optional[ Union[ CameraBase, List[CameraBase], Dict[Any,CameraBase] ] ]              = None
    controller_classes   : Optional[ Union[ ControllerBase, List[ControllerBase], Dict[Any,ControllerBase] ] ]  = None