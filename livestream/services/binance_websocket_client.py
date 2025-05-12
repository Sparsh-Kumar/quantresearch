import aiohttp
import json
from datetime import datetime, timezone
from livestream.abstracts.websocket_client_interface import WebSocketClient
from livestream.book.order_book import OrderBook

class BinanceWebSocketClient(WebSocketClient):
  def __init__(
    self,
    url: str,
    ticker: str,
    order_book: OrderBook,
    check_latency: bool = False,
    latency_records: int = 500,
    session: aiohttp.ClientSession = None
  ):
    self.ws = None
    self.ticker = ticker or 'btcusdt'
    self.url = url
    self.order_book = order_book
    self.session = session
    self.check_latency = check_latency
    self.latency_records_total = latency_records
    self.latency_records_remaining = latency_records
    self.total_latency = 0
  
  async def on_connect(self):
    async with self.session.ws_connect(self.url, compress=15) as ws:
      await self.on_open(ws)
      async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
          await self.handle_message(ws, msg.data)
        elif msg.type == aiohttp.WSMsgType.ERROR:
          print('WebSocket Error:', msg)
          await self.on_close(ws)
          break
  
  async def on_open(self, ws):
    subscribe_message = {
      "method": "SUBSCRIBE",
      "params": [f"{self.ticker}@depth"],
      "id": 1
    }
    await ws.send_str(json.dumps(subscribe_message))

  async def handle_message(self, ws, message):
    data = json.loads(message)
    if self.check_latency:
      await self.check_latency_fn(ws, data)
    else:
      await self.on_message(data)

  async def on_message(self, data):
    print('Here')
    # self.order_book.create_order_book(data)
  
  async def check_latency_fn(self, ws, data):
    event_time = data.get('E')
    if event_time is None:
      return
    if self.latency_records_remaining <= 0:
      await self.on_close(ws)
      return

    event_time_dt = datetime.fromtimestamp(event_time / 1000, tz=timezone.utc)
    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    latency_ms = int((current_time - event_time_dt).total_seconds() * 1000)
    self.total_latency += latency_ms
    self.latency_records_remaining -= 1
    avg_latency = self.total_latency / (self.latency_records_total - self.latency_records_remaining)
    print(
      f"Total Latency: {self.total_latency} ms, "
      f"Records Remaining: {self.latency_records_remaining}, "
      f"Records Checked: {self.latency_records_total - self.latency_records_remaining}, "
      f"Average Latency: {avg_latency:.2f} ms"
    )

  async def on_close(self, ws):
    print("Connection closed")
    await ws.close()

  def get_average_latency(self) -> float:
    return self.total_latency / self.latency_records_total if self.latency_records_total else 0
