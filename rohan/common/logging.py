from rohan.common.base   import _RohanThreading
from rohan.utils.timers  import IntervalTimer
from time                import time 
from typing              import Optional
from io                  import TextIOWrapper
from queue               import Queue, Full

class Logger(_RohanThreading):

    """
    Logger for rohan Modules
    :param filename: Optional file name for logger to write to (if None is provided, no file will be openneds)
    :param queue_size: Size of logger queue (defaults to inf)
    """
    process_name     : str = "logger"
    init_time        : float 
    filename         : Optional[str]            = None
    file             : Optional[TextIOWrapper]  = None
    log_queue        : Queue
    thread_intrvl    : float

    def __init__(
        self,
        filename        : Optional[str] = None,
        queue_size      : int           = -1,
        thread_intrvl   : float         = -1,
    ):
        _RohanThreading.__init__( self )
        self.init_time      = time()
        self.filename       = filename
        if self.filename is not None:
            try:
                self.file = open(self.filename,"w")
            except Exception as e:
                self.file = None
                self.write(
                    f'Failed to open {self.filename} with exception {e}',
                    process_name=self.process_name
                )
        self.log_queue      = Queue(maxsize=queue_size)
        self.thread_intrvl  = thread_intrvl
        self.add_threaded_method( target=self.spin )
        
    def __enter__( self ):
        self.start_spin()
        self.write(
            f'Spinning up thread',
            process_name=self.process_name
        )
        return self


    def __exit__( self, exception, exception_value, traceback ):
        self.write(
            f'Unravelling thread',
            process_name=self.process_name
        )
        self.stop_spin()
        if isinstance(self.file,TextIOWrapper):
            self.file.close()
        self.file = None


    def _format_msg( 
        self, 
        msg          : str,
        process_name : str = " ",
    ): 
        """
        Formater for incoming message 
        :param msg: Message for logger to write 
        :param process_name: Name of process writing message
        """
        return "[@{:.2f}] {} -> {} ".format( time() - self.init_time, process_name, msg )


    def spin( self ):
        thread_timer = IntervalTimer(interval=self.thread_intrvl)
        while not self.sigterm.is_set():
            while not self.log_queue.empty(): 
                thread_timer.await_interval()
                formatted_msg = self.log_queue.get()
                print( formatted_msg )
                if isinstance(self.file,TextIOWrapper):
                    try:
                        self.file.write( formatted_msg + "\n")
                    except Exception as e:
                        print(  
                            self._format_msg( 
                                msg=f"Attempt to write on {self.filename} raised exception {e}", 
                                process_name=self.process_name 
                            ) 
                        ) 


    def write(
        self,
        msg          : str,
        process_name : str = " ",
    ):
        """
        Write log information either to file or to console
        :param msg: Message for logger to write 
        :param process_name: Name of process writing message
        """
        try:
            self.log_queue.put( self._format_msg( msg=msg, process_name=process_name ), block=False  )
        except Full:
            # >> ISSUE: Possible consequence of finite sized queue, especially relatively small queues wrt traffic
            # >> TODO: Inform user that log queue was full and that message was therefore dropped
            pass