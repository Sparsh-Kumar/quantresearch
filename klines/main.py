import os
import argparse
from dotenv import load_dotenv
from klines import SyncKLines

load_dotenv()

def main():

  parser = argparse.ArgumentParser(description="Sync Klines (OHLCV) Data to MongoDB")
  parser.add_argument('--ticker', type=str, required=True, help='Asset ticker symbol (e.g., BTC/USDT)')
  parser.add_argument('--timeframe', type=str, default='1m', help='Timeframe (e.g., 1m, 5m, 15m, 1h, 1d) supported by CCXT')
  
  args = parser.parse_args()

  config = {
    'mongoServerName': os.getenv('MONGODB_SERVER'),
    'mongoDatabaseName': os.getenv('MONGO_DATABASE'),
    'mongoCollectionName': args.ticker.replace('/', '_').lower(),
    'ticker': args.ticker.lower(),
    'timeframe': args.timeframe,
  }
  syncKLines = SyncKLines(config)
  syncKLines.fetchOhlcvData()


if __name__ == '__main__':
  main()

