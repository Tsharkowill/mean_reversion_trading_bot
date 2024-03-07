import pandas as pd
import numpy as np
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
                if half_life <= 40 and half_life > 0:
                    cointegrated_pairs.append({
                    'Base': symbols[i],
                    'Quote': symbols[j],
                    'HedgeRatio': hedge_ratio,
                    'HalfLife': half_life
                })
    
    # Convert the list of cointegrated pairs into a DataFrame
    df_cointegrated_pairs = pd.DataFrame(cointegrated_pairs)
    df_cointegrated_pairs.to_csv('cointegrated_train.csv', index=False)

    return df_cointegrated_pairs

# Example usage
cointegrated_pairs_df = find_cointegrated_pairs('data_test_2.csv')
print(cointegrated_pairs_df)

