"""
Support class used to handle database interactions.

Will not be useful at the moment, but later when changing from
remote to local hosting, a local mysql db will be imperative to
ensure bot is running at top speed when possible.
"""
##############################################
# Package Imports
##############################################

import mysql.connector
import os

from log import ConsoleLog
from typing import Iterable

##############################################
# Constants and Setup
##############################################

MODULE = "DATABASE"

DB_HOST = os.getenv( "DB_HOST" )
DB_NAME = os.getenv( "DB_NAME" )
DB_PASS = os.getenv( "DB_PASS" )
DB_USER = os.getenv( "DB_USER" )
READ_TAG = "r"
SEMICOLON = ";"

DEBUG = False

##############################################
# DB Class
##############################################

class DB:

  def __init__( self ):
    self.openDB = False
    self.db = None 
    self.cursor = None 
    self.logging = ConsoleLog()
    return 

  ##############################################
  # DB External Functions
  ##############################################

  def start( self ) -> None:
    """
    Allows the user to create a connection to the database
    """
    if self.checkOpenDB():
      self.openDBError()
      return 

    try:
      self.db = mysql.connector.connect(
        host = DB_HOST,
        user = DB_USER,
        password = DB_PASS,
        database = DB_NAME
      )
      self.cursor = self.db.cursor(buffered = True )
      self.openDB = True
      if DEBUG:
        self.logging.send( MODULE, f"{DB_NAME} at {DB_HOST} connected to successfully!")
    except Exception as e:
      self.throwException(e)

  def stop( self ) -> None :
    """
    Allows the user to close the connection to the database
    """
    if not self.checkOpenDB():
      self.notOpenDBError()
      return
    self.db.close()
    self.cursor.close()
    self.openDB = False 
    if DEBUG:
      self.logging.send( MODULE, f"{DB_NAME} at {DB_HOST} closed." )
    return

  def executeScript( self, scriptStr : str, vals : Iterable[list] = None ) -> None :

    if not self.checkOpenDB():
      self.notOpenDBError()
      return
    
    if DEBUG:
        self.logging.send( MODULE, f"Command(s): {scriptStr}" )
        self.logging.send( MODULE, f"Value(s): {vals}" )

    commandSuccessful = True
    try:
      if vals is None:
        self.cursor.execute(scriptStr);
      else:
        self.cursor.execute(scriptStr, vals)
    except Exception as e:
      self.throwException(e)
      commandSuccessful = False
      
    self.db.commit()

    if commandSuccessful:
      if DEBUG:
        self.logging.send( MODULE, "SQL command from string executed successfully!" )
    else:
      self.logging.send( MODULE, "ERROR: SQL command from string had trouble executing." )

    return

  def executeScriptFromFile( self, filename: str ) -> None:

    if not self.checkOpenDB():
      self.notOpenDBError()
      return

    file = open(filename, READ_TAG )
    sqlFile = file.read()
    file.close()

    sqlCommands = sqlFile.split( SEMICOLON )
    
    sqlCommands = sqlCommands[:-1]

    allCommandsSuccessful = True
    for command in sqlCommands:
      try:
        if DEBUG:
            self.logging.send( MODULE, f"Command: {command}" )
        self.cursor.execute(command)
        if DEBUG:
          self.logging.send( MODULE, f"SQL command in '{filename}' executed successfully!" )
      except Exception as e:
        self.throwException(e)
        allCommandsSuccessful = False
    
    self.db.commit()

    if allCommandsSuccessful:
      if DEBUG:
        self.logging.send( MODULE, f"All SQL commands in '{filename}' executed!" )
    else:
      self.logging.send( MODULE, f"ERROR: One or more SQL commands in '{filename}' did not execute successfully." )

    return

  ##############################################
  # DB Internal / Support Functions
  ##############################################

  def checkOpenDB( self ) -> bool :
    """
    Returns a boolean determining whether or not a connection
    has been established
    """
    if self.openDB:
      return True
    return False

  def openDBError( self ) -> None :
    """
    Sends an error on the console about a db connection already
    having been established.
    """
    self.logging.send( MODULE, "ERROR: Connection to DB has already been established. Use '.stop()' to close the connection before attempting again." )
    return 

  def notOpenDBError( self ) -> None :
    """
    Sends an error on the console about a db connection not yet
    being established.
    """
    self.logging.send( MODULE, "ERROR: Connection to DB has not yet been established. Use '.start()' to start a connection before attempting again." )
    return

  def throwException( self, exception: Exception ) -> None:
    exceptionStr = f"{type(exception).__name__}: {exception}"
    self.logging.send( MODULE, f"ERROR: Something went wrong executing a .sql script from string: \n{exceptionStr}")
    return

  # End of DB Class

# End of File
