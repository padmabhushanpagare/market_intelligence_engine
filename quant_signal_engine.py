import pandas as pd
import numpy as np

class QuantSignalEngine:
    def __init__(self, data_path: str, spot_price: float = None):
        self.data_path = data_path
        self.spot_price = spot_price
        self.df = self._load_and_clean_data()

    def _load_and_clean_data(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.data_path)
            rename_map = {
                'strike': 'strike_price', 'option_type': 'option_type',
                'open_interest': 'open_interest', 'gamma': 'gamma',
                'active_underlying_price': 'spot_price'
            }
            if not set(rename_map.keys()).issubset(df.columns):
                return pd.DataFrame() # Return empty if wide-format or malformed
                
            df = df.rename(columns=rename_map)
            df['option_type'] = df['option_type'].map({'C': 'call', 'P': 'put'})
            df = df[df['open_interest'] > 0].copy()
            
            if self.spot_price is None and not df.empty:
                self.spot_price = df['spot_price'].iloc[0]
            return df
        except Exception as e:
            print(f"Ingestion Error: {e}")
            return pd.DataFrame()

    def calculate_net_gex(self) -> dict:
        if self.df.empty:
            return {"error": "No valid data."}

        calls = self.df[self.df['option_type'] == 'call'].copy()
        puts = self.df[self.df['option_type'] == 'put'].copy()

        calls['gex'] = calls['gamma'] * calls['open_interest'] * 100 * self.spot_price
        puts['gex'] = puts['gamma'] * puts['open_interest'] * 100 * self.spot_price * -1

        total_call_gex, total_put_gex = calls['gex'].sum(), puts['gex'].sum()
        net_gex_billions = (total_call_gex + total_put_gex) / 1e9

        # Strike-Level Profile
        combined = pd.concat([calls, puts])
        strike_profile = combined.groupby('strike_price')['gex'].sum().reset_index().sort_values('strike_price')
        strike_profile['cumulative_gex'] = strike_profile['gex'].cumsum()

        # True Gamma Flip (Zero Gamma Level) with Liquidity Window (+/- 15%)
        lower_bound, upper_bound = self.spot_price * 0.85, self.spot_price * 1.15
        active_strikes = strike_profile[
            (strike_profile['strike_price'] >= lower_bound) & 
            (strike_profile['strike_price'] <= upper_bound) & 
            (strike_profile['gex'] != 0)
        ].copy()
        
        gamma_flip = active_strikes.loc[active_strikes['cumulative_gex'].abs().idxmin(), 'strike_price'] if not active_strikes.empty else self.spot_price
        regime = "Low Volatility / Mean Reverting" if net_gex_billions > 0 else "High Volatility / Directional Trend"

        return {
            "net_gex_billions": round(net_gex_billions, 2),
            "dominant_exposure": "Calls" if total_call_gex > abs(total_put_gex) else "Puts",
            "implied_regime": regime,
            "gamma_flip_strike": gamma_flip,
            "strike_profile": strike_profile
        }