import pandas as pd

# Use the exact filename
data_path = "Conversation.csv"

# Load the dataset
df = pd.read_csv(data_path)

# Show first 5 rows to check
print(df.head())
