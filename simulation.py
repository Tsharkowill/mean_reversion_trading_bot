import numpy as np
import pandas as pd
import os
import json





'''Make loop to iterate through data.csv and cointegrated_pairs.csv to create spread data frame as do the simulation'''

'''Also use the first week of data to establish a hedge ratio and then simulate time periods following
the intial one to see how a simulation from the past will work on future data'''

'''How long between refreshing the cointegrated pairs? The 1hr_data is about a month'''

'''Test whether I need to feed data in to the simulation with only the spread (I think I don't need to use the
static z_score)'''

'''Look at correlation between parameters and final portfolio value/sharpe ratio'''

'''Make seperate repo for analysis with jupyter notebooks and link to it in the README'''


# Adjusted Z-Score calculation to be a method within the class
class TradingStrategy:
    def __init__(self, price_data):
        self.price_data = price_data  # DataFrame with timestamp indexed asset prices
        self.leverage = 50
        self.initial_portfolio_value = 2000
        self.results_df = pd.DataFrame()  # DataFrame to store simulation results

    def calculate_spread(self, cointegrated_pairs_file):
        cointegrated_pairs = pd.read_csv(cointegrated_pairs_file)
        spreads_df = pd.DataFrame(index=self.price_data.index)
        spreads_df['time'] = self.price_data['time']
        for _, row in cointegrated_pairs.iterrows():
            base_asset = row['Base']
            quote_asset = row['Quote']
            hedge_ratio = row['HedgeRatio']
            spread_name = f'{base_asset}_{quote_asset}'
            spreads_df[spread_name] = self.price_data[base_asset] - (hedge_ratio * self.price_data[quote_asset])
            

        self.spreads_df = spreads_df
        print(self.spreads_df)

    '''Need to update zscore calculation to accommodate the new way of calculating the spread'''
    
    def calculate_zscore(self, WINDOW):
        spread_series = self.price_data['spread']
        mean = spread_series.rolling(window=WINDOW).mean()
        std = spread_series.rolling(window=WINDOW).std()
        self.price_data['z_score'] = (spread_series - mean) / std

    def simulate_trade(self, WINDOW, POSITION_SIZE, ENTRY_Z, EXIT_Z):
        self.calculate_zscore(WINDOW)  # Update Z-score calculation
        portfolio_values = [self.initial_portfolio_value]
        portfolio_value = self.initial_portfolio_value
        in_position = False
        
        for _, row in self.price_data.iterrows():
            z_score = row['z_score']
            spread = row['spread']
            trade_return = 0

            if not in_position:
                if z_score > ENTRY_Z:  # Short the spread
                    trade_return = -spread * POSITION_SIZE * self.leverage
                    in_position = True  # Mark that a position is now open
                elif z_score < -ENTRY_Z:  # Long the spread
                    trade_return = spread * POSITION_SIZE * self.leverage
                    in_position = True  # Mark that a position is now open
            elif abs(z_score) <= EXIT_Z:
                in_position = False  # Close position if Z-score within bounds for exiting

            portfolio_value += trade_return
            portfolio_values.append(portfolio_value)

        # Calculate Sharpe ratio (assuming risk-free rate = 0 for simplicity)
        returns = pd.Series(portfolio_values).pct_change().dropna()
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) # Risk free rate might be *.95/period length/year
        final_portfolio_value = portfolio_values[-1]

        return sharpe_ratio, final_portfolio_value

    def run_monte_carlo_simulation(self, iterations):
        simulations = []
        for _ in range(iterations):
            WINDOW = np.random.randint(5, 30)
            POSITION_SIZE = 5
            ENTRY_Z = np.random.uniform(0.5, 1.5)
            EXIT_Z = np.random.uniform(0, 0.2)
            sharpe_ratio, final_portfolio_value = self.simulate_trade(WINDOW, POSITION_SIZE, ENTRY_Z, EXIT_Z)
            simulations.append({
                'WINDOW': WINDOW,
                'POSITION_SIZE': POSITION_SIZE,
                'ENTRY_Z': ENTRY_Z,
                'EXIT_Z': EXIT_Z,
                'SHARPE_RATIO': sharpe_ratio,
                'FINAL_PORTFOLIO_VALUE': final_portfolio_value
            })
        self.results_df = pd.DataFrame(simulations)
        self.results_df.to_csv('simulation_results.csv', index=False)
        return self.results_df
    
    def test_trading_strategy(self, cointegrated_pairs_file, price_data_file, optimal_parameters_file):
        pairs_df = pd.read_csv(cointegrated_pairs_file)
        price_data = pd.read_csv(price_data_file)
        optimal_parameters = pd.read_csv(optimal_parameters_file)

        results = []

        for _, pair_row in pairs_df.iterrows():
            base_asset, quote_asset, hedge_ratio = pair_row['Base'], pair_row['Quote'], pair_row['HedgeRatio']
            spread = price_data[base_asset] - price_data[quote_asset] * hedge_ratio
            spread_data = pd.DataFrame({'spread': spread})
            
            for _, params_row in optimal_parameters.iterrows():
                if f"{base_asset}_{quote_asset}" == params_row['Market']:
                    sharpe_ratio, final_portfolio_value = self.simulate_trade(spread_data, WINDOW=params_row['WINDOW'], POSITION_SIZE=1, ENTRY_Z=params_row['ENTRY_Z'], EXIT_Z=params_row['EXIT_Z'])
                    results.append({'Market': params_row['Market'], 'SharpeRatio': sharpe_ratio, 'FinalPortfolioValue': final_portfolio_value})

        results_df = pd.DataFrame(results)
        results_df.to_csv('tested_trades.csv', index=False)
        print("Simulation results saved to 'tested_trades.csv'")


