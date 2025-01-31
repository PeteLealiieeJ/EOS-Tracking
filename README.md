# EOS-Tracking 
This repository provides a simple structure for interfacing and spinning up components of manipulator systems that actuate vision sensors. In our experience, setting up hardware communication in manipulated camera systems often involves an identical workflow across various system configurations. This observation has encouraged us to present a python package which allows users to approach interfacing these components in a simple and modular fashion. 

### **Table of Contents**    
  * [1 | Requirements](#1--requirements)
  * [2 | Installation](#2--installation)
  * [3 | Functionality](#3--functionality)
  * [4 | Usage](#4--usage)
  * [5 | Validation](#5--validation)

## 1 | Requirements 
###  1.1 | Basic Functionality 
The functionality in this repository requires **Python 3.7+** and depends on the following package:

1. [numpy](https://pypi.org/project/numpy/)

```console
$ python -m pip install numpy
```

## 2 | Installation
To install this repository as a python package, the following is additionally required:

6. [setuptools](https://pypi.org/project/setuptools/)

```console
$ python -m pip install setuptools
```

###  2.1 | Local Installation 
As this project is not yet uploaded to the Python Package Index (PyPI) it is, many times, useful to install this package locally via pip:

```ShellSession
$ cd <WORKSPACE>
$ git clone https://github.com/PeteLealiieeJ/EOS-Tracking.git -b <VERSION>
$ cd EOS-Tracking
$ python -m pip install .
```

where `<WORKSPACE>` location is up to the user and a `<VERSION>` can be found in the the tags list on the associated github page

###  2.2 | Pip installation 
- [ ] NOT YET IMPLEMENTED

## 3 | Functionality

###  3.1 | Abstraction and Inhertitance as a Tool 
The basic functionality revolves around a basic workflow structured through the base parent classes provided in `EOS_Tracking/common/`. Inheriting these class when creating new models for different system configurations ensures communications channels are consisent when swapping system components. For example, `base_cameras.py` acts as a parent class for an arbitrary camera model in the following:

```Python
class ExampleCamera(BaseCamera):
    """
    An Example 
    """

    def __init__(
        self,
        resolution          : Resolution,
        fps                 : int,
        **config_kwargs
    ):
        BaseCamera.__init__( 
            resolution=resolution, 
            fps=fps, 
        )
        self.load( **config_kwargs )

    def connect( self, **connection_kwargs ) -> None:
        """
        Abstract Method defined in Base class which instructs users to specify how to connect to this camera's stream
        """

    def disconnect( self, **disconnect_kwargs ) -> None:
        """
        Abstract Method defined in Base class which instructs users to specify how to connect to disconnect from this camera's stream
        """
        
    def get_frame( self, **kwargs ):
        """
         Method defined by user which instructs users to specify how to provide the camera data to the stack
        """
```
The abstract methods `connect()` and `disconnect()`, instaniated by the parent class, are all sensor specific and needed to start and stop data collection for all applications; However, the underlying transfer of data to the stack can be handled arbitrarily and has been defined in the base class `BaseCamera` -- which handles things such as object contextualization, data packaging and transmission, and logging *(to be added later)*.

###  3.2 | Abstract Methods for Actuated Camera Systems 
The above approach to interfacing system components, again, provides users a modular structure for system components and allows for a more compressed approach when connecting system components. The abstract methods that must be defined by the user for each of the provided base classes are listed below:

- `BaseCamera`
    - Note: `__init__()` must provide the `BaseCamera.__init__()` initializer with the following kwargs:
        - resolution : tuple[int,int]
        - fps: int
    - `connect()` : connects to camera data stream
    - `disconnect()` : disconnects from camera data stream
- `BaseThreadedCamera`
    - Note: `__init__()` must provide the `BaseCamera.__init__()` initializer with the following kwargs:
        - resolution : tuple[int,int]
        - fps: int
    - `connect()` : connects to camera data stream
    - `disconnect()` : disconnects from camera data stream
    - `spin()` : process that should run in seperate thread (thread handling found in `_EOSThreading`)
- `BaseLidarCamera` 
    - Note: `__init__()` must provide the `BaseLidarCamera.__init__()` initializer with the following kwargs:
        - resolution : tuple[int,int]
        - lidar_resolution : tuple[int,int]
        - fps: int
        - lidar_fps : int
    - `connect()` : connects to camera data stream
    - `disconnect()` : disconnects from camera data stream
- `BaseThreadedLidarCamera` 
    - Note: `__init__()` must provide the `BaseLidarCamera.__init__()` initializer with the following kwargs:
        - resolution : tuple[int,int]
        - lidar_resolution : tuple[int,int]
        - fps: int
        - lidar_fps : int
    - `connect()` : connects to camera data stream
    - `disconnect()` : disconnects from camera data stream
    - `spin()` : process that should run in seperate thread (thread handling found in `_EOSThreading`)
- `BaseController`
    - Note: `__init__()` must provide the `super().__init__()` initializer with the following kwargs:
        - None
    - `init_controller()` : initializes and/or connects controller 
    - `deinit_controller()` : cleans-up artifacts instantiated by controller initialization
- `BaseThreadedController`
    - Note: `__init__()` must provide the `super().__init__()` initializer with the following kwargs:
        - None
    - `init_controller()` : initializes and/or connects controller 
    - `deinit_controller()` : cleans-up artifacts instantiated by controller initialization
    - `spin()` : process that should run in seperate thread (thread handling found in `_EOSThreading`)
- `BaseNetwork`
    - Note: `__init__()` must provide the `super().__init__()` initializer with the following kwargs:
        - None
    - `connect()` : connects to network
    - `disconnect()` : disconnects from network
- `BaseThreadedNetwork`
    - Note: `__init__()` must provide the `super().__init__()` initializer with the following kwargs:
        - None
    - `connect()` : connects to network
    - `disconnect()` : disconnects from network
    - `spin()` : process that should run in seperate thread (thread handling found in `_EOSThreading`)
- `BaseStack`
    - `process()` : process the data coming from the camera stream -- determines control and sends control signal using provided network, camera and controller contexts
- `BaseThreadedStack`
    - `process()` : process the data coming from the camera stream -- determines control and sends control signal using provided network, camera and controller contexts
    - `spin()` : process that should run in seperate thread (thread handling found in `_EOSThreading`)

> [!IMPORTANT]
> The threaded prefix implies that the user will spin off a threaded process for the component -- which will be spun up when the context is entered when the stack spins up

## 4 | Usage 

### 4.1 | Passing Configuration through the Stack
After defining specific models for system components as explained in the above section, users must provide the stack with the configuration parameters for all stack sub-systems. This can be done by importing the dataclass structure **StackConfiguration** from ***EOS_Tracking.data.classes***:

```Python
from EOS_Tracking.data.classes import StackConfiguration
```

The stack configuration has the following members, with associated meaning:
- `log_filename`
    - file location for the logger to write to
- `network_class`
    - specifies the class for the camera model being used
- `camera_config`
    - the camera configuration parameters for specified camera model
- `controller_class`
    - specifies the class for the controller model being used
- `network_config`
    - the controller configuration parameters for the specified controller model
- `network_class`
    - specifies the class for the network interface being used
- `network_config`
    - the network configuration parameters for specified class/model

It is most times simplier to store these specifications in a .json file and load it at runtime.

### 4.2 | Spinning Up and Down Stack

After specifying and loading the unthreaded stack configuration, the system can be spun up in the following:

```Python
config = StackConfiguration()
# ...
# Load configuration parameters
# ...
stack = ExampleStack( config=config )
stack.spin()
```
This system may be spun down cleanly using `cntl+c`. On the other hand, the threaded stack should be spun up and down with the following, assuming a singleton instance:

```Python
config = StackConfiguration()
# ...
# Load configuration parameters
# ...
ExampleThreadedStack.get_instance()
ExampleThreadedStack.get_instance().configure(config=config)
ExampleThreadedStack.get_instance().start_spin()
```
This system may be spun down cleanly using the `stop_spin()` method.
```Python
ExampleThreadedStack.get_instance().stop_spin()
```

## 5 | Validation
As this package handles interactions between hardware components, our validation procedure is carried out through a baseline system in house. In many ways, this makes it difficult to validate contributions. However, when possible, we validate code on the pan-tilt camera system -- pictured below -- using pytest and the following debug files found at this repository:

- [ ] NOT YET IMPLEMENTED
