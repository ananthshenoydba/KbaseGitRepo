from transformers import pipeline

print("Initializing classifier...")
classifier = pipeline("zero-shot-classification", model="paraphrase-MPNet-base-v2")
print("Classifier initialized.")

test_text = "Cordless Drill, DW-168-08 A cordless drill with 21V battery packs and a charger. Machinery Cordless Drill"
subcategories = ["Drill Presses/Mortisers (Powered)", "Drills - Combination (Powered) ELECTRIC - CORDED", "Drills - Combination (Powered) ELECTRIC - cordless", "Drills - Combination (Powered) ELECTRIC - PETROL/GASOLINE", "Drills - Combination (Powered) ELECTRIC - PNEUMATIC", "Drills - Consumables", "Drills - Replacement Parts/Accessories", "Drills (Non Powered)", "Hammer Drill and Impact Driver Kit (Powered)", "Hammer Drills (Powered)", "Drill/Drivers (Powered)", "Other"]

result = classifier(test_text, subcategories)
print(result)
