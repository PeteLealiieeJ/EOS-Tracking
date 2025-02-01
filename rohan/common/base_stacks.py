from abc                             import abstractmethod
from rohan.common.base               import _RohanBase,_RohanThreading
from rohan.data.classes              import StackConfiguration
from rohan.common.base_cameras       import CameraBase
from rohan.common.base_controllers   import ControllerBase
from rohan.common.base_networks      import NetworkBase
from rohan.common.logging            import Logger
from typing                          import Optional, List, Dict, Union, Any, TypeVar
from contextlib                      import nullcontext, ExitStack
from rohan.utils.timers              import IntervalTimer

SelfStackBase = TypeVar("SelfStackBase", bound="StackBase" )
class StackBase(_RohanBase): 
    """
    Base class for an arbitrary camera(s) + controller(s) + network(s) stack
    :param config: configuration as rohan StackConfiguration() dataclass
    :param spin_intrvl: Inverse-frequency of spinning loop
    """

    process_name : str = "unnamed stack"
    config       : StackConfiguration
    spin_intrvl  : float 


    def __init__( 
        self, 
        config      : Optional[StackConfiguration] = None,
        spin_intrvl : float = -1
    ):
        self.spin_intrvl = spin_intrvl
        self.configure(config=config)

    def configure(
        self,
        config : Optional[StackConfiguration] = None
    ) -> None:
        """
        Configures the stack
        :param config: configuration as rohan StackConfiguration() dataclass
        """
        if isinstance(config,StackConfiguration):
            self.config = config

    def spin( self ) -> None:
        """
        Spin-up stack
        """
        spin_timer = IntervalTimer(interval=self.spin_intrvl)
        with Logger(self.config.log_filename) as logger, ExitStack() as stack: 
            _networks, _cameras, _controllers = self._enter_subcontexts( stack=stack, logger=logger ) 

            if isinstance(logger,Logger): 
                logger.write(
                    f'Spinning Up Stack',
                    process_name=self.process_name
                )
            try:
                while True:
                    spin_timer.await_interval()
                    self.process( 
                        network=_networks, 
                        camera=_cameras, 
                        controller=_controllers
                    )

            except KeyboardInterrupt:
                if isinstance(logger,Logger): 
                    logger.write(
                        f'Spinning Down Stack',
                        process_name=self.process_name
                    )

    def _enter_subcontexts(
        self,
        stack   : ExitStack,
        logger  : Logger,
    ) -> None:
        """
        Enter stack subcomponent contexts
        """
        
        if not isinstance(self.config,StackConfiguration):
            if isinstance(logger,Logger): 
                    logger.write(
                        f'No configuration file was loaded and config is {type(self.config)} ... raising RuntimeError',
                        process_name=self.process_name
                    )
            raise RuntimeError("No configuration file was loaded")

        # Enter Network Contexts
        if self.config.network_classes is None:
            networks = stack.enter_context( nullcontext() ) 
        elif isinstance(self.config.network_classes,List):
            networks = [ 
                stack.enter_context( network_class( logger=logger, **network_config ) if network_class is not None else stack.enter_context( nullcontext ) ) 
                for network_class, network_config in zip(self.config.network_classes,self.config.network_configs)
            ]
        elif isinstance(self.config.network_classes,Dict):
            networks = {
                key : stack.enter_context( network_class( logger=logger, **self.config.network_configs[key] ) if network_class is not None else stack.enter_context( nullcontext ) ) 
                for key, network_class in self.config.network_classes.items()
            }
        else:
            if not issubclass(self.config.network_classes,NetworkBase):
                raise TypeError(f"Network object provided did not match any excpected classes: Provided class is {type(self.config.network_classes)} ")
            networks = stack.enter_context( self.config.network_classes( logger=logger,**self.config.network_configs ) )
        
        # Enter Camera Contexts
        if self.config.camera_classes is None:
            cameras = stack.enter_context( nullcontext() ) 
        elif isinstance(self.config.camera_classes,List):
            cameras = [ 
                stack.enter_context( camera_class( logger=logger, **camera_config ) if camera_class is not None else stack.enter_context( nullcontext ) ) 
                for camera_class, camera_config in zip(self.config.camera_classes,self.config.camera_configs)
            ]
        elif isinstance(self.config.camera_classes,Dict):
            cameras = {
                key : stack.enter_context( camera_class( logger=logger, **self.config.camera_configs[key] ) if camera_class is not None else stack.enter_context( nullcontext ) ) 
                for key, camera_class in self.config.camera_classes.items()
            }
        else:
            if not issubclass(self.config.camera_classes,CameraBase):
                raise TypeError(f"Camera object provided did not match any excpected classes: Provided class is {type(self.config.camera_classes)} ")
            cameras = stack.enter_context( self.config.camera_classes( logger=logger, **self.config.camera_configs ) )

        # Enter Controller Contexts
        if self.config.controller_classes is None:
            controllers = stack.enter_context( nullcontext() )
        elif isinstance(self.config.controller_classes,List):
            controllers = [ 
                stack.enter_context( controller_class( logger=logger, **controller_config ) if controller_class is not None else stack.enter_context( nullcontext ) ) 
                for controller_class,controller_config in zip(self.config.controller_classes,self.config.controller_configs)
            ]
        elif isinstance(self.config.controller_classes,Dict):
            controllers = {
                key : stack.enter_context( controller_class( logger=logger, **self.config.controller_configs[key] ) if controller_class is not None else stack.enter_context( nullcontext ) ) 
                for key, controller_class in self.config.controller_classes.items()
            }
        else:
            if not issubclass(self.config.controller_classes,ControllerBase):
                raise TypeError(f"Controller object provided did not match any excpected classes: Provided class is {type(self.config.controller_classes)} ")
            controllers = stack.enter_context( self.config.controller_classes( logger=logger,**self.config.controller_configs ) )

        return networks, cameras, controllers

    @abstractmethod
    def process(  
        self, 
        network     : Optional[ Union[ NetworkBase, List[NetworkBase], Dict[Any,NetworkBase] ] ]               = None,
        camera      : Optional[ Union[ CameraBase, List[CameraBase], Dict[Any,CameraBase] ] ]                  = None,
        controller  : Optional[ Union[ ControllerBase, List[ControllerBase], Dict[Any,ControllerBase] ] ]      = None,
    ) -> None: 
        """
        Processes incoming data from camera(s) to determine control(s) being sent to hardware via specified network(s)
        :param network: network object for sending control to hardware
        :param camera: camera object used to collect vision data
        :param controller: controller object used to determine control from network information and camera data 
        """


