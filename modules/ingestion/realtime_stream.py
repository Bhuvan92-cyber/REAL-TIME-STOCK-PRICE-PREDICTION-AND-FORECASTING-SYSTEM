import time
import yfinance as yf
from threading import Thread
from modules.utils.logger import get_logger

logger = get_logger(__name__)

class RealTimeStreamer:
    """
    Real-time stock price streamer using yfinance.
    Note: Replace this with a WebSocket/API integration for true streaming.
    """

    def __init__(self, ticker: str, interval: int = 10):
        self.ticker = ticker
        self.interval = interval
        self.running = False

    def _fetch_latest(self):
        data = yf.Ticker(self.ticker).history(period="1d", interval="1m")
        if not data.empty:
            latest = data.tail(1)
            price = latest["Close"].values[0]
            logger.info(f"Real-time price for {self.ticker}: {price}")
            return price
        logger.warning("No data returned for realtime.")
        return None

    def start(self):
        self.running = True
        Thread(target=self._run).start()

    def _run(self):
        while self.running:
            try:
                self._fetch_latest()
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Error in RealTimeStreamer: {e}")

    def stop(self):
        self.running = False
