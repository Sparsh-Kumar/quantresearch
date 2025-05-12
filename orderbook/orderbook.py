import json
import os
import requests
import aiohttp
import asyncio
import uvloop
import argparse
from datetime import datetime, timezone

config = {}
with open("config.json", "r") as file:
  config = json.load(file)

WEBSOCKET_STREAM_ENDPOINT = config['SPOT']['RAW_WEBSOCKET_STREAM_ENDPOINT_1']
REST_API_ENDPOINT = config['SPOT']['REST_API_ENDPOINT']

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class BinanceWebSocketClient:

  def __init__(
    self, url = '',
    ticker='btcusdt',
    orderBook = None,
    checkLatency = False,
    checkLatencyRecords = 500,
    session = None
  ):
    self.ws = None
    self.ticker = ticker
    self.url = f'{url}/{ticker}@depth@100ms'
    self.orderBook = orderBook
    self.totalLatency = 0
    self.checkLatency = checkLatency
    self.checkLatencyRecords = checkLatencyRecords
    self.checkLatencyRecordsCopy = checkLatencyRecords
    self.session = session

  async def onConnect(self):
    async with self.session.ws_connect(self.url, compress=15) as ws:
      await self.onOpen(ws)
      async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
          data = msg.data
          if self.checkLatency:
            await self.onCheckLatency(ws, data)
          else:
            await self.onMessage(ws, data)
        elif msg.type == aiohttp.WSMsgType.ERROR:
          print('WebSocket Error:', msg)
          await self.onClose(ws)
          break

  async def onOpen(self, ws):
    subscribe_message = {
      "method": "SUBSCRIBE",
      "params": [f"{self.ticker}@depth"],
      "id": 1
    }
    await ws.send_str(json.dumps(subscribe_message))

  async def onMessage(self, ws, message):
    data = json.loads(message)
    self.orderBook.create(data)

  async def onCheckLatency(self, ws, message):
    data = json.loads(message)

    event_time = data.get('E')
    if event_time is None:
      return

    if (not self.checkLatencyRecords):
      await self.onClose(ws)
      return

    eventTime = datetime.fromtimestamp(data['E'] / 1000, tz=timezone.utc)
    currentTime = datetime.utcnow().replace(tzinfo=timezone.utc)
    timeDiffInMs = int((currentTime - eventTime).total_seconds() * 1000)
    self.totalLatency += timeDiffInMs
    self.checkLatencyRecords -= 1
    averageLatency = self.totalLatency / (self.checkLatencyRecordsCopy - self.checkLatencyRecords)
    print(f'Total Latency = {self.totalLatency}, Records Remaining = {self.checkLatencyRecords}, Records Checked = {self.checkLatencyRecordsCopy - self.checkLatencyRecords}, Average Latency = {averageLatency}')

  async def onClose(self, ws):
    print("Connection closed")
    await ws.close()
    return

  def getAverageLatency(self):
    return self.totalLatency / self.checkLatencyRecordsCopy


class OrderBook:

  def __init__(self, url = '', ticker = 'btcusdt', limit = 1000, bids = [], asks = []):
    self.bids = bids
    self.asks = asks
    self.ticker = ticker
    self.depthData = {}
    self.url = f'{url}/depth?symbol={self.ticker.upper()}&limit={limit}'
  
  def create(self, orderBookData: dict):
    if 'b' in orderBookData and 'a' in orderBookData:
      self.bids = orderBookData['b']
      self.asks = orderBookData['a']
      self.display_order_book()

  def display_order_book_spread(self):
    os.system('cls' if os.name == 'nt' else 'clear')

    asks = sorted(
      (ask for ask in self.asks if float(ask[1]) > 0),
      key=lambda x: float(x[0])
    )[:5] if self.asks else []

    bids = sorted(
      (bid for bid in self.bids if float(bid[1]) > 0),
      key=lambda x: float(x[0]),
      reverse=True
    )[:5] if self.bids else []

    if (len(asks) and len(bids)):
      vwAskPrice = sum(float(price) * float(volume) for price, volume in asks) / sum(float(volume) for _, volume in asks)
      vwBidPrice = sum(float(price) * float(volume) for price, volume in bids) / sum(float(volume) for _, volume in bids)
      vwSpread = vwAskPrice - vwBidPrice
      midPrice = (vwAskPrice + vwBidPrice) / 2
      spreadPercentage = (vwSpread / midPrice) * 100
      if (spreadPercentage > 0.1):
        print(spreadPercentage)

  def display_order_book(self):
    os.system('cls' if os.name == 'nt' else 'clear')
    order_book_str = f"{'Ask Price':>10} | {'Ask Size':>10} || {'Bid Price':>10} | {'Bid Size':>10}\n"
    order_book_str += "-" * 50 + "\n"
    
    asks = sorted(
      (ask for ask in self.asks if float(ask[1]) > 0),
      key=lambda x: float(x[0])
    ) if self.asks else []

    bids = sorted(
      (bid for bid in self.bids if float(bid[1]) > 0),
      key=lambda x: float(x[0]),
      reverse=True
    ) if self.bids else []

    max_rows = max(len(asks), len(bids))
    for i in range(max_rows):
      ask_price, ask_size = asks[i] if i < len(asks) else ("", "")
      bid_size, bid_price = bids[i] if i < len(bids) else ("", "")
      order_book_str += f"{str(ask_price):>10} | {str(ask_size):>10} || {str(bid_size):>10} | {str(bid_price):>10}\n"
    print(order_book_str)

  def get_orderbook_depth(self):

    depthData = {}
    depthResponse = requests.get(self.url)
    if depthResponse.status_code == 200:
      depthData = depthResponse.json()
    return depthData

async def main():
  parser = argparse.ArgumentParser(
    description='Low latency order book live streaming.'
  )
  parser.add_argument(
    "--ticker",
    type=str,
    required=True,
    help="Ticker symbol (e.g., btcusdt, ethusdt)"
  )
  parser.add_argument(
    "--check-latency",
    action="store_true",
    help="Enable latency checking (default: disabled)"
  )
    
  args = parser.parse_args()

  async with aiohttp.ClientSession() as session:
    orderBook = OrderBook(REST_API_ENDPOINT, args.ticker)
    client = BinanceWebSocketClient(
      WEBSOCKET_STREAM_ENDPOINT,
      args.ticker,
      orderBook,
      checkLatency=args.check_latency,
      session=session
    )
    await client.onConnect()
    print(client.getAverageLatency())

if __name__ == "__main__":
  asyncio.run(main())
