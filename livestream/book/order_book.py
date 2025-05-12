import os
from livestream.services.strategy_manager import StrategyManager

class OrderBook:
  def __init__(
    self,
    ticker:str,
    strategy_manager: StrategyManager,
    bids: list = [],
    asks: list = []
  ):
    self.ticker = ticker or 'btcusdt'
    self.strategy_manager = strategy_manager
    self.bids = bids or []
    self.asks = asks or []

  def create_order_book(self, order_book_data=None):
    order_book_data = order_book_data or {}
    self.bids = order_book_data.get('b', [])
    self.asks = order_book_data.get('a', [])
    self._consume_order_book_data()

  def register_strategy_manager(self, strategy_manager: StrategyManager):
    self.strategy_manager = strategy_manager

  def _clear_screen(self):
    os.system('cls' if os.name == 'nt' else 'clear')

  def _get_sorted_orders(self, orders, reverse=False, limit=None):
    filtered = [order for order in orders if float(order[1]) > 0]
    sorted_orders = sorted(filtered, key=lambda x: float(x[0]), reverse=reverse)
    return sorted_orders if limit is None else sorted_orders[:limit]

  def _consume_order_book_data(self):
    asks = self._get_sorted_orders(self.asks)
    bids = self._get_sorted_orders(self.bids, reverse=True)
    self.strategy_manager.update_all(bids, asks)

  def _display_order_book(self):
    self._clear_screen()
    order_book_str = f"{'Ask Price':>10} | {'Ask Size':>10} || {'Bid Price':>10} | {'Bid Size':>10}\n"
    order_book_str += "-" * 50 + "\n"
    
    asks = self._get_sorted_orders(self.asks)
    bids = self._get_sorted_orders(self.bids, reverse=True)
    max_rows = max(len(asks), len(bids))
    
    for i in range(max_rows):
      ask_price, ask_size = asks[i] if i < len(asks) else ("", "")
      bid_price, bid_size = bids[i] if i < len(bids) else ("", "")
      order_book_str += f"{str(ask_price):>10} | {str(ask_size):>10} || {str(bid_price):>10} | {str(bid_size):>10}\n"
      
    print(order_book_str)

  def _display_order_book_spread(self, depth=5):
    self._clear_screen()
    asks = self._get_sorted_orders(self.asks, limit=depth)
    bids = self._get_sorted_orders(self.bids, reverse=True, limit=depth)
    
    if not asks or not bids:
      return

    vw_ask_price = sum(float(price) * float(size) for price, size in asks) / sum(float(size) for _, size in asks)
    vw_bid_price = sum(float(price) * float(size) for price, size in bids) / sum(float(size) for _, size in bids)
    mid_price = (vw_ask_price + vw_bid_price) / 2
    spread_percentage = (vw_ask_price - vw_bid_price) / mid_price * 100
    
    if spread_percentage > 0.1:
      print(f"Spread: {spread_percentage:.2f}%")

  def __del__(self):
    pass

