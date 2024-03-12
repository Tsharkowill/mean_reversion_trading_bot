import numpy as np
import pandas as pd
import os
import json


'''The way the cointegration function is determining the hedge ratio isn't working for all pairs'''

'''Need to fix calculate spread so that its seperate for train and test data (or do I?)'''

'''Make seperate repo for analysis with jupyter notebooks and link to it in the README'''


# Adjusted Z-Score calculation to be a method within the class
class TradingStrategy:
    def __init__(self, price_data):
        self.price_data = pd.read_csv(price_data)  # DataFrame with timestamp indexed asset prices
        self.leverage = 50
        self.initial_portfolio_value = 2000

            
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
        self.spreads_df.to_csv('spreads_df.csv')
        print("Spread calculation completed successfully.")
        print(self.spreads_df.head())

    
    def calculate_zscore(self, market, WINDOW):
            spread_series = self.spreads_df[market]
            mean = spread_series.rolling(window=WINDOW).mean()
            std = spread_series.rolling(window=WINDOW).std()
            self.spreads_df[f'z_score_{market}'] = (spread_series - mean) / std

    def simulate_trade(self, market, WINDOW, POSITION_SIZE, ENTRY_Z, EXIT_Z):
        # calculate z-scores for the given market and WINDOW
        self.calculate_zscore(market, WINDOW)

        # Initialize portfolio values tracking
        portfolio_values = [self.initial_portfolio_value]
        portfolio_value = self.initial_portfolio_value
        in_position = False
        position_type = None  # Track whether the position is long or short
        entry_spread = None  # Track spread at the entry point
        
        z_score_column = f'z_score_{market}'
        
        for _, row in self.spreads_df.iterrows():
            current_z_score = row[z_score_column]
            current_spread = row[market]
            trade_return = 0

            if not in_position:
                if current_z_score > ENTRY_Z:  # Enter short position
                    trade_return = -current_spread * POSITION_SIZE * self.leverage
                    in_position, position_type, entry_spread = True, "short", current_spread
                elif current_z_score < -ENTRY_Z:  # Enter long position
                    trade_return = current_spread * POSITION_SIZE * self.leverage
                    in_position, position_type, entry_spread = True, "long", current_spread
            elif abs(current_z_score) <= EXIT_Z:
                # Exit position based on profitability
                if (position_type == "long" and current_spread > (entry_spread * 1.05)) or \
                (position_type == "short" and (current_spread * 1.05) < entry_spread):
                    in_position, position_type, entry_spread = False, None, None  # Exit position
        

            portfolio_value += trade_return
            portfolio_values.append(portfolio_value)

        # Calculate Sharpe ratio (assuming risk-free rate = 0 for simplicity)
        returns = pd.Series(portfolio_values).pct_change().dropna()  
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) 
        final_portfolio_value = portfolio_values[-1]

        return sharpe_ratio, final_portfolio_value

    def run_monte_carlo_simulation(self, market, iterations):
        simulations = []
        for _ in range(iterations):
            WINDOW = np.random.randint(5, 50)
            POSITION_SIZE = 5
            ENTRY_Z = np.random.uniform(0.3, 1.5)
            EXIT_Z = np.random.uniform(0, 0.2)
            sharpe_ratio, final_portfolio_value = self.simulate_trade (market, WINDOW, POSITION_SIZE, ENTRY_Z, EXIT_Z)
            simulations.append({
                'WINDOW': WINDOW,
                'POSITION_SIZE': POSITION_SIZE,
                'ENTRY_Z': ENTRY_Z,
                'EXIT_Z': EXIT_Z,
                'SHARPE_RATIO': sharpe_ratio,
                'FINAL_PORTFOLIO_VALUE': final_portfolio_value
            })
        results_df = pd.DataFrame(simulations)
        return results_df
    
    def simulate_all_pairs(self):
    # Assuming each column in spreads_df represents a cointegrated pair (market)
        for market in self.spreads_df.columns:
            # Skip 'time' or any non-market column if present
            if market == 'time':
                continue

            # Run Monte Carlo simulation for this market
            # Make sure to adjust the method to handle simulations for a single market correctly
            results_df = self.run_monte_carlo_simulation(market=market, iterations=4000)
            
            # Save results to CSV, naming the file after the cointegrated pair
            filename = f"{market}_simulation_train.csv"
            results_df.to_csv(filename, index=False)
            print(f"Results for {market} saved to {filename}")


    
    def extract_parameters(self, simulation_train_files_path):
        optimal_parameters = {}
        csv_files = [f for f in os.listdir(simulation_train_files_path) if f.endswith('_simulation_train.csv')]
        for csv_file in csv_files:
            df = pd.read_csv(os.path.join(simulation_train_files_path, csv_file)).dropna().sort_values(by='FINAL_PORTFOLIO_VALUE', ascending=False).head(30)
             # Filter the DataFrame based on your criteria
            df = df[(df['FINAL_PORTFOLIO_VALUE'] > 2000) & (df['FINAL_PORTFOLIO_VALUE'] < 5000) & (df['SHARPE_RATIO'] > 1)]
            print(f'Filtered {len(df)} entries from {csv_file}')
            # If filtered_df is empty, continue to the next csv_file
            if df.empty:
                print(f'No entries met the criteria in {csv_file}, skipping...')
                continue

            most_frequent_window = int(df['WINDOW'].mode()[0])
            entry_z_mean = float(df[df['WINDOW'] == most_frequent_window]['ENTRY_Z'].mean())
            exit_z_mean = float(df[df['WINDOW'] == most_frequent_window]['EXIT_Z'].mean())
            market_name = csv_file.split('_simulation_train.csv')[0]
            optimal_parameters[market_name] = {
                'WINDOW': most_frequent_window,
                'ENTRY_Z': entry_z_mean,
                'EXIT_Z': exit_z_mean
            }
        with open('optimal_parameters.json', 'w') as json_file:
            json.dump(optimal_parameters, json_file, indent=4)


    def test_strategy(self, cointegrated_pairs_file, optimal_parameters_file):
        with open(optimal_parameters_file, 'r') as file:
            optimal_parameters= json.load(file)
        test_results = {}

        for market, params in optimal_parameters.items():
            WINDOW = params['WINDOW']
            ENTRY_Z = params['ENTRY_Z']
            EXIT_Z = params['EXIT_Z']
            POSITION_SIZE = 5

            self.calculate_spread(cointegrated_pairs_file)
            sharpe_ratio, final_portfolio_value = self.simulate_trade(
                market, WINDOW, POSITION_SIZE, ENTRY_Z, EXIT_Z
            )

            test_results[market] = {
                'SharpeRatio': sharpe_ratio,
                'FinalPortfolioValue': final_portfolio_value
            }

        with open('test_strategy.json', 'w') as json_file:
            json.dump(test_results, json_file, indent=4)
    
    

'''Testing monte carlo simulation after modifications'''

if __name__ == '__main__':

    train_strategy = TradingStrategy('data_train.csv')
    train_strategy.calculate_spread('cointegrated_train.csv')
    train_strategy.simulate_all_pairs()
    train_strategy.extract_parameters('.')

    test_strategy = TradingStrategy('data_test.csv')
    test_strategy.calculate_spread('cointegrated_train.csv')
    test_strategy.test_strategy('cointegrated_train.csv', 'optimal_parameters.json')




        

