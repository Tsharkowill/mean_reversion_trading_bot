from get_time import get_unix_times
from get_markets import fetch_and_compile_candle_data
from mean_reversion import manage_trade
from constants import MARKETS, Z_SCORE_HIGH, Z_SCORE_MEDIUM, HIGH_WINDOW, MEDIUM_WINDOW


from bitget.bitget_api import BitgetApi
from decouple import config

'''Create instance of Api'''


apiKey = config('apiKey')
secretKey = config('secretKey')
passphrase = config('passphrase')


baseApi = BitgetApi(apiKey, secretKey, passphrase)




# Create dictionary for requesting market data
times_dict = get_unix_times(3)

# Get market prices and create a .csv for selected markets
try:
    fetch_and_compile_candle_data(times_dict, MARKETS, '15m')
except Exception as e:
    print(f"Error fetching market data: {e}")

try:
    manage_trade('data_15m.csv', MARKETS, 'high', Z_SCORE_HIGH, HIGH_WINDOW)
except Exception as e:
    print(f"Error managing scalps: {e}")

try:
    manage_trade('data_15m.csv', MARKETS, 'medium', Z_SCORE_MEDIUM, MEDIUM_WINDOW)
except Exception as e:
    print(f"Error managing scalps: {e}")


