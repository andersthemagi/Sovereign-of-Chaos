import mysql.connector
import os

DB_HOST = os.getenv( "DB_HOST" )
DB_NAME = os.getenv( "DB_NAME" )
DB_PASS = os.getenv( "DB_PASS" )
DB_USER = os.getenv( "DB_USER" )
READ_TAG = "r"
SEMICOLON = ";"

class DB:

  def __init__(self):
    self.openDB = False
    self.db = None 
    self.cursor = None 
    return 

  def start(self):
    try:
      self.db = mysql.connector.connect(
        host = DB_HOST,
        user = DB_USER,
        password = DB_PASS,
        database = DB_NAME
      )
      self.cursor = self.db.cursor(buffered = True )
      self.openDB = True
      print(f"{DB_NAME} at {DB_HOST} connected to successfully!")
    except Exception as e:
      self.throwException(e)

  def stop(self):
    if not self.checkOpenDB():
      return
    self.db.close()
    self.cursor.close()
    self.openDB = False 
    print(f"{DB_NAME} at {DB_HOST} closed.")
    return

  def checkOpenDB( self ):
    if self.openDB:
      return True
    return False

  def throwException( self, exception ):
    exceptionStr = f"{type(exception).__name__}: {exception}"
    print( f"Something went wrong executing a .sql script from string: \n{exceptionStr}" )

  def executeScript( self, scriptStr, vals = None ):

    if not self.checkOpenDB():
      return

    commandSuccessful = True
    try:
      if vals is None:
        self.cursor.execute(scriptStr);
      else:
        self.cursor.execute(scriptStr, vals)
      self.db.commit()
    except Exception as e:
      self.throwException(e)
      commandSuccessful = False 

    if commandSuccessful:
      print("SQL command from string executed successfully!")
    else:
      print("ERROR: SQL command from string had trouble executing.")

    return

  def executeScriptFromFile( self, filename ):

    if not self.checkOpenDB():
      return

    file = open(filename, READ_TAG )
    sqlFile = file.read()
    file.close()

    sqlCommands = sqlFile.split( SEMICOLON )

    allCommandsSuccessful = True
    for command in sqlCommands:
      try:
        self.cursor.execute(command)
        print(f"SQL command in '{filename}' executed successfully!")
      except Exception as e:
        self.throwException(e)
        allCommandsSuccessful = False 

    if allCommandsSuccessful:
      print(f"All SQL commands in '{filename}' executed!")
    else:
      print(f"ERROR: One or more SQL commands in '{filename}' did not execute successfully.")

    return