import bitget.v2.mix.account_api as mixAccountApi
from decouple import config
import json
import pandas as pd

apiKey = config('apiKey')
secretKey = config('secretKey')
passphrase = config('passphrase')


params = {
            "productType": "USDT-FUTURES",
            "marginCoin": "USDT"
        }



account_api = mixAccountApi.AccountApi(apiKey, secretKey, passphrase)

response_base = account_api.allPosition(params)


# Process positions and calculate position sizes
positions = []
for pos in response_base['data']:
    try:
        symbol = pos['symbol']
        hold_side = pos['holdSide']
        units = float(pos['total'])
        price = float(pos['markPrice'])
        
        # Calculate position size (margin * price)
        position_size = units * price
        
        positions.append({
            'symbol': symbol,
            'hold_side': hold_side,
            'units': units,
            'price': price,
            'position_size': position_size
        })
    except KeyError as e:
        print(f"Missing key in position data: {e}")
        continue

# Create DataFrame
df = pd.DataFrame(positions)

# Calculate aggregated values
total_portfolio_size = df['position_size'].sum()
total_long = df[df['hold_side'] == 'long']['position_size'].sum()
total_short = df[df['hold_side'] == 'short']['position_size'].sum()
net_exposure = total_long - total_short

print("Position Sizes:")
print(df[['symbol', 'hold_side', 'position_size']])
print("\nAggregated Values:")
print(f"Total Long Exposure: {total_long:.2f} USDT")
print(f"Total Short Exposure: {total_short:.2f} USDT")
print(f"Net Exposure: {net_exposure:.2f} USDT")

# Save to Parquet
df.to_parquet('position_sizes.parquet')

# To upload to S3 (requires boto3 and AWS credentials configured)
# import boto3
# s3 = boto3.client('s3')
# s3.upload_file('position_sizes.parquet', 'your-bucket-name', 'path/position_sizes.parquet')