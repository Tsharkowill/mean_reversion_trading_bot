import pandas as pd
import numpy as np
import time

from get_time import get_unix_times
from get_markets import fetch_and_compile_candle_data
from cointegration import find_cointegrated_pairs, update_hedge_ratios
from trade_functions import filter_and_save_tradable_pairs, calculate_spread, manage_trades
from simulation import TradingStrategy
from constants import MARKETS

from bitget.bitget_api import BitgetApi
from bitget.exceptions import BitgetAPIException
from decouple import config

'''Create instance of Api'''

apiKey = config('apiKey')
secretKey = config('secretKey')
passphrase = config('passphrase')

baseApi = BitgetApi(apiKey, secretKey, passphrase)


'''Get new candle data for markets and append results on to existing dataframe, read from csv'''

# Create dictionary for requesting market data
times_dict = get_unix_times()

# Get market prices and create a .csv for selected markets
fetch_and_compile_candle_data(times_dict, MARKETS)

# Splitting time data for training and testing
data_15m = pd.read_csv('data_15m.csv')
data_interim = data_15m.tail(300)
data_train = data_interim.head(200)
data_test = data_interim.tail(100)
data_train.to_csv('data_train.csv', index=False)
data_test.to_csv('data_test.csv', index=False)

# Find cointegrated pairs
cointegrated_pairs_df = find_cointegrated_pairs('data_train.csv')

# Use trading strategy class to find optimal trading parameters
train_strategy = TradingStrategy('data_train.csv')
train_strategy.calculate_spread('cointegrated_train.csv')
train_strategy.simulate_all_pairs()
train_strategy.extract_parameters('.')

# Update hedge ratio in cointegrated pairs file
update_hedge_ratios('data_test.csv', 'cointegrated_train.csv')

# Test strategy with optimal extracted parameters
test_strategy = TradingStrategy('data_test.csv')
test_strategy.test_strategy('cointegrated_train.csv', 'optimal_parameters.json')



'''This part should be put on a loop or while true'''
while True:

    '''Getting new time data'''

    # Create dictionary for requesting market data
    times_dict = get_unix_times()

    # Get market prices and create a .csv for selected markets
    fetch_and_compile_candle_data(times_dict, MARKETS)


    '''Update the hedge ratio by using the last 100 rows of data and append to the cointegrated_pairs.csv'''

    # Update hedge ratio with most recent price data
    update_hedge_ratios('data_15m.csv', 'cointegrated_train.csv')

    '''Create new dictionary and json containing tradeable pairs'''

    filter_and_save_tradable_pairs('optimal_parameters.json', 'test_strategy.json', 'tradable_pairs.json')

    '''Calculate spread on new prices and see whether pairs should be entered or exited,
    this should include seeing whether the pair exists within the open trades dictionary'''

    calculate_spread('data_15m.csv', 'updated_cointegrated_pairs.csv')


    '''Execute trades, store data in dictionary/json if entering and remove from that dictionary when exiting'''

    manage_trades('spreads_df.csv', 'tradable_pairs.json', 'updated_cointegrated_pairs.csv', 'data_15m.csv')


    '''Decide whether after 1 day (or whatever period) I should just close all open trades
    and start fresh or make a new dicitonary for close only positions'''
    time.sleep(900)