import json

# Replace 'your_json_file.json' with the path to your actual JSON file
with open('test_strategy.json', 'r') as file:
    data = json.load(file)

# Initialize variables for counting and summing
number_of_keys = len(data)
sum_final_portfolio_value = sum(item.get("FinalPortfolioValue", 0) for item in data.values())

# Calculate the average if there are any keys
average_final_portfolio_value = sum_final_portfolio_value / number_of_keys if number_of_keys else 0

print("Average Final Portfolio Value:", average_final_portfolio_value)
