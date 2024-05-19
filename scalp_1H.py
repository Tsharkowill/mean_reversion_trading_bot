import pandas as pd
import time

from get_time import get_unix_times
from get_markets import fetch_and_compile_candle_data
from constants import SCALP_MARKETS, SCALP_SIZE
from scalping import manage_scalp, enter_scalp_trade
from trade_functions import calculate_zscore

from bitget.bitget_api import BitgetApi
from decouple import config

'''Create instance of Api'''


apiKey = config('apiKey')
secretKey = config('secretKey')
passphrase = config('passphrase')


baseApi = BitgetApi(apiKey, secretKey, passphrase)


while True:

    start_time = time.time()

    # Create dictionary for requesting market data
    times_dict = get_unix_times(2)

    # Get market prices and create a .csv for selected markets
    try:
        fetch_and_compile_candle_data(times_dict, SCALP_MARKETS, '1H')
    except Exception as e:
        print(f"Error fetching market data: {e}")

    try:
        manage_scalp('data_1H.csv', SCALP_MARKETS, '1H', 2.8, 200)
    except Exception as e:
        print(f"Error managing scalps: {e}")

    
    end_time = time.time()
    elapsed_time = end_time - start_time
    sleep_time = max(60*60 - elapsed_time, 0)
    time.sleep(sleep_time)
