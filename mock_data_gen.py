import pandas as pd
import numpy as np

def generate_spx_mock_chain(filename="spx_chain_eod.csv", spot_price=5100.50):
    """
    Generates a realistic mock options chain for SPX to test GEX calculations.
    Simulates Gamma concentration ATM and higher Open Interest at round strikes.
    """
    print(f"Generating mock options chain for SPX at Spot: {spot_price}")
    
    # Define a realistic strike range (e.g., +/- 300 points from spot)
    strikes = np.arange(4800, 5405, 5) 
    data = []

    for strike in strikes:
        # 1. Simulate Gamma (Highest ATM, tapering off ITM/OTM)
        # Using a simple Gaussian curve approximation for the gamma profile
        distance_from_spot = abs(strike - spot_price)
        base_gamma = 0.05 * np.exp(-0.5 * (distance_from_spot / 50)**2)
        
        # 2. Simulate Open Interest (Higher at round numbers like 5000, 5100)
        base_oi = np.random.randint(500, 5000)
        if strike % 100 == 0:
            base_oi += np.random.randint(10000, 30000) # Big round numbers have massive OI
        elif strike % 50 == 0:
            base_oi += np.random.randint(5000, 15000)

        # Append Call Data
        data.append({
            'strike_price': strike,
            'option_type': 'call',
            'open_interest': int(base_oi * np.random.uniform(0.8, 1.2)),
            'gamma': round(base_gamma * np.random.uniform(0.9, 1.1), 5)
        })

        # Append Put Data (Puts often have higher OI due to downside hedging)
        data.append({
            'strike_price': strike,
            'option_type': 'put',
            'open_interest': int(base_oi * np.random.uniform(1.0, 1.5)), 
            'gamma': round(base_gamma * np.random.uniform(0.9, 1.1), 5)
        })

    # Create DataFrame and save
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Successfully generated {len(df)} rows of options data in '{filename}'.")

# Run the generator
if __name__ == "__main__":
    generate_spx_mock_chain()