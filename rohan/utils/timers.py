from time       import perf_counter, sleep
from typing     import Optional

class IntervalTimer:

    """
    Timer for targetting certain process intervals -- call within loops to target loop frequencies
    :param interval: Target interval between calls
    """

    last_tick   : Optional[float] = None 

    def __init__( 
        self, 
        interval : float 
    ): 
        self.interval = interval

    def await_interval( self ):
        """
        Waits for the target interval to pass then updates last read time
        """
        if not self.last_tick is None:
            delta_t = perf_counter() - self.last_tick
            if delta_t < self.interval : sleep( self.interval - delta_t )
        self.last_tick = perf_counter()

    def check_interval( self ) -> bool:
        """
        Check that time interval has passed and overwrites last tick if it has
        :returns True if more time has passed since last call than interval, False otherwise 
        """
        if not self.last_tick is None:
            if perf_counter() - self.last_tick < self.interval :
                return False
        self.last_tick = perf_counter()
        return True 