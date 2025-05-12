import os
import json

class Config:

  def __init__(self, path: str = None):
    self.path = path or os.path.join(os.getcwd(), 'config.json')
    self.config = self._load_config()
  
  def _load_config(self) -> dict:
    if not os.path.exists(self.path):
      raise FileNotFoundError(f"Config file not found: {self.path}")
    with open(self.path, "r") as file:
      try:
        return json.load(file)
      except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {self.path}") from e

  def get_config(self) -> dict:
    return self.config
