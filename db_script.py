import mysql.connector as my_connector
from decouple import config


class CarrefourDB:
  def __init__(self,):
    self.__host = config('DB_HOST')
    self.__user = config('DB_USER')
    self.__password = config('DB_PASSWORD')
    self.database = "carrefour_sample"
    self.conn = None
    self.curr = None
  
  def connection(self):
    self.conn = my_connector.connect(host=self.__host, user=self.__user, password=self.__password)
    self.curr = self.conn.cursor(dictionary=True)
    self.curr.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
    self.conn.database = self.database
  
  def execute_query(self, query, params=None, many=False):
    if self.conn is None or not self.conn.is_connected():
      self.connection()
    
    try:
      if many:
        self.curr.executemany(query, params or [])
      else:
        self.curr.execute(query, params)
      
      if self.curr.with_rows:
        return self.curr.fetchall()
      
      self.conn.commit()
      return self.curr.rowcount
      
    except Exception as e:
      self.conn.rollback()
      raise RuntimeError(f'Query failed: {e}') from e


  def close_connection(self):
    if self.curr:
      self.curr.close()
    if self.conn and self.conn.is_connected():
      self.curr.close()
    self.curr = self.conn = None

  
  # use class as `with CarrefourDB() as db:`
  def __enter__(self):
    self.connection()
    return self
  
  def __exit__(self, exc_type, exc, tb):
    self.close_connection()
