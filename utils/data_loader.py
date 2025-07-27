import pandas as pd
import glob
import logging
from datetime import datetime

class DataLoader:
    def __init__(self, data_path='data/'):
        self.data_path = data_path
        
    def load_all_trades(self):
        """Load and merge all CSV trade files"""
        csv_files = glob.glob(f"{self.data_path}Stock_trading_*.csv")
        
        if not csv_files:
            raise FileNotFoundError("No trading CSV files found")
        
        all_trades = []
        
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                
                df = df[df['DataDiscriminator'] == 'Order']
                all_trades.append(df)
                logging.info(f"Loaded {len(df)} trades from {file}")
                
            except Exception as e:
                logging.error(f"Error loading {file}: {e}")
                continue
        
        if not all_trades:
            raise ValueError("No valid trade data found")
        
        
        combined_df = pd.concat(all_trades, ignore_index=True)
        
        
        combined_df['Date/Time'] = pd.to_datetime(combined_df['Date/Time'])
        
        
        numeric_columns = ['Quantity', 'T. Price', 'C. Price', 'Proceeds', 'Comm/Fee']
        for col in numeric_columns:
            combined_df[col] = pd.to_numeric(combined_df[col].astype(str).str.replace(',', ''), 
                                           errors='coerce')
        
        
        combined_df['adjusted_quantity'] = combined_df['Quantity']
        combined_df['adjusted_price'] = combined_df['T. Price']
        
        return combined_df.sort_values('Date/Time')
