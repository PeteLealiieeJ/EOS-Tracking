from rohan.common.base       import _RohanBase, _RohanThreading
from abc                     import abstractmethod
from rohan.common.logging    import Logger
from typing                  import Optional, TypeVar


SelfControllerBase = TypeVar("SelfControllerBase", bound="ControllerBase" )
class ControllerBase(_RohanBase):
    """
    Base class for an arbitrary manipulator controller
    :param logger: rohan Logger() instance
    """

    process_name    : str = "unnamed controller"
    logger          : Optional[Logger]

    def __init__( 
        self,
        logger : Optional[Logger] = None  
    ):
        self.logger = logger

    def __enter__( self ):
        self.init_controller()
        if isinstance(self.logger,Logger): 
            self.logger.write(
                f'Controller initialized',
                process_name=self.process_name
            )
        return self

    def __exit__( self, exception_type, exception_value, traceback ):
        self.deinit_controller()        
        if isinstance(self.logger,Logger): 
            self.logger.write(
                f'Controller cleaned-up',
                process_name=self.process_name
            )

    @abstractmethod
    def init_controller( self ):
        """
        Initializes controller
        """

    @abstractmethod
    def deinit_controller( self ):
        """
        Cleans up artifacts openned by controller initialization
        """


SelfThreadedControllerBase = TypeVar("SelfThreadedControllerBase", bound="ThreadedControllerBase" )
class ThreadedControllerBase(ControllerBase,_RohanThreading):
    """
    Base class for an arbitrary manipulator controller spinning up a threaded method
    :param logger: rohan Logger() instance
    """

    process_name : str = "unnamed threaded controller"
    
    def __init__( 
        self,
        logger : Optional[Logger] = None  
    ):
        ControllerBase.__init__(logger=logger)
        _RohanThreading.__init__( self )
    
    def __enter__( self ):
        ControllerBase.__enter__( self )
        self.start_spin()
        if isinstance(self.logger,Logger): 
            self.logger.write(
                f'Spinning up controller thread',
                process_name=self.process_name
            )
        return self
    
    def __exit__( self, exception_type, exception_value, traceback ):
        self.stop_spin()
        if isinstance(self.logger,Logger): 
            self.logger.write(
                f'Unravelling controller thread',
                process_name=self.process_name
            )
        ControllerBase.__exit__( self, exception_type, exception_value, traceback )
