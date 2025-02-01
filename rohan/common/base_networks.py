from abc                     import abstractmethod
from rohan.common.base       import _RohanBase, _RohanThreading
from rohan.common.logging    import Logger
from typing                  import Optional, TypeVar

SelfNetworkBase = TypeVar("SelfNetworkBase", bound="NetworkBase" )
class NetworkBase(_RohanBase):
    """
    Base class for an arbitrary network interface
    :param logger: rohan Logger() instance
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

SelfThreadedNetworkBase = TypeVar("SelfThreadedNetworkBase", bound="ThreadedNetworkBase" )
class ThreadedNetworkBase(NetworkBase,_RohanThreading):
    """
    Base class for an arbitrary network interface spinning up a threaded method
    :param logger: rohan Logger() instance
    """

    process_name : str = "unnamed threaded netowrk"
    
    def __init__( 
        self,
        logger : Optional[Logger] = None  
    ):
        NetworkBase.__init__(
            self,
            logger=logger
        )
        _RohanThreading.__init__( self )
    
    def __enter__( self ):
        NetworkBase.__enter__( self )
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
        NetworkBase.__exit__( self, exception_type, exception_value, traceback )
