from abc                            import abstractmethod
from EOS_Tracking.common.base       import _EOSBase, _EOSThreading
from EOS_Tracking.common.logging    import Logger
from typing                         import Optional, TypeVar

SelfBaseNetwork = TypeVar("SelfBaseNetwork", bound="BaseNetwork" )
class BaseNetwork(_EOSBase):
    """
    Base class for an arbitrary network interface
    :param logger: EOS-Tracker Logger() instance
    """

    process_name    : str = "unnamed network"
    logger          : Logger

    def __init__( 
        self,
        logger : Optional[Logger] = None 
    ):
        self.logger = logger

    def __enter__( self ):
        self.connect()
        return self

    def __exit__( self, exception_type, exception_value, traceback ):
        self.disconnect()

    @ abstractmethod
    def connect( self ) -> None :
        """
        Connects network
        """

    @ abstractmethod
    def disconnect( self ) -> None: 
        """
        Disconnects network
        """

SelfBaseThreadedNetwork = TypeVar("SelfBaseThreadedNetwork", bound="BaseThreadedNetwork" )
class BaseThreadedNetwork(BaseNetwork,_EOSThreading):
    """
    Base class for an arbitrary network interface spinning up a threaded method
    :param logger: EOS-Tracker Logger() instance
    """

    process_name : str = "unnamed threaded netowrk"
    
    def __init__( 
        self,
        logger : Optional[Logger] = None  
    ):
        BaseNetwork.__init__(
            self,
            logger=logger
        )
        _EOSThreading.__init__( self )
    
    def __enter__( self ):
        BaseNetwork.__enter__( self )
        self.start_spin()
        if isinstance(self.logger,Logger): 
            self.logger.write(
                f'Spinning up thread',
                process_name=self.process_name
            )
        return self
    
    def __exit__( self, exception_type, exception_value, traceback ):
        self.stop_spin()
        if isinstance(self.logger,Logger): 
            self.logger.write(
                f'Unravelling thread',
                process_name=self.process_name
            )
        BaseNetwork.__exit__( self, exception_type, exception_value, traceback )
