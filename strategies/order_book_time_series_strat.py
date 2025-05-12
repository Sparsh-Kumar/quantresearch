
import os
from livestream.abstracts.strategy_interface import Strategy

class OrderBookTimeSeries(Strategy):

  def process_order_book_data(self, bids=[], asks=[]):
    self.asks = asks
    self.bids = bids
    self._display_order_book(bids, asks)

  def _clear_screen(self):
    os.system('cls' if os.name == 'nt' else 'clear')

  def _display_order_book(self, bids = [], asks = []):
    self._clear_screen()
    order_book_str = f"{'Ask Price':>10} | {'Ask Size':>10} || {'Bid Price':>10} | {'Bid Size':>10}\n"
    order_book_str += "-" * 50 + "\n"
    
    max_rows = max(len(asks), len(bids))
    
    for i in range(max_rows):
      ask_price, ask_size = asks[i] if i < len(asks) else ("", "")
      bid_price, bid_size = bids[i] if i < len(bids) else ("", "")
      order_book_str += f"{str(ask_price):>10} | {str(ask_size):>10} || {str(bid_price):>10} | {str(bid_size):>10}\n"
      
    print(order_book_str)

