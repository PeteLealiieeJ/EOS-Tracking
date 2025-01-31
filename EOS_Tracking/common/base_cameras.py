from abc                                import abstractmethod
from EOS_Tracking.common.base           import _EOSBase,_EOSThreading
from EOS_Tracking.common.logging        import Logger
from typing                             import TypeVar, Optional
from EOS_Tracking.common.type_aliases   import Resolution

SelfBaseCamera = TypeVar("SelfBaseCamera", bound="BaseCamera" )
class BaseCamera(_EOSBase):
    """
    Base class for an arbitrary camera model
    :param resolution: Pixel resolution of the camera's RGB channels
    :param fps: Frames-per-second (fps) of the camera's RGB channels
    :param logger: EOS-Tracker Logger() instance
    """

    process_name : str = "unnamed camera"
    resolution   : Resolution
    fps          : int
    logger       : Optional[Logger] = None

    def __init__(   
        self, 
        resolution  : Resolution,
        fps         : int,
        logger      : Optional[Logger] = None
    ):
        self.resolution = resolution
        self.fps        = fps
        self.logger     = logger

    def __enter__( self ):
        self.connect()
        if isinstance(self.logger,Logger): 
            self.logger.write(
                f'Camera Connected',
                process_name=self.process_name
            )
        return self
    
    def __exit__( self, exception_type, exception_value, traceback ):
        self.disconnect()
        if isinstance(self.logger,Logger): 
            self.logger.write(
                f'Camera Disconnected',
                process_name=self.process_name
            )
    
    @abstractmethod
    def connect( self ) -> None:
        """
        Connects to the camera's I/O
        """

    @abstractmethod
    def disconnect( self ) -> None:
         """
        Disconnect from the camera's I/O
        """

SelfBaseThreadedCamera = TypeVar("SelfBaseThreadedCameraModel", bound="BaseThreadedCamera" )
class BaseThreadedCamera(BaseCamera,_EOSThreading):
    """
    Base class for an arbitrary camera model spinning up a threaded method
    :param resolution: Pixel resolution of the camera's RGB channels
    :param fps: Frames-per-second (fps) of the camera's RGB channels
    :param logger: EOS-Tracker Logger() instance
    """

    process_name : str = "unnamed threaded camera"

    def __init__(   
        self, 
        resolution  : Resolution,
        fps         : int,
        logger      : Optional[Logger] = None
    ):
        BaseCamera.__init__(
            self,
            resolution=resolution,
            fps=fps,
            logger=logger
        )
        _EOSThreading.__init__( self )

    def __enter__( self ):
        BaseCamera.__enter__( self )
        self.start_spin()
        if isinstance(self.logger,Logger): 
            self.logger.write(
                f'Spinning up camera thread',
                process_name=self.process_name
            )
        return self
    
    def __exit__( self, exception_type, exception_value, traceback ):
        self.stop_spin()
        if isinstance(self.logger,Logger): 
            self.logger.write(
                f'Unravelling camera thread',
                process_name=self.process_name
            )
        BaseCamera.__exit__( self, exception_type, exception_value, traceback )


SelfBaseLidarCamera = TypeVar("SelfBaseLidarCamera", bound="BaseLidarCamera" )
class BaseLidarCamera(BaseCamera):
    """
    Base class for an arbitrary lidar camera model spinning up a threaded method
    :param resolution: Pixel resolution of the camera's RGB channels
    :param lidar_resolution: Pixel resolution of the camera's depth channel
    :param fps: Frames-per-second (fps) of the camera's RGB channels
    :param lidar_fps: Frames-per-second (fps) of the camera's depth channel
    :param logger: EOS-Tracker Logger() instance
    """

    process_name        : str = "unnamed lidar camera"
    lidar_resolution    : Resolution
    lidar_fps           : int

    def __init__(   
        self, 
        resolution : Resolution,
        lidar_resolution : Resolution,
        fps : int, 
        lidar_fps : int,
        logger : Optional[Logger] = None,  
    ):
        BaseCamera.__init__( 
            self,
            resolution=resolution, 
            fps=fps, 
            logger=logger 
        )
        self.lidar_resolution   = lidar_resolution
        self.lidar_fps          = lidar_fps


SelfBaseThreadedLidarCamera = TypeVar("SelfBaseThreadedLidarCamera", bound="BaseThreadedLidarCamera" )
class BaseThreadedLidarCamera(BaseThreadedCamera):
    """
    Base class for an arbitrary lidar camera model
    :param resolution: Pixel resolution of the camera's RGB channels
    :param lidar_resolution: Pixel resolution of the camera's depth channel
    :param fps: Frames-per-second (fps) of the camera's RGB channels
    :param lidar_fps: Frames-per-second (fps) of the camera's depth channel
    :param logger: EOS-Tracker Logger() instance
    """

    process_name        : str = "unnamed threaded lidar camera"
    lidar_resolution    : Resolution
    lidar_fps           : int

    def __init__(   
        self, 
        resolution : Resolution,
        lidar_resolution : Resolution,
        fps : int, 
        lidar_fps : int,
        logger : Optional[Logger] = None,  
    ):
        BaseThreadedCamera.__init__( 
            self,
            resolution=resolution, 
            fps=fps, 
            logger=logger 
        )
        self.lidar_resolution   = lidar_resolution
        self.lidar_fps          = lidar_fps