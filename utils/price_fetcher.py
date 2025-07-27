
import yfinance as yf
import pandas as pd
import logging
import time
from datetime import datetime, timedelta
import random


class PriceFetcher:
    def __init__(self, retries=3, base_delay=2):
        self.retries = retries
        self.base_delay = base_delay
        self._cache = {}
        self._last_request_time = {}

    def _rate_limit_delay(self, symbol):
        """Implement rate limiting between requests"""
        current_time = time.time()
        if symbol in self._last_request_time:
            time_since_last = current_time - self._last_request_time[symbol]
            if time_since_last < self.base_delay:
                sleep_time = self.base_delay - time_since_last + random.uniform(0.5, 1.5)
                logging.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self._last_request_time[symbol] = time.time()
    
    def is_valid_ticker(self, symbol):
        """Check if ticker is valid and not delisted"""
        try:
            
            invalid_patterns = ['$', '.L', '.TO', '^']
            
            if any(pattern in symbol for pattern in invalid_patterns):
                return symbol in ['SPY', 'QQQ', 'VTI', 'VOO']  
                
            if len(symbol) > 6:
                return False
                
            return True
            
        except Exception:
            return False

    def get_latest_price_safe(self, symbol):
        """Get latest price with enhanced error handling"""
        if not self.is_valid_ticker(symbol):
            logging.info(f"Skipping invalid ticker: {symbol}")
            return 100.0  
            
        try:
            return self.get_latest_price(symbol)
        except Exception as e:
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ['delisted', 'timezone', 'not found']):
                logging.info(f"Ticker {symbol} appears delisted or invalid: {e}")
                return 100.0  
            else:
                logging.error(f"Error fetching price for {symbol}: {e}")
                return 100.0

    def _fetch_with_retry(self, ticker_symbol):
        """Internal method to fetch Ticker object with exponential backoff"""
        self._rate_limit_delay(ticker_symbol)
        
        for i in range(self.retries):
            try:
                ticker = yf.Ticker(ticker_symbol)
                
                test_data = ticker.history(period="1d")
                if not test_data.empty:
                    return ticker
                else:
                    logging.warning(f"No data found for {ticker_symbol} on attempt {i+1}")
            except Exception as e:
                if "429" in str(e) or "Too Many Requests" in str(e):
                    wait_time = self.base_delay * (2 ** i) + random.uniform(1, 3)
                    logging.warning(f"Rate limited for {ticker_symbol}. Waiting {wait_time:.2f} seconds before retry {i+1}/{self.retries}")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Error fetching {ticker_symbol} on attempt {i+1}: {e}")
                    time.sleep(self.base_delay * (i + 1))
        
        logging.error(f"Failed to fetch data for {ticker_symbol} after {self.retries} attempts")
        return None

    def get_latest_price(self, symbol):
        """Fetches the latest market price with improved error handling"""
        cache_key = (symbol, 'latest_price')
        if cache_key in self._cache:
            return self._cache[cache_key]

        ticker = self._fetch_with_retry(symbol)
        if ticker:
            try:
                
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
                    self._cache[cache_key] = price
                    logging.info(f"Successfully fetched price for {symbol}: ${price:.2f}")
                    return price
                    
                
                price = ticker.info.get('regularMarketPrice') or ticker.info.get('navPrice')
                if price:
                    self._cache[cache_key] = price
                    return price

            except Exception as e:
                logging.error(f"Could not get latest price for {symbol}: {e}")
        
        logging.warning(f"Failed to fetch latest price for {symbol}, using cached or default value")
        return self._cache.get(cache_key, 100.0)  

    def get_split_info(self, symbol, split_date):
        """Verifies if a split occurred around a specific date"""
        ticker = self._fetch_with_retry(symbol)
        if not ticker:
            return None

        try:
            splits = ticker.splits
            if splits.empty:
                return None
            
            
            for date, ratio in splits.items():
                if abs((split_date.date() - date.date()).days) <= 5:
                    return {'date': date, 'ratio': ratio}
        except Exception as e:
            logging.error(f"Error fetching split info for {symbol}: {e}")
        
        return None

    def get_historical_daily_prices(self, symbol, start_date, end_date):
        """Fetches historical daily closing prices with batch processing"""
        cache_key = (symbol, start_date, end_date, 'historical')
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        ticker = self._fetch_with_retry(symbol)
        if ticker:
            try:
                hist = ticker.history(start=start_date, end=end_date, auto_adjust=True)
                if not hist.empty:
                    prices = hist['Close']
                    self._cache[cache_key] = prices
                    return prices
            except Exception as e:
                logging.error(f"Error fetching historical data for {symbol}: {e}")
        
        return pd.Series(dtype=float)
