from abc                         import abstractmethod
from rohan.common.base           import _RohanBase,_RohanThreading
from rohan.common.logging        import Logger
from typing                      import TypeVar, Optional
from rohan.common.type_aliases   import Resolution

SelfCameraBase = TypeVar("SelfCameraBase", bound="CameraBase" )
class CameraBase(_RohanBase):
    """
    Base class for an arbitrary camera model
    :param resolution: Pixel resolution of the camera's RGB channels
    :param fps: Frames-per-second (fps) of the camera's RGB channels
    :param logger: rohan Logger() instance
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

SelfThreadedCameraBase = TypeVar("SelfThreadedCameraBaseModel", bound="ThreadedCameraBase" )
class ThreadedCameraBase(CameraBase,_RohanThreading):
    """
    Base class for an arbitrary camera model spinning up a threaded method
    :param resolution: Pixel resolution of the camera's RGB channels
    :param fps: Frames-per-second (fps) of the camera's RGB channels
    :param logger: rohan Logger() instance
    """

    process_name : str = "unnamed threaded camera"

    def __init__(   
        self, 
        resolution  : Resolution,
        fps         : int,
        logger      : Optional[Logger] = None
    ):
        CameraBase.__init__(
            self,
            resolution=resolution,
            fps=fps,
            logger=logger
        )
        _RohanThreading.__init__( self )

    def __enter__( self ):
        CameraBase.__enter__( self )
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
        CameraBase.__exit__( self, exception_type, exception_value, traceback )


SelfLidarCameraBase = TypeVar("SelfLidarCameraBase", bound="LidarCameraBase" )
class LidarCameraBase(CameraBase):
    """
    Base class for an arbitrary lidar camera model spinning up a threaded method
    :param resolution: Pixel resolution of the camera's RGB channels
    :param lidar_resolution: Pixel resolution of the camera's depth channel
    :param fps: Frames-per-second (fps) of the camera's RGB channels
    :param lidar_fps: Frames-per-second (fps) of the camera's depth channel
    :param logger: rohan Logger() instance
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
        CameraBase.__init__( 
            self,
            resolution=resolution, 
            fps=fps, 
            logger=logger 
        )
        self.lidar_resolution   = lidar_resolution
        self.lidar_fps          = lidar_fps


SelfThreadedLidarCameraBase = TypeVar("SelfThreadedLidarCameraBase", bound="ThreadedLidarCameraBase" )
class ThreadedLidarCameraBase(ThreadedCameraBase):
    """
    Base class for an arbitrary lidar camera model
    :param resolution: Pixel resolution of the camera's RGB channels
    :param lidar_resolution: Pixel resolution of the camera's depth channel
    :param fps: Frames-per-second (fps) of the camera's RGB channels
    :param lidar_fps: Frames-per-second (fps) of the camera's depth channel
    :param logger: rohan Logger() instance
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
        ThreadedCameraBase.__init__( 
            self,
            resolution=resolution, 
            fps=fps, 
            logger=logger 
        )
        self.lidar_resolution   = lidar_resolution
        self.lidar_fps          = lidar_fps