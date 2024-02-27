import pandas as pd
import numpy as np
import time
import math
from pprint import pprint
from datetime import datetime, timedelta


# Format number
def format_number(curr_num, match_num):

  """
    Give current number an example of number with decimals desired
    Function will return the correctly formatted string
  """

  curr_num_string = f"{curr_num}"
  match_num_string = f"{match_num}"

  if "." in match_num_string:
    match_decimals = len(match_num_string.split(".")[1])
    curr_num_string = f"{curr_num:.{match_decimals}f}"
    curr_num_string = curr_num_string[:]
    return curr_num_string
  else:
    return f"{int(curr_num)}"
  




# Helper function to convert datetime to Unix timestamp in milliseconds and round down to the nearest hour
def to_unix_milliseconds_rounded(dt):
    # Round down to the nearest hour
    dt_rounded = dt.replace(minute=0, second=0, microsecond=0)
    return int(dt_rounded.timestamp() * 1000)

def get_unix_times():
    # Get current datetime and round down to the nearest hour
    current_time = datetime.now()
    current_time_rounded = current_time.replace(minute=0, second=0, microsecond=0)
    
    # Initialize the dictionary to store time ranges
    times_dict = {}
    hours_step = 200  # Define the hours to step back for each range
    
    # Generate sequential time ranges
    for i in range(1, 5):
        end_time = current_time_rounded - timedelta(hours=(i-1) * hours_step)
        start_time = current_time_rounded - timedelta(hours=i * hours_step)
        
        times_dict[f"range_{i}"] = {
            "from_unix": to_unix_milliseconds_rounded(start_time),
            "to_unix": to_unix_milliseconds_rounded(end_time),
        }
    
    return times_dict


print(get_unix_times())
