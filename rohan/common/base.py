import threading
from abc    import ABC, abstractmethod
from typing import Optional, List, Iterable, Any, Mapping, Callable

class _RohanBase(ABC):
    """
    Base Class for rohan Modules
    """
    def load(
        self,
        **kwargs,
    ):
        self.__dict__.update(kwargs)

class _RohanThreading(ABC):
    """
    Class for spinning off threads in rohan modules
    """

    sigterm         : threading.Event
    threads         : List[threading.Thread]
    _instance_lock  : threading.Lock = threading.Lock() 


    def __init__( self ):
        self.threads    = []
        self.sigterm    = threading.Event()

    def add_threaded_method( 
        self,
        target  : Callable[[],None],
        name    : Optional[str]                 = None,
        args    : Iterable[Any]                 = (),
        kwargs  : Optional[ Mapping[str, Any] ] = None,
    ):
        self.threads.append( 
            threading.Thread(
                target  = target,
                name    = name,
                args    = args,
                kwargs  = kwargs
            )
        )

    def start_spin( self ) -> None:
        """
        Signal to start threaded processes
        """
        self.sigterm.clear()
        for thread in self.threads:
            if isinstance(thread,threading.Thread):
                thread.start()

    def stop_spin( self ) -> None:
        """
        Signal to stop threaded processes
        """            
        self.sigterm.set()
        for thread in self.threads:
            if isinstance(thread,threading.Thread) and thread.is_alive():
                thread.join()