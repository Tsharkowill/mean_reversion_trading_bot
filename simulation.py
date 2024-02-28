import numpy as np
import pandas as pd



# Use rolling z-score from cointegration.py both in monte carlo as well as eventual trading strategy
# Incorporate more into the TradingStrategy class
# Also maybe try comparing optimizing parameters for all cointegrated pairs vs optimizing for individual pairs
# Maybe it is too tough because when I recheck to get new cointegrated pairs once a week or however often how do I
# keep parameter settings for cointegrated pairs that are no longer part of the dictionary. Maybe update values for
# pairs that are still cointegrated so that you dont have to refresh the parameter dictionary every time. So the dicttionary
# could get quite large after running for a long time but thats ok bec ause it should get too unwieldy


# Adjusted Z-Score calculation to be a method within the class
class TradingStrategy:
    def __init__(self, price_data):
        self.price_data = price_data  # DataFrame with columns ['spread', 'z_score']
        self.leverage = 50
        self.initial_portfolio_value = 2000
        self.results_df = pd.DataFrame()  # DataFrame to store simulation results

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
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)  # Annualized
        final_portfolio_value = portfolio_values[-1]

        return sharpe_ratio, final_portfolio_value

    def run_monte_carlo_simulation(self, iterations):
        simulations = []
        for _ in range(iterations):
            WINDOW = np.random.randint(5, 20)
            POSITION_SIZE = np.random.uniform(10, 20)
            ENTRY_Z = np.random.uniform(0.5, 2)
            EXIT_Z = np.random.uniform(-0.2, 0.2)
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


# Assume price_data is loaded here, e.g., using pd.read_csv()
price_data = pd.read_csv('your_spread_data.csv')

# Initialize the trading strategy with price data
strategy = TradingStrategy(price_data)

# Run Monte Carlo simulations
results_df = strategy.run_monte_carlo_simulation(iterations=2000)

# Results are saved to 'simulation_results.csv' and returned as a DataFrame
print(results_df)

