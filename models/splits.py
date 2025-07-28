# models/splits.py (Enhanced Version)
import pandas as pd
import numpy as np
import yfinance as yf
import logging
from datetime import datetime, timedelta

class SplitAdjuster:
    def __init__(self):
        self.splits_cache = {}
        
    def adjust_for_splits(self, df_trades):
        """Enhanced split adjustment with better logging and validation"""
        if df_trades.empty:
            return df_trades
            
        # Create copies for adjustment
        df_adjusted = df_trades.copy()
        df_adjusted['split_adjusted'] = False
        
        # Group by symbol and process each
        for symbol in df_adjusted['Symbol'].unique():
            try:
                symbol_splits = self._get_splits_for_symbol(symbol)
                if symbol_splits.empty:
                    continue
                    
                symbol_mask = df_adjusted['Symbol'] == symbol
                symbol_trades = df_adjusted[symbol_mask].copy()
                
                # Apply split adjustments
                adjusted_trades = self._apply_splits_to_trades(symbol_trades, symbol_splits, symbol)
                df_adjusted.loc[symbol_mask] = adjusted_trades
                
            except Exception as e:
                logging.error(f"Error adjusting splits for {symbol}: {e}")
                continue
        
        return df_adjusted
    
    def _get_splits_for_symbol(self, symbol):
        """Get splits with caching and enhanced error handling"""
        if symbol in self.splits_cache:
            return self.splits_cache[symbol]
            
        try:
            ticker = yf.Ticker(symbol)
            splits = ticker.splits
            
            if splits.empty:
                self.splits_cache[symbol] = pd.Series(dtype=float)
                return pd.Series(dtype=float)
            
            # Convert to timezone-naive if needed
            if hasattr(splits.index, 'tz') and splits.index.tz is not None:
                splits.index = splits.index.tz_localize(None)
                
            # Filter splits from last 10 years to avoid very old splits
            cutoff_date = datetime.now() - timedelta(days=3650)
            recent_splits = splits[splits.index >= cutoff_date]
            
            self.splits_cache[symbol] = recent_splits
            logging.info(f"Found {len(recent_splits)} recent splits for {symbol}")
            
            return recent_splits
            
        except Exception as e:
            logging.error(f"Error fetching splits for {symbol}: {e}")
            self.splits_cache[symbol] = pd.Series(dtype=float)
            return pd.Series(dtype=float)
    
    def _apply_splits_to_trades(self, trades, splits, symbol):
        """Apply split adjustments to trades with detailed logging"""
        if splits.empty:
            return trades
            
        trades = trades.copy()
        trades['adjusted_quantity'] = trades['Quantity'].astype(float)
        trades['adjusted_price'] = trades['T. Price'].astype(float)
        
        for split_date, split_ratio in splits.items():
            try:
                # Convert trade dates to datetime for comparison
                trade_dates = pd.to_datetime(trades['Date/Time'])
                
                # Find trades before split date
                pre_split_mask = trade_dates.dt.normalize() < split_date.normalize()
                
                if pre_split_mask.any():
                    # Adjust quantity (multiply by split ratio)
                    trades.loc[pre_split_mask, 'adjusted_quantity'] *= float(split_ratio)
                    # Adjust price (divide by split ratio)  
                    trades.loc[pre_split_mask, 'adjusted_price'] /= float(split_ratio)
                    trades.loc[pre_split_mask, 'split_adjusted'] = True
                    
                    affected_count = pre_split_mask.sum()
                    logging.info(f"Applied {split_ratio}:1 split for {symbol} on {split_date.date()}, affected {affected_count} trades")
                    
            except Exception as e:
                logging.error(f"Error applying split {split_ratio} for {symbol} on {split_date}: {e}")
                continue
        
        return trades
