"""
Neatly handles logging of information to the console.
"""
##############################################
# Package Imports
##############################################
from timer import Timer 

##############################################
# ConsoleLog Class
##############################################

class ConsoleLog:

  def __init__( self ):
    self.timer = Timer()
    return

  ##############################################
  # ConsoleLog External Functions
  ##############################################

  def printSpacer( self ) -> None :
    print( '------' )
    return

  def send( self, module_str: str , message_str: str ) -> None:
    """
    Outputs a formatted print statement to the console, indicating
    something that needs to be logged
    """
    print( f"{self.timer.getTimeStr()}[{module_str}] {message_str}" )
    return 

  # End of ConsoleLog Class

# End of File

