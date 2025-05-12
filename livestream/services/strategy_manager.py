

class StrategyManager:

  def __init__(self, strategies = []):
    self.strategies = strategies

  def register_strategy(self, strategy):
    self.strategies.append(strategy)

  def update_all(self, bids = [], asks = []):
    for strategy in self.strategies:
      strategy.process_order_book_data(bids, asks)

  def __del__(self):
    pass

