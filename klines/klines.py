
import sys
import ccxt
import time
import datetime
import pytz
from pymongo import MongoClient


class SyncKLines:
  def __init__(self, configObject = {}):
    self.mongoServerName = configObject['mongoServerName']
    self.mongoDatabaseName = configObject['mongoDatabaseName']
    self.mongoCollectionName = configObject['mongoCollectionName']
    self.ticker = configObject['ticker']
    self.timeframe = configObject['timeframe']
    self.databaseConnectionHandler = None
    self.entriesDone = 0

  def _setUpMongoDBConnection(self):
    try:
      mongoClient = MongoClient(self.mongoServerName)
      self.databaseConnectionHandler = mongoClient[self.mongoDatabaseName][self.mongoCollectionName]
      print(f'Mongo connection successfull ... {self.databaseConnectionHandler}')
    except Exception as e:
      print('Error : ', e)
      sys.stderr.write(e)
      sys.exit(1)

  def _msToIst(self, ms):
    utcDt = datetime.datetime.utcfromtimestamp(ms / 1000)
    ist = pytz.timezone('Asia/Kolkata')
    istDt = utcDt.replace(tzinfo=pytz.utc).astimezone(ist)
    return istDt.strftime('%Y-%m-%d %H:%M:%S')
  
  def fetchOhlcvData(self):
    binance = ccxt.binance()
    self._setUpMongoDBConnection()
    while True:
      self.entriesDone += 1
      currentTime = int(time.time())
      nextMinute = (currentTime // 60 + 1) * 60
      timeToSleep = nextMinute - currentTime + 1
      print(f'Sleeping for {timeToSleep} ....')
      time.sleep(timeToSleep)
      try:
        ohlcv = binance.fetch_ohlcv(self.ticker.upper(), timeframe=self.timeframe, limit=1)
        candle = ohlcv[-1]
        istTime = self._msToIst(candle[0])
        data = {
          'Name': self.ticker.upper(),
          'Time': istTime,
          'Open': candle[1],
          'High': candle[2],
          'Low': candle[3],
          'Close': candle[4],
          'Volume': candle[5]
        }
        self.databaseConnectionHandler.insert_one(data)
      except Exception as e:
        print('Error : ',e)
        sys.stderr.write(e)
        sys.exit(1)
    
  def __del__(self):
    pass

if __name__ == '__main__':
  pass
