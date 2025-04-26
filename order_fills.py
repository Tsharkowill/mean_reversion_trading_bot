import bitget.v2.mix.order_api as mixOrderApi
from constants import MARKETS
from decouple import config

import pandas as pd
import boto3
import time
from datetime import datetime



def get_unix_times():
    """Get the Unix time for the last 24 hours."""
    current_unix_time = int(time.time() * 1000)  # Current time in milliseconds
    unix_time_minus_24h = current_unix_time - (24 * 60 * 60 * 1000)  # 24 hours back
    return current_unix_time, unix_time_minus_24h


def fetch_order_fills(order_api, markets, start_time, end_time):
    """Fetch historical trades for each market."""
    fills_df = pd.DataFrame()
    for market in markets:
        params = {
            "symbol": market,
            "productType": "USDT-FUTURES",
            "startTime": start_time,
            "endTime": end_time
        }
        try:
            response = order_api.fills(params)
            if 'data' in response and 'fillList' in response['data']:
                # Convert the fillList to a DataFrame and append to fills_df
                market_fills = response['data']['fillList']
                if isinstance(market_fills, list):
                    temp_df = pd.DataFrame(market_fills)
                    fills_df = pd.concat([fills_df, temp_df], ignore_index=True)
                else:
                    print(f"Unexpected format for fillList in market: {market}")
            else:
                print(f"No data returned for market: {market}")
        except Exception as e:
            print(f"Error fetching orders for market {market}: {str(e)}")
        
        time.sleep(0.2)
    
    return fills_df


def upload_to_s3(local_file, bucket_name, s3_key):
    """Upload a file to S3."""
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(local_file, bucket_name, s3_key)
        print(f"File uploaded to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")



def main():
    # Get Unix times
    current_unix_time, unix_time_minus_24h = get_unix_times()

    # credentials
    apiKey = config('apiKey')
    secretKey = config('secretKey')
    passphrase = config('passphrase')
    bucket_name = config('s3_bucket_name')

    # Initialize the API
    order_api = mixOrderApi.OrderApi(apiKey, secretKey, passphrase)

    # Fetch historical trades
    fills_df = fetch_order_fills(order_api, MARKETS, unix_time_minus_24h, current_unix_time)
    print(fills_df.dtypes)

    if not fills_df.empty:
        # Save Parquet file locally
        parquet_file = f"/tmp/fills_{datetime.now().strftime('%Y%m%d')}.parquet"
        fills_df.to_parquet(parquet_file, index=False)

        # Upload to S3
        s3_key = f"fills/daily/fills_{datetime.now().strftime('%Y%m%d')}.parquet"
        upload_to_s3(parquet_file, bucket_name, s3_key)
    else:
        print("No fills to upload.")


if __name__ == "__main__":
    main()
