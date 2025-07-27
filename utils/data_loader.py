# utils/data_loader.py
import pandas as pd
import os
import glob
import logging

class DataLoader:
    def __init__(self, data_path):
        if not os.path.isdir(data_path):
            raise FileNotFoundError(f"Data directory not found: {data_path}")
        self.data_path = data_path
        logging.info(f"DataLoader initialized with path: {self.data_path}")

    def load_all_trades(self):
        csv_files = glob.glob(os.path.join(self.data_path, "*.csv"))
        if not csv_files:
            logging.warning(f"No CSV files found in {self.data_path}")
            return pd.DataFrame()

        all_trades = []
        for file in csv_files:
            try:
                df = pd.read_csv(file)
                
                # --- ROBUST DATA CLEANING TO FIX THE ERROR ---
                # Convert key columns to numeric, coercing errors to NaN (Not a Number)
                df['Date/Time'] = pd.to_datetime(df['Date/Time'], errors='coerce')
                df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
                df['T. Price'] = pd.to_numeric(df['T. Price'], errors='coerce')

                # Drop rows where essential data is missing after coercion
                df.dropna(subset=['Date/Time', 'Quantity', 'T. Price', 'Symbol'], inplace=True)

                all_trades.append(df)
            except Exception as e:
                logging.error(f"Error reading or processing {file}: {e}")
                continue
        
        if not all_trades: return pd.DataFrame()

        df_combined = pd.concat(all_trades, ignore_index=True)
        df_combined['adjusted_quantity'] = df_combined['Quantity']
        df_combined['adjusted_price'] = df_combined['T. Price']
        return df_combined.sort_values(by="Date/Time").reset_index(drop=True)
