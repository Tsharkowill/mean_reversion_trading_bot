from datetime import datetime, timedelta

# Helper function to convert datetime to Unix timestamp in milliseconds and round down to the nearest 15 minutes
def to_unix_milliseconds_rounded(dt):
    # Calculate the number of minutes to subtract to round down to the nearest 15 minutes
    minutes_to_subtract = dt.minute % 15
    # Round down to the nearest 15 minutes
    dt_rounded = dt.replace(minute=dt.minute - minutes_to_subtract, second=0, microsecond=0)
    return int(dt_rounded.timestamp() * 1000)

def get_unix_times(steps):
    # Get current datetime and round down to the nearest 15 minutes
    current_time = datetime.now()
    current_time_rounded = current_time - timedelta(minutes=current_time.minute % 15, seconds=current_time.second, microseconds=current_time.microsecond)
    
    # Initialize the dictionary to store time ranges
    times_dict = {}
    intervals_step = 200  # Define the number of 15-minute intervals to step back for each range. For example, 800 intervals of 15 minutes each equal 200 hours.
    
    # Generate sequential time ranges
    for i in range(1, steps):
        end_time = current_time_rounded - timedelta(minutes=(i-1) * intervals_step * 15)
        start_time = current_time_rounded - timedelta(minutes=i * intervals_step * 15)
        
        times_dict[f"range_{i}"] = {
            "from_unix": to_unix_milliseconds_rounded(start_time),
            "to_unix": to_unix_milliseconds_rounded(end_time),
        }
    
    return times_dict


