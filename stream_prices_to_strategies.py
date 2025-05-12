import os
import asyncio
import aiohttp

from livestream.services.load_config import Config
from livestream.book.order_book import OrderBook
from livestream.services.strategy_manager import StrategyManager
from livestream.services.binance_websocket_client import BinanceWebSocketClient
from livestream.services.uv_loop import uv_event_loop

from strategies.order_book_time_series_strat import OrderBookTimeSeries

async def main():
  
  # Use the uv event loop instead of python's default event loop
  uv_event_loop()

  # Ticker for which we are creating strategy
  ticker = 'btcusdt'

  # Loading the configuration from 'config.json' file
  config_path = os.path.join(os.getcwd(), 'stream_prices_config.json')
  config = Config(config_path).get_config()

  # Define strategies
  strategies = [
    OrderBookTimeSeries()
  ]

  # Creating a strategy manager which will provide order book data to all strategies at once.
  strategy_manager = StrategyManager(strategies)

  # Creating an order book with the strategy manager
  order_book = OrderBook(
    ticker,
    strategy_manager
  )

  # Creating an instance of Binance web socket client and running it in async
  async with aiohttp.ClientSession() as session:
    binance_client = BinanceWebSocketClient(
      config['SPOT']['RAW_WEBSOCKET_STREAM_ENDPOINT_1'],
      ticker,
      order_book,
      session=session
    )
    await binance_client.on_connect()

if __name__ == "__main__":
  asyncio.run(main())
