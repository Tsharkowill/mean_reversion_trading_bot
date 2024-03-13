import json
import pandas as pd
import numpy as np




def filter_and_save_tradable_pairs(optimal_parameters_file, test_results_file, output_file):
  # Load the JSON data from files
  with open(optimal_parameters_file, 'r') as f:
      optimal_parameters = json.load(f)
  
  with open(test_results_file, 'r') as f:
      test_results = json.load(f)
  
  # Initialize a dictionary to hold tradable pairs with optimal parameters
  tradable_pairs = {}

  # Iterate through the test results and filter based on Sharpe ratio
  for market, results in test_results.items():
      if results['SharpeRatio'] >= 1:
          # Check if market exists in optimal parameters
          if market in optimal_parameters:
              # Add the market and its parameters to tradable pairs
              tradable_pairs[market] = optimal_parameters[market]

  # Save the tradable pairs with their parameters to a new JSON file
  with open(output_file, 'w') as f:
      json.dump(tradable_pairs, f, indent=4)
  
  print(f"Tradable pairs saved to {output_file}")



def calculate_spread(price_data_file, cointegrated_pairs_file):
        
  price_data = pd.read_csv(price_data_file)
  cointegrated_pairs = pd.read_csv(cointegrated_pairs_file)
  spreads_df = pd.DataFrame(index=price_data.index)
  spreads_df['time'] = price_data['time']
  for _, row in cointegrated_pairs.iterrows():
      base_asset = row['Base']
      quote_asset = row['Quote']
      hedge_ratio = row['HedgeRatio']
      spread_name = f'{base_asset}_{quote_asset}'
      spreads_df[spread_name] = price_data[base_asset] - (hedge_ratio * price_data[quote_asset])
          

  spreads_df.to_csv('spreads_df.csv')
  print("Spread calculation completed successfully.")
  print(spreads_df.head())


def calculate_zscore(market, spreads_df, WINDOW):
  spread_series = spreads_df[market]
  mean = spread_series.rolling(window=WINDOW).mean()
  std = spread_series.rolling(window=WINDOW).std()
  spreads_df[f'z_score_{market}'] = (spread_series - mean) / std



'''Use example.py to be able to open trades'''
def enter_trade_pair(base_asset, quote_asset, position_type):
  print(f"Entering trade: {position_type} {base_asset}, {position_type} {quote_asset}")
  # Placeholder for logic to execute trade entry for both assets


'''Also use example.py for this one, maybe just change params['side'] to close_long, close_short'''
def exit_trade_pair(base_asset, quote_asset):
  print(f"Exiting trade: {base_asset}, {quote_asset}")
  # Placeholder for logic to execute trade exit for both assets


'''Also needs spreads_df fed in to it for functionality'''
def manage_trades(self, spreads_file, tradable_pairs_file,):
  spreads_df = pd.read_csv(spreads_file)
  
  with open(tradable_pairs_file, 'r') as file:
      tradable_pairs = json.load(file)

  open_positions = {}  # Dictionary to track open positions

  for market, params in tradable_pairs.items():
    base_asset, quote_asset = market.split('_')
    WINDOW = params['WINDOW']
    POSITION_SIZE = params['POSITION_SIZE']  # Assuming this is defined in tradable_pairs.json
    ENTRY_Z = params['ENTRY_Z']
    EXIT_Z = params['EXIT_Z']

    calculate_zscore(market, spreads_df, WINDOW)

    z_score_column = f'z_score_{market}'

    for _, row in spreads_df.iterrows():
        current_z_score = row[z_score_column]
        current_spread = row[market]  # Assuming this is how you've stored the spread data for each market
    
        # Determine if any trade logic needs to be processed
        if market not in open_positions:
            if current_z_score > ENTRY_Z:  # Enter positions with base asset shorted and quote asset longed
                enter_trade_pair(base_asset, quote_asset, "short/long")
                open_positions[market] = {"position_type": "short/long", "entry_spread": current_spread}
            elif current_z_score < -ENTRY_Z:  # Enter positions with base asset longed and quote asset shorted
                enter_trade_pair(base_asset, quote_asset, "long/short")
                open_positions[market] = {"position_type": "long/short", "entry_spread": current_spread}
        elif abs(current_z_score) <= EXIT_Z and market in open_positions:
          position_info = open_positions[market]
          position_type = position_info["position_type"]
          entry_spread = position_info["entry_spread"]
          current_spread = row[market]  # Assuming this is how you've stored the current spread for each market
          
          profitable_to_exit = False
          # Check if it's profitable to exit "short/long" positions
          if position_type == "short/long" and current_spread < entry_spread:
              profitable_to_exit = True
          # Check if it's profitable to exit "long/short" positions
          elif position_type == "long/short" and current_spread > entry_spread:
              profitable_to_exit = True

          if profitable_to_exit:
              exit_trade_pair(base_asset, quote_asset)
              del open_positions[market]


        # Additional logic for updating portfolio values or tracking trades can be added here

    # Consider persisting open_positions to a file if needed for longer-term tracking beyond script execution
  with open('open_positions.json', 'w') as json_file:
          json.dump(open_positions, json_file, indent=4)

# Example of calling manage_trades
# Assuming you have a TradingStrategy instance named strategy
# manage_trades('tradable_pairs.json')

