import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load your trained model
model_path = "./chatbot_model"  # Folder where your trained model is saved
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

def chat_with_bot():
    print("My Chatbot 🤖 (type 'quit' to exit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            print("Bot: Goodbye!")
            break

        # Encode input
        inputs = tokenizer(user_input, return_tensors="pt").to(device)

        # Generate response
        outputs = model.generate(
            **inputs,
            max_length=100,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            top_p=0.9,
            temperature=0.7
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        print(f"Bot: {response}")

if __name__ == "__main__":
    chat_with_bot()
