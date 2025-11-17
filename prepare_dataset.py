import pandas as pd

# Load your CSV
df = pd.read_csv("Conversation.csv")

# Make sure the column names match your CSV
# For example, if your CSV has columns 'question' and 'answer', use these
conversations = df.apply(lambda row: f"User: {row['question']} Bot: {row['answer']}", axis=1)

# Save to a text file
with open("training_data.txt", "w", encoding="utf-8") as f:
    for line in conversations:
        f.write(line + "\n")

print("Dataset prepared for training!")
