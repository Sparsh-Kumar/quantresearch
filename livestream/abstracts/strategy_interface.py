from abc import ABC, abstractmethod

class Strategy(ABC):
  @abstractmethod
  def process_order_book_data(self, bids = [], asks = []):
    pass