# # # Assume price_data is loaded here, e.g., using pd.read_csv()
# price_data = pd.read_csv('your_spread_data.csv')

# # # Initialize the trading strategy with price data
# strategy = TradingStrategy(price_data)

# # # Run Monte Carlo simulations
# results_df = strategy.run_monte_carlo_simulation(iterations=4000)

# # # Results are saved to 'simulation_results.csv' and returned as a DataFrame
# print(results_df)
    

def calculate_spread_and_run_simulation(cointegrated_pairs_file, price_data_file):
    # Load cointegrated pairs and price data
    pairs_df = pd.read_csv(cointegrated_pairs_file)
    price_data = pd.read_csv(price_data_file)
    
    for _, row in pairs_df.iterrows():
        base_asset = row['Base']
        quote_asset = row['Quote']
        hedge_ratio = row['HedgeRatio']
        
        # Calculate the spread
        spread = price_data[base_asset] - price_data[quote_asset] * hedge_ratio
        
        # Prepare DataFrame for trading strategy
        spread_data = pd.DataFrame({'spread': spread})
        
        # Initialize trading strategy with spread data
        strategy = TradingStrategy(spread_data)
        
        # Run Monte Carlo simulation
        results_df = strategy.run_monte_carlo_simulation(iterations=4000)
        
        # Save results to CSV, naming the file after the cointegrated pair
        filename = f"{base_asset}_{quote_asset}_simulation_train.csv"
        results_df.to_csv(filename, index=False)
        print(f"Results for {base_asset}-{quote_asset} saved to {filename}")

# Replace 'cointegrated_pairs.csv' and 'data.csv' with your actual file paths
# calculate_spread_and_run_simulation('cointegrated_train.csv', 'data_train.csv')
        

'''Filtering for the best parameters to feed in to a simulation to test how well
the first 600 hours of training data will perform for the remaining 200 hours'''

# csv_files = [f for f in os.listdir('.') if f.endswith('_simulation_train.csv')]


# Extract optimal trading parameters from the training data then 
def extract_parameters(csv_file):
    df = pd.read_csv(csv_file).dropna().sort_values(by='FINAL_PORTFOLIO_VALUE', ascending=False).head(30)
    most_frequent_window = df['WINDOW'].mode()[0]
    entry_z_mean = df[df['WINDOW'] == most_frequent_window]['ENTRY_Z'].mean()
    exit_z_mean = df[df['WINDOW'] == most_frequent_window]['EXIT_Z'].mean()
    market_name = csv_file.split('_simulation_train.csv')[0]
    return {'Market': market_name, 'WINDOW': most_frequent_window, 'ENTRY_Z': entry_z_mean, 'EXIT_Z': exit_z_mean}

# # Assuming csv_files is already defined
# optimal_parameters_list = [extract_parameters(csv_file) for csv_file in csv_files]

# # Convert list of dictionaries to a DataFrame and save to CSV
# pd.DataFrame(optimal_parameters_list).to_csv('optimal_parameters.csv', index=False)


# Example of using the TradingStrategy class
strategy = TradingStrategy(pd.read_csv('data_test.csv'))
# strategy.test_trading_strategy('cointegrated_train.csv', 'data_test.csv', 'optimal_parameters.csv')
strategy.calculate_spread('cointegrated_train.csv')

