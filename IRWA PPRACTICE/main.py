import os
import pandas as pd

# Print the current working directory
print("Current Working Directory:", os.getcwd())

# Try reading the CSV file
data = pd.read_csv('tmdb_5000_movies.csv')

print(data)
