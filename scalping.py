import numpy as np
import pandas as pd
import os
import json

from trade_functions import calculate_zscore


class ScalpingStrategy:
    def __init__(self, price_data):
        self.price_data = price_data  # DataFrame with timestamp indexed asset prices
        self.leverage = 100
        self.initial_portfolio_value = 2000
    
    def calculate_zscore(self, market):
            spread_series = self.price_data[market]
            mean = spread_series.rolling(window=200).mean()
            std = spread_series.rolling(window=200).std()
            self.price_data[f'z_score_{market}'] = (spread_series - mean) / std

    def simulate_trade(self, market, WINDOW, POSITION_SIZE, Z_SCORE):
        # # Calculate Z-scores for the given market and WINDOW
        # self.calculate_zscore(market, WINDOW)

        # Initialize portfolio values tracking
        portfolio_value = self.initial_portfolio_value
        in_position = False
        position_type = None  # Track whether the position is long or short
        
        z_score_column = f'z_score_{market}'
        price_column = market
        
        for _, row in self.price_data.iterrows():
            current_z_score = row[z_score_column]
            current_price = row[price_column]
            trade_return = 0.0

            # Flipping positions based on Z_SCORE threshold
            if in_position:
            # Calculate return based on price change since entry
                price_increase = (current_price - entry_price) * ((POSITION_SIZE * self.leverage) / entry_price)
                if position_type == "long" and current_z_score >= Z_SCORE:
                    trade_return = price_increase - (POSITION_SIZE * self.leverage) * 0.02
                    in_position, position_type, entry_price = False, None, None
                # elif position_type == "short" and current_z_score <= -Z_SCORE:
                #     in_position, position_type, entry_price = False, None, None
                #     trade_return = -price_increase - (POSITION_SIZE * self.leverage) * 0.02
                        
            elif not in_position:
                if current_z_score <= -Z_SCORE:  # Enter long position
                    in_position, position_type, entry_price = True, "long", current_price
                # elif current_z_score >= Z_SCORE:  # Enter short position
                #    in_position, position_type, entry_price = True, "short", current_price
                


            portfolio_value += trade_return


        # Exiting the last open position at the end of the data
        if in_position:
            # Simulate exiting the position with no additional profit or loss
            # You may adjust this part based on your strategy for exiting the final open position
            in_position, position_type = False, None

        # Returning the portfolio values for further analysis
        return portfolio_value


        

    def run_monte_carlo_simulation(self, iterations):
        best_parameters = {}
        highest_returns = -np.inf

        for _ in range(iterations):
            WINDOW = 200
            POSITION_SIZE = 1
            Z_SCORE = np.random.uniform(3.0, 5.0)
            total_returns = self.trade_all_markets(WINDOW, POSITION_SIZE, Z_SCORE)
            # Check if this simulation yielded higher returns than previous best
            if total_returns > highest_returns:
                highest_returns = total_returns
                best_parameters = {
                    'returns': highest_returns,
                    'window': WINDOW,
                    'position_size': POSITION_SIZE,
                    'z_score': Z_SCORE
                }

        # Save the best parameters to a JSON file
        with open('best_parameters_15_200.json', 'w') as f:
            json.dump(best_parameters, f, indent=4)

        return best_parameters
    
    def simulate_all_markets(self):
    # Assuming each column in spreads_df represents a cointegrated pair (market)
        for market in self.price_data:
            # Skip 'time' or any non-market column if present
            if market == 'time':
                continue
            
            # Run Monte Carlo simulation for this market
            # Make sure to adjust the method to handle simulations for a single market correctly
            results_df = self.run_monte_carlo_simulation(market=market, iterations=1000)
            # results_df = results_df[(results_df['FINAL_PORTFOLIO_VALUE'] > 2000)]
            results_df = results_df.sort_values(by='FINAL_PORTFOLIO_VALUE', ascending=False)
            
            # Save results to CSV, naming the file after the cointegrated pair
            filename = f"{market}_scalping_1h.csv"
            results_df.to_csv(filename, index=False)
            print(f"Results for {market} saved to {filename}")

    def trade_all_markets(self, WINDOW, POSITION_SIZE, Z_SCORE):
        
        total_returns = 0.0
        for market in self.price_data:
            if market == 'time' or market.startswith('z_score_'):
                continue

            portfolio_value = self.simulate_trade(market, WINDOW, POSITION_SIZE, Z_SCORE)
            returns = portfolio_value - self.initial_portfolio_value
            total_returns += returns
           

        return total_returns
        


def manage_scalp(price_data_file, MARKETS):
    
    price_data = pd.read_csv(price_data_file)
    Z_SCORE = 3.5
    WINDOW = 40

    try:
        with open('open_scalps.json', 'r') as json_file:
            open_scalps = json.load(json_file)
        print(f'Open positions loaded: {open_scalps}')
    except FileNotFoundError:
        open_scalps = {}
        print('No open positions found, starting fresh')

    keys_to_remove = []

    for market in MARKETS:
       
        calculate_zscore(market, price_data, WINDOW)
        z_score_column = f'z_score_{market}'
        latest_row = price_data[market].iloc[-1]
        current_z_score = latest_row[z_score_column]
        key_to_remove = None

        if market not in open_scalps:
            if current_z_score <= -Z_SCORE:
                enter_scalp_trade(market, "long", price_data)
            elif current_z_score >= Z_SCORE:
                enter_scalp_trade(market, "short", price_data)

        elif market in open_scalps:
            position_type = open_scalps[market]['position_type']
            if position_type == "long" and current_z_score >= Z_SCORE:
                print(f"Exiting long position for market: {market}")
                key_to_remove = exit_scalp_trade(market, position_type, open_scalps)

            elif position_type == "short" and current_z_score >= -Z_SCORE:
                print(f"Exiting short position for market: {market}")
                key_to_remove = exit_scalp_trade(market, position_type, open_scalps)
        
            if key_to_remove is not None:
                keys_to_remove.append(key_to_remove) 

    for key in keys_to_remove:
        if key in open_scalps:
            del open_scalps[key]


    with open('open_scalps.json', 'w') as json_file:
        json.dump(open_scalps, json_file, indent=4)


def enter_scalp_trade(market, position_type, price_data):



def exit_scalp_trade(market, position_type, price_data):




data = pd.read_csv('data_15_scalp.csv')
# data = data.tail(2000)



scalping = ScalpingStrategy(data)
for market in scalping.price_data:
    # Skip 'time' or any non-market column if present
    if market == 'time':
        continue
    scalping.calculate_zscore(market)
scalping.run_monte_carlo_simulation(1000)
