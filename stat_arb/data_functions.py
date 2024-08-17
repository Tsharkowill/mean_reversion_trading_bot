import pandas as pd
import json
import os

# Function to read keys from JSON and return a list of columns to keep
def get_columns_to_keep(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
        # Assuming the keys you want are the top-level keys in the JSON file
        columns_to_keep = list(data.keys())
    return columns_to_keep

# Function to append data from one CSV to another, based on keys from a JSON file
def append_filtered_data(source_csv_file, target_csv_file, json_file):
    # Step 1: Get the columns to keep from the JSON file
    columns_to_keep = get_columns_to_keep(json_file)
    
    # Step 2: Read the source CSV file
    source_df = pd.read_csv(source_csv_file, usecols=columns_to_keep)
    
    # Step 3: Check if the target CSV file exists to decide on appending/creating
    if os.path.exists(target_csv_file):
        # File exists, read it and append new data
        target_df = pd.read_csv(target_csv_file)
        updated_df = pd.concat([target_df, source_df], ignore_index=True)
    else:
        # File doesn't exist, so just use the source DataFrame as the new data
        updated_df = source_df
    
    # Step 4: Save the updated DataFrame to the target CSV file
    updated_df.to_csv(target_csv_file, index=False)
    print("Data appended successfully.")

def filter_and_append_data(source_csv_file, target_csv_file, json_file):
    # Step 1: Get the pairs to keep from the JSON file
    pairs_to_keep = get_columns_to_keep(json_file)
    
    # Step 2: Read the source CSV file
    source_df = pd.read_csv(source_csv_file)
    
    # Step 3: Filter the DataFrame to only include desired pairs
    # Create a new column that combines Base and Quote for filtering
    source_df['Pair'] = source_df['Base'] + '_' + source_df['Quote']
    filtered_df = source_df[source_df['Pair'].isin(pairs_to_keep)]
    
    # Step 4: Check if the target CSV file exists to decide on appending/creating
    if os.path.exists(target_csv_file):
        # File exists, read it and append new data
        target_df = pd.read_csv(target_csv_file)
        updated_df = pd.concat([target_df, filtered_df], ignore_index=True)
    else:
        # File doesn't exist, so just use the filtered DataFrame as the new data
        updated_df = filtered_df
    
    # Remove the temporary 'Pair' column before saving
    updated_df.drop(columns=['Pair'], inplace=True)
    
    # Step 5: Save the updated DataFrame to the target CSV file
    updated_df.to_csv(target_csv_file, index=False)
    print("Data filtered and appended successfully.")


def merge_json(source_file, target_file):
    # Load or initialize the target data
    if os.path.exists(target_file):
        with open(target_file, 'r') as file:
            target_data = json.load(file)
    else:
        target_data = {}

    # Load the source data
    if os.path.exists(source_file):
        with open(source_file, 'r') as file:
            source_data = json.load(file)
        # Merge source data into target data
        # This simple update will overwrite existing keys in target with source
        # Customize this logic as needed (e.g., merging lists or nested dicts)
        target_data.update(source_data)

        # Save the updated data back into the target file
        with open(target_file, 'w') as file:
            json.dump(target_data, file, indent=4)

        print(f"Data from {source_file} has been merged into {target_file}.")
    else:
        print(f"{source_file} does not exist. No data to merge.")

