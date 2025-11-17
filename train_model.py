import pandas as pd
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments

# -----------------------------
# Step 1: Load your dataset
# -----------------------------
data_path = "Conversation.csv"  # Make sure this is your CSV filename
df = pd.read_csv(data_path)

# Combine question-answer into one 'text' column for GPT-style training
df['text'] = df['question'].astype(str) + " " + df['answer'].astype(str)

dataset = Dataset.from_pandas(df[['text']])

print("Dataset loaded! Number of examples:", len(dataset))

# -----------------------------
# Step 2: Load tokenizer and model
# -----------------------------
model_name = "gpt2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Fix padding issue
tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = tokenizer.eos_token_id

# -----------------------------
# Step 3: Tokenize dataset
# -----------------------------
def tokenize_function(examples):
    tokens = tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )
    # Add labels (same as input_ids)
    tokens["labels"] = tokens["input_ids"]
    return tokens

tokenized_dataset = dataset.map(tokenize_function, batched=True)
print("Dataset tokenized with labels!")

# -----------------------------
# Step 4: Set training arguments
# -----------------------------
training_args = TrainingArguments(
    output_dir="./chatbot_model",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    save_steps=500,
    save_total_limit=2,
    logging_steps=50,
    learning_rate=5e-5,
    weight_decay=0.01,
    report_to="none"
)

# -----------------------------
# Step 5: Trainer
# -----------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset
)

# -----------------------------
# Step 6: Train
# -----------------------------
trainer.train()
print("Training complete!")

# -----------------------------
# Step 7: Save model
# -----------------------------
trainer.save_model("./chatbot_model")
tokenizer.save_pretrained("./chatbot_model")
print("Model and tokenizer saved!")
