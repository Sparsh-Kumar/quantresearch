from abc import ABC, abstractmethod

class WebSocketClient(ABC):
  @abstractmethod
  async def on_connect(self):
    pass
  @abstractmethod
  async def on_open(self, ws = None):
    pass
  @abstractmethod
  async def on_message(self, ws = None, message = ''):
    pass
  @abstractmethod
  async def check_latency_fn(self, ws = None, message = ''):
    pass
  @abstractmethod
  async def on_close(self, ws = None):
    pass

