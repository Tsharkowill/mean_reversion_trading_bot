from data_functions import merge_json, append_filtered_data, filter_and_append_data
import os
import pandas as pd


# merge_json('open_positions.json', 'close_only.json')

# append_filtered_data('spreads_df.csv', 'closing_spreads_df.csv', 'open_positions.json')

# filter_and_append_data('cointegrated_pairs.csv', 'cointegrated_close.csv', 'close_only.json')

# files = ['data_15m.csv', 'data_train.csv', 'open_positions.json', 'spreads_df.csv', 'cointegrated_pairs.csv']

# for f in files:
#     os.remove(f)

df = pd.read_csv('closing_spreads_df.csv')

# Assuming 'time' is always fully populated and is the first column
columns_to_shift = df.columns[1:]  # Adjust based on your DataFrame structure

# Shift each column up by the number of leading NaNs
for col in columns_to_shift:
    # Count NaNs at the start of the column
    nans = df[col].isna().cumsum()  # Counts cumulatively number of NaNs
    first_non_nan = nans[nans < len(nans)].idxmax()  # Get first non-NaN index
    # Shift data upwards
    df[col] = df[col].shift(-first_non_nan)

# Drop any rows that are still NaN (which will be at the bottom after shifting)
df.dropna(inplace=True)

# Reset the index after the shift if necessary
df.reset_index(drop=True, inplace=True)

# Optionally, truncate the dataframe to only 201 rows including headers
df = df.iloc[:200]  # Adjust as needed to include headers

df.to_csv('spreads_df.csv', index=False)