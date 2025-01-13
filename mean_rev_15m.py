import pandas as pd

from get_time import get_unix_times
from get_markets import fetch_and_compile_candle_data
from mean_reversion import manage_scalp
from constants import SCALP_MARKETS, Z_SCORE_LONG, Z_SCORE_SHORT, WINDOW


from bitget.bitget_api import BitgetApi
from decouple import config

'''Create instance of Api'''


apiKey = config('apiKey')
secretKey = config('secretKey')
passphrase = config('passphrase')


baseApi = BitgetApi(apiKey, secretKey, passphrase)




# Create dictionary for requesting market data
times_dict = get_unix_times(2)

# Get market prices and create a .csv for selected markets
try:
    fetch_and_compile_candle_data(times_dict, SCALP_MARKETS, '15m')
except Exception as e:
    print(f"Error fetching market data: {e}")

try:
    manage_scalp('data_15m.csv', SCALP_MARKETS, '15m', Z_SCORE_LONG, Z_SCORE_SHORT, WINDOW)
except Exception as e:
    print(f"Error managing scalps: {e}")


