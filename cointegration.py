import pandas as pd
import numpy as np
import os
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm


# Function to calculate half-life of mean reversion
def calculate_half_life(spread):
    df_spread = pd.DataFrame(spread, columns=["spread"])
    spread_lag = df_spread.spread.shift(1)
    spread_lag.iloc[0] = spread_lag.iloc[1]
    spread_ret = df_spread.spread - spread_lag
    spread_ret.iloc[0] = spread_ret.iloc[1]
    spread_lag2 = sm.add_constant(spread_lag)
    model = sm.OLS(spread_ret, spread_lag2)
    res = model.fit()
    halflife = round(-np.log(2) / res.params.iloc[1], 0)
    return halflife


def find_cointegrated_pairs(price_data):
    # Load csv file 
    df_market_prices = pd.read_csv(price_data)
    
    # Remove the timestamp column for analysis
    prices = df_market_prices.drop(columns=[df_market_prices.columns[0]])
    
    # Initialize an empty list to store the cointegrated pairs
    cointegrated_pairs = []
    
    # Get the list of asset symbols
    symbols = prices.columns
    
    # Iterate over each combination of pairs
    for i in range(len(symbols)):
        for j in range(i+1, len(symbols)):
            series_1 = prices[symbols[i]]
            series_2 = prices[symbols[j]]
            
            # Perform the cointegration test
            score, pvalue, _ = coint(series_1, series_2)
            
            # If the p-value is less than 0.05, consider the pair cointegrated
            if pvalue < 0.05:
                # Calculate the hedge ratio
                model = sm.OLS(series_1, series_2).fit()
                hedge_ratio = model.params.iloc[0]

                # Calculate the spread adjusted by the hedge ratio
                spread = series_1 - hedge_ratio * series_2

                # Calculate the half life (Ornstein-Uhlenbeck process) 
                half_life = calculate_half_life(spread)

                # Append the pair and their hedge ratio to the list
                if half_life <= 100 and half_life > 0:
                    cointegrated_pairs.append({
                    'Base': symbols[i],
                    'Quote': symbols[j],
                    'HedgeRatio': hedge_ratio,
                    'HalfLife': half_life,
                    'Score': score,
                    'Pvalue': pvalue
                })
    
    # Convert the list of cointegrated pairs into a DataFrame
    df_cointegrated_pairs = pd.DataFrame(cointegrated_pairs)
    df_cointegrated_pairs.to_csv('cointegrated_pairs.csv', index=False)

    return df_cointegrated_pairs



def update_hedge_ratios(price_data_file, existing_pairs_file):
    if not os.path.exists(existing_pairs_file):
        return
    # Load new price data and existing pairs
    df_market_prices = pd.read_csv(price_data_file).tail(100)
    existing_pairs = pd.read_csv(existing_pairs_file)

    # Remove the timestamp column for analysis
    prices = df_market_prices.drop(columns=[df_market_prices.columns[0]])
    
    # Iterate over each existing cointegrated pair to update its hedge ratio
    for index, row in existing_pairs.iterrows():
        base_asset = row['Base']
        quote_asset = row['Quote']
        
        series_1 = prices[base_asset]
        series_2 = prices[quote_asset]
        
        # Recalculate the hedge ratio
        model = sm.OLS(series_1, series_2).fit()
        hedge_ratio = model.params.iloc[0]
        
        # Update the hedge ratio in the existing_pairs DataFrame
        existing_pairs.at[index, 'HedgeRatio'] = hedge_ratio

    # Optionally, save the updated DataFrame to a new CSV file
    
    existing_pairs.to_csv(existing_pairs_file, index=False)
    
    return existing_pairs
