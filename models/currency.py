
import yfinance as yf
import logging
from datetime import date

class CurrencyConverter:
    def __init__(self):
        self._rate_cache = {}

    def _get_rate(self, from_curr, to_curr):
        """Fetches and caches the exchange rate for a currency pair."""
        if from_curr == to_curr:
            return 1.0

        today = date.today()
        
        pair = f"{from_curr}{to_curr}=X"
        cache_key = (pair, today)

        if cache_key in self._rate_cache:
            return self._rate_cache[cache_key]
        
        try:
            ticker = yf.Ticker(pair)
            rate = ticker.history(period='1d')['Close'].iloc[0]
            if rate:
                self._rate_cache[cache_key] = rate
                return rate
        except IndexError: 
            logging.warning(f"Could not fetch direct rate for {pair}, trying inverse.")
        except Exception as e:
            logging.warning(f"Failed to fetch direct rate for {pair}: {e}")

        
        inverse_pair = f"{to_curr}{from_curr}=X"
        cache_key = (inverse_pair, today)
        if cache_key in self._rate_cache:
            return 1 / self._rate_cache[cache_key]

        try:
            ticker = yf.Ticker(inverse_pair)
            rate = ticker.history(period='1d')['Close'].iloc[0]
            if rate:
                self._rate_cache[cache_key] = rate
                return 1 / rate
        except Exception as e:
            logging.error(f"Failed to fetch inverse rate for {inverse_pair}: {e}")
            return None

    def convert(self, amount, from_curr, to_curr):
        """Converts an amount from one currency to another."""
        if from_curr == to_curr:
            return amount

        rate = self._get_rate(from_curr, to_curr)

        
        if rate is None and from_curr != 'USD' and to_curr != 'USD':
            logging.info(f"Pivoting via USD for {from_curr} to {to_curr}")
            usd_amount = self.convert(amount, from_curr, 'USD')
            if usd_amount:
                return self.convert(usd_amount, 'USD', to_curr)
            else:
                return None
        
        if rate:
            return amount * rate
        
        logging.error(f"Conversion failed for {from_curr} to {to_curr}")
        return None
