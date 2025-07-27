
import logging
import pandas as pd
import yfinance as yf

class SplitAdjuster:
    """
    Adjusts the historical trade DataFrame for all stock splits that
    actually happened between the first and last trade in the CSV files.
    """

    def adjust_for_splits(self, df_trades: pd.DataFrame) -> pd.DataFrame:
        if df_trades.empty:
            return df_trades

        df_adj = df_trades.copy()

        for symbol in df_adj['Symbol'].unique():
            try:
                ticker = yf.Ticker(symbol)
                splits: pd.Series = ticker.splits

                if splits.empty:
                    continue

                
                symbol_trades = df_adj[df_adj['Symbol'] == symbol]
                trade_dates = pd.to_datetime(symbol_trades['Date/Time'])
                
                if trade_dates.dt.tz is not None:
                    trade_dates = trade_dates.dt.tz_localize(None)
                
                first_date = trade_dates.min().normalize()
                last_date = trade_dates.max().normalize()

                for split_date, ratio in splits.items():
                    
                    if hasattr(split_date, 'tz') and split_date.tz is not None:
                        split_date_naive = split_date.tz_localize(None)
                    else:
                        split_date_naive = split_date
                    
                    split_date_naive = pd.Timestamp(split_date_naive).normalize()
                    
                    
                    if not (first_date <= split_date_naive <= last_date):
                        continue

                    logging.info(f"Applying split adjustment: {symbol} {split_date_naive.strftime('%Y-%m-%d')} ratio {ratio}:1")

                    
                    trade_datetime_naive = pd.to_datetime(df_adj['Date/Time'])
                    if trade_datetime_naive.dt.tz is not None:
                        trade_datetime_naive = trade_datetime_naive.dt.tz_localize(None)
                    
                    mask = (df_adj['Symbol'] == symbol) & (trade_datetime_naive < split_date_naive)

                    df_adj.loc[mask, 'adjusted_quantity'] = (
                        df_adj.loc[mask, 'adjusted_quantity'] * ratio
                    )
                    df_adj.loc[mask, 'adjusted_price'] = (
                        df_adj.loc[mask, 'adjusted_price'] / ratio
                    )

            except Exception as e:
                logging.warning(f"Split adjustment failed for {symbol}: {e}")
                continue

        return df_adj
