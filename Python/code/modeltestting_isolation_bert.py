import torch
from transformers import BertTokenizer, BertForSequenceClassification
from transformers import pipeline

# Check if a GPU is available and use it if possible
device = 0 if torch.cuda.is_available() else -1

# Load the tokenizer and model
model_name = "paraphrase-MPNet-base-v2"  # You can choose any BERT model
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(model_name)

# Create a zero-shot classification pipeline
classifier = pipeline("zero-shot-classification", model=model, tokenizer=tokenizer, device=device)

# Define your test text and subcategories
test_text = "Cordless Drill, DW-168-08 A cordless drill with 21V battery packs and a charger. Cordless Drill"
subcategories = [
    "Drill Presses/Mortisers (Powered)", 
    "Drills - Combination (Powered) ELECTRIC - CORDED", 
    "Drills - Combination (Powered) ELECTRIC - cordless", 
    "Drills - Combination (Powered) ELECTRIC - PETROL/GASOLINE", 
    "Drills - Combination (Powered) ELECTRIC - PNEUMATIC", 
    "Drills - Consumables", 
    "Drills - Replacement Parts/Accessories", 
    "Drills (Non Powered)", 
    "Hammer Drill and Impact Driver Kit (Powered)", 
    "Hammer Drills (Powered)", 
    "Drill/Drivers (Powered)", 
    "Other"
]

# Classify the text
result = classifier(test_text, subcategories)

# Print the result
print(result)
