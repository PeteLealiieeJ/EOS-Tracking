from EOS_Tracking.common.base       import _EOSBase, _EOSThreading
from abc                            import abstractmethod
from EOS_Tracking.common.logging    import Logger
from typing                         import Optional, TypeVar


SelfBaseController = TypeVar("SelfBaseController", bound="BaseController" )
class BaseController(_EOSBase):
    """
    Base class for an arbitrary manipulator controller
    :param logger: EOS-Tracker Logger() instance
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


SelfBaseThreadedController = TypeVar("SelfBaseThreadedController", bound="BaseThreadedController" )
class BaseThreadedController(BaseController,_EOSThreading):
    """
    Base class for an arbitrary manipulator controller spinning up a threaded method
    :param logger: EOS-Tracker Logger() instance
    """

    process_name : str = "unnamed threaded controller"
    
    def __init__( 
        self,
        logger : Optional[Logger] = None  
    ):
        BaseController.__init__(logger=logger)
        _EOSThreading.__init__( self )
    
    def __enter__( self ):
        BaseController.__enter__( self )
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
        BaseController.__exit__( self, exception_type, exception_value, traceback )
