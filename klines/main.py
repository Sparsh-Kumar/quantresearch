import os
from dotenv import load_dotenv
from klines import SyncKLines

load_dotenv()


def main():
  asset = 'BTC/USDT'
  config = {
    'mongoServerName': os.getenv('MONGODB_SERVER'),
    'mongoDatabaseName': os.getenv('MONGO_DATABASE'),
    'mongoCollectionName': asset.lower(),
    'ticker': asset,
    'timeframe': '1m',
  }
  syncKLines = SyncKLines(config)
  syncKLines.fetchOhlcvData()


if __name__ == '__main__':
  main()

