import pandas as pd
import time
import os
import glob
import sys

from get_time import get_unix_times
from get_markets import fetch_and_compile_candle_data
from cointegration import find_cointegrated_pairs, update_hedge_ratios
from trade_functions import calculate_spread, manage_trades, manage_close_only_trades, close_all_trades
from data_functions import append_filtered_data, filter_and_append_data, merge_json
from simulation import TradingStrategy
from constants import MARKETS, CLOSE_ALL_TRADES

from bitget.bitget_api import BitgetApi
from decouple import config

'''Create instance of Api'''

apiKey = config('apiKey')
secretKey = config('secretKey')
passphrase = config('passphrase')

baseApi = BitgetApi(apiKey, secretKey, passphrase)


while True:

    # # Create dictionary for requesting market data
    # times_dict = get_unix_times()

    # # Get market prices and create a .csv for selected markets
    # fetch_and_compile_candle_data(times_dict, MARKETS)

    # # Splitting time data for training and testing
    # data_15m = pd.read_csv('data_15m.csv')
    # data_train = data_15m.tail(200)
    # data_train.to_csv('data_train.csv', index=False)

    # # Find cointegrated pairs
    # cointegrated_pairs_df = find_cointegrated_pairs('data_train.csv')

    # # Use trading strategy class to find optimal trading parameters
    # train_strategy = TradingStrategy('data_train.csv')
    # train_strategy.calculate_spread('cointegrated_pairs.csv')
    # train_strategy.simulate_all_pairs()
    # train_strategy.extract_parameters('.')



    # for i in range(2):

    #     start_time = time.time()
        
    #     '''Getting new time data'''

    #     # Create dictionary for requesting market data
    #     times_dict = get_unix_times()

    #     # Get market prices and create a .csv for selected markets
    #     fetch_and_compile_candle_data(times_dict, MARKETS)


    #     '''Update the hedge ratio by using the last 100 rows of data and append to the cointegrated_pairs.csv'''

    #     # Update hedge ratio with most recent price data
    #     update_hedge_ratios('data_15m.csv', 'cointegrated_pairs.csv')

    #     '''Update hedge ratios for close only pairs'''

    #     update_hedge_ratios('data_15m.csv', 'cointegrated_close.csv')

    #     '''Calculate spread on new prices and see whether pairs should be entered or exited,
    #     this should include seeing whether the pair exists within the open trades dictionary'''

    #     calculate_spread('data_15m.csv', 'cointegrated_pairs.csv').to_csv('spreads_df.csv', index=False)
        

    #     '''Calculate spreads for close only pairs'''

    #     closing_spreads = calculate_spread('data_15m.csv', 'cointegrated_close.csv')
    #     if closing_spreads is not None:
    #         closing_spreads.to_csv('closing_spreads_df', index=False)
    #     else:
    #         print('No close only poisitons at this time')


    #     '''Execute trades, store data in dictionary/json if entering and remove from that dictionary when exiting'''

    #     manage_trades('spreads_df.csv', 'optimal_parameters.json', 'cointegrated_pairs.csv', 'data_15m.csv')

    #     '''Manage closing only trades here'''

    #     if closing_spreads is not None:
    #         manage_close_only_trades('closing_spreads_df.csv', 'close_only.json')
    #     else:
    #         print('No close only positions at this time')


        
    #     end_time = time.time()
    #     # elapsed_time = end_time - start_time
    #     # sleep_time = max(15*60 - elapsed_time, 0)
    #     # time.sleep(sleep_time)
    #     time.sleep(20)

    
    # '''Dump open_positions.json in to close_only.json, create new spreads_df for positions in close_only, close only cointegrated_pairs'''
    # merge_json('open_positions.json', 'close_only.json')

    # append_filtered_data('spreads_df.csv', 'closing_spreads_df.csv', 'close_only.json')

    # filter_and_append_data('cointegrated_pairs.csv', 'cointegrated_close.csv', 'close_only.json')

    # pattern = '*simulation_train.csv'

    # files_to_delete = glob.glob(pattern)

    # for file in files_to_delete:
    #     try:
    #         os.remove(file)
    #         print(f"Deleted {file}")
    #     except Exception as e:
    #         print(f"Error deleting {file}: {e}")

    if CLOSE_ALL_TRADES is True:
        close_all_trades('open_positions.json')
        close_all_trades('close_only.json')
        sys.exit("Closed all trades and exited the script")
    





    '''Force close trades which uses a variable from constants to force close all positions in both close only and open trades'''

    '''Look at trades and how long they take to close and how profitable they are, scatter plot to show length of
    time the trade was open for vs profitability, perhaps segment these trades based on how many days they were open for.
    Correlation between half life and time the trades are open to see whether it is a good measure. This can be done just
    from gathering trade history. Also maybe make a distribution of the legnth of time trades take to execute as well as 
    a distribution of profitability. Maybe do a copula of length of time and profitability and see how that differs from
    the scatter plot as far as visualization'''