import bitget.v1.mix.order_api as maxOrderApi
from bitget.bitget_api import BitgetApi
from bitget.exceptions import BitgetAPIException
from decouple import config
from constants import SCALP_MARKETS

import time
import pandas as pd
import boto3
from datetime import datetime


def get_unix_times():
    """Get the Unix time for the last 24 hours."""
    current_unix_time = int(time.time() * 1000)  # Current time in milliseconds
    unix_time_minus_24h = current_unix_time - (24 * 60 * 60 * 1000)  # 24 hours back
    return current_unix_time, unix_time_minus_24h


# Get the current and 24 hours back Unix times
current_unix_time, unix_time_minus_24h = get_unix_times()

# API credentials
apiKey = config('apiKey')
secretKey = config('secretKey')
passphrase = config('passphrase')

# Initialize the API
order_api = maxOrderApi.OrderApi(apiKey, secretKey, passphrase)

orders_df = pd.DataFrame()

# Fetch orders for each market
for market in SCALP_MARKETS:
    params = {
        "symbol": f"{market}_UMCBL",
        "productType": "USDT-FUTURES",
        "startTime": unix_time_minus_24h,
        "endTime": current_unix_time,
        "pageSize": 20
    }
    try:
        response = order_api.ordersHistory(params)

        # Extract and append orders
        if 'data' in response and 'orderList' in response['data']:
            orders = response['data']['orderList']
            current_orders = pd.DataFrame(orders)
            orders_df = pd.concat([orders_df, current_orders], ignore_index=True)
        else:
            print(f"No data returned for market: {market}")

    except BitgetAPIException as e:
        print(f"Error fetching orders for market {market}: {e.message}")

# Save to Parquet and upload to S3
if not orders_df.empty:
    # Save Parquet file locally
    parquet_file = f"/tmp/trades_{datetime.now().strftime('%Y%m%d')}.parquet"
    orders_df.to_parquet(parquet_file, index=False)

    # Upload Parquet file to S3
    s3_client = boto3.client("s3")
    bucket_name = "your-s3-bucket"
    s3_key = f"trades/daily/trades_{datetime.now().strftime('%Y%m%d')}.parquet"

    try:
        s3_client.upload_file(parquet_file, bucket_name, s3_key)
        print(f"File uploaded to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")
else:
    print("No data to upload.")