SelfThreadedStackBase = TypeVar("SelfThreadedStackBase", bound="ThreadedStackBase" )
class ThreadedStackBase(StackBase,_RohanThreading): 
    """
    Base class for an arbitrary camera(s) + controller(s) + network(s) stack
    :param config: configuration as rohan StackConfiguration() dataclass
    :param spin_intrvl: Inverse-frequency of spinning loop
    """
    
    _instance      = None

    def __init__( 
        self, 
        config      : Optional[StackConfiguration] = None,
        spin_intrvl : float = -1
    ):
        StackBase.__init__( 
            self,
            config=config, 
            spin_intrvl=spin_intrvl 
        )
        _RohanThreading.__init__( self )
        self.add_threaded_method( target=self.spin )

    def configure(
        self,
        config : Optional[StackConfiguration] = None
    ) -> None:
        """
        Configures the stack
        :param config: configuration as rohan StackConfiguration() dataclass
        """
        if not config is None:
            with self._instance_lock:
                StackBase.configure(self,config=config)


    def spin( self ) -> None:
        """
        Spin-up stack
        """
        spin_timer = IntervalTimer(interval=self.spin_intrvl)
        with Logger(self.config.log_filename) as logger, ExitStack() as stack: 
            _networks, _cameras, _controllers = self._enter_subcontexts( stack=stack, logger=logger ) 

            if isinstance(logger,Logger): 
                logger.write(
                    f'Spinning up stack',
                    process_name=self.process_name
                )
            
            while not self.sigterm.is_set():
                spin_timer.await_interval()
                self.process( 
                    network=_networks, 
                    camera=_cameras, 
                    controller=_controllers
                )

            if isinstance(logger,Logger): 
                    logger.write(
                        f'Spinning down stack',
                        process_name=self.process_name
                    )

    @classmethod
    def get_instance(cls):
        """
        Ensure singleton instance
        """
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """
        Create a new singleton instance
        """
        stop_instance_threads = False
        with cls._instance_lock:
            if isinstance( cls._instance, cls ) and not cls._instance.sigterm.is_set():
                stop_instance_threads = True
                
        if stop_instance_threads : cls._instance.stop_spin()
        with cls._instance_lock:
            cls._instance = cls()
        return cls._instance