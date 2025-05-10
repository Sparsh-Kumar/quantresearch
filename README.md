# QuantResearch

A modular quantitative research and trading system focused on real-time order book strategies, candlestick data storage, backtesting, and financial research.

---

## 📂 Project Structure

| Folder | Description |
|:-------|:------------|
| **backtesting/** | Backtesting of trading strategies using the `Backtesting.py` framework. |
| **klines/** | Scripts to synchronize (e.g., 1m, 5m, 15m, 1h, 1d) timeframe data supported by CCXT candlestick (OHLCV) data from exchanges into MongoDB for historical analysis and backtesting. |
| **orderbook/** | Low-latency order book streaming using Binance WebSocket APIs, built for high-frequency data capture. |
| **research/** | Research notebooks for statistical analysis, regime detection, and exploration of new strategies. |
| **strategies/** | Core trading strategies that consume real-time low latency order book data from **orderbook** module for signal generation and execution. |

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Sparsh-Kumar/quantresearch.git
cd quantresearch
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
```

### 3. Enabling Virtual Environment
```bash
source ./venv/bin/activate
```
### 4. Install dependencies
```bash
pip install -r requirements.txt
```


