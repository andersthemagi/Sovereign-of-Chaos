"""
Represents a timer used to diagnose loading times. 

A majority of this code was adapted from the following source:
https://realpython.com/python-timer/
Please support their tutorials and blog!
"""
##############################################
# Package Imports
##############################################

import time

##############################################
# TimeError Exception Class
##############################################

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""

##############################################
# Timer Class
##############################################

class Timer:

  def __init__( self ):
    self._start_time = None

  ##############################################
  # Timer External Functions
  ##############################################

  def getTimeStr( self ) -> str :
    """
    Returns a formatted string with the current time for logging events.
    """
    return time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())

  def start( self ) -> None:
    """
    Start a new timer.
    """
    if self._start_time is not None:
        raise TimerError(f"Timer is running. Use .stop() to stop it")
    self._start_time = time.perf_counter()
    return 

  def stop( self ) -> str :
    """
    Stop the timer, and report the elapsed time. Returns value as a string in seconds.
    """
    if self._start_time is None:
      raise TimerError(f"Timer is not running. Use .start() to start it")

    elapsed_time = time.perf_counter() - self._start_time

    self._start_time = None
    txt = "{elapsed:.4f}"
    elapsed_time = txt.format( elapsed = elapsed_time ) 

    return elapsed_time

  # End of Timer Class

# End of File