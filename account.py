import bitget.v1.mix.order_api as maxOrderApi
from bitget.bitget_api import BitgetApi
from bitget.exceptions import BitgetAPIException
from decouple import config
from constants import SCALP_MARKETS

import time
import pandas as pd
import cx_Oracle
import os


def get_unix_times():
    # Get the current Unix time
    current_unix_time = int(time.time())
    
    # Calculate the Unix time 7 days back (7 days * 24 hours * 60 minutes * 60 seconds)
    unix_time_minus_7 = current_unix_time - (7 * 24 * 60 * 60)

    # Multiply by 1000 to account for milliseconds
    current_unix_time = current_unix_time * 1000
    unix_time_minus_7 = unix_time_minus_7 * 1000

    
    return current_unix_time, unix_time_minus_7

# Get the current and 7 days back Unix times
current_unix_time, unix_time_minus_7 = get_unix_times()



apiKey = config('apiKey')
secretKey = config('secretKey')
passphrase = config('passphrase')

# Create an instance of the BitgetApi class
baseApi = BitgetApi(apiKey, secretKey, passphrase)

order_api = maxOrderApi.OrderApi(apiKey, secretKey, passphrase)

orders_df = pd.DataFrame()

for market in SCALP_MARKETS:
    params = {
    "symbol": f"{market}_UMCBL",
    "productType": "USDT-FUTURES",
    "startTime": unix_time_minus_7,
    "endTime": current_unix_time,
    "pageSize": 20
    }
    try:
        response = order_api.ordersHistory(params)

        # Extract the order list
        orders = response['data']['orderList']

        # Create a DataFrame
        current_orders = pd.DataFrame(orders)

        # Append current orders to orders_df
        orders_df = pd.concat([orders_df, current_orders], ignore_index=True)

    except BitgetAPIException as e:
            print("error:" + e.message)


orders_df.drop(orders_df.columns[18], axis=1, inplace=True)

# Set the location of the client credentials wallet
os.environ["TNS_ADMIN"] = "/opt/oracle/wallet"

# Create a connection to Oracle database using the TNS name from your tnsnames.ora
# Replace 'dbname_high' with the actual TNS name from your tnsnames.ora
connection = cx_Oracle.connect(
    user=config('oracle_user_name'),
    password=config('oracle_password'),
    dsn="meanrevbot_high"  # This is the TNS name for your Oracle database connection
)

# Create a cursor object
cursor = connection.cursor()

# Convert Pandas DataFrame to Oracle-compatible format
data_to_insert = orders_df.to_records(index=False).tolist()

# Dynamically create placeholders based on the DataFrame's number of columns
placeholders = ', '.join([f":{i+1}" for i in range(len(orders_df.columns))])

# SQL Insert Statement
sql_insert_query = f"INSERT INTO trades VALUES ({placeholders})"

# Insert data into Oracle database
cursor.executemany(sql_insert_query, data_to_insert)

# Commit changes and close connection
connection.commit()
connection.close()

'''Create heatmap maybe using Spearman rank correlation or Kendalls Tau instead of Pearson correlation
coefficient as pearson assumes linearity and normal distribution (although maybe there is a normal distribution)'''







