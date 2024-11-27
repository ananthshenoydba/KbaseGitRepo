import pandas as pd
from transformers import pipeline

# Load your product and category files
products_df = pd.read_csv('C:/Users/ashenoy/OneDrive - TRIAD GROUP PLC/BEIS/Taxonomy/PSD/products_202410171145.csv')
category_subcategory_df = pd.read_excel('C:/Users/ashenoy/OneDrive - TRIAD GROUP PLC/BEIS/Taxonomy/PSD/category_subcategory.xlsx')

# Combine 'name', 'description', 'category', and 'subcategory' for better context in matching
products_df['combined_text'] = (
    products_df['name'].fillna('') + ' ' + 
    products_df['description'].fillna('') + ' ' + 
    products_df['category'].fillna('') + ' ' +
    products_df['subcategory'].fillna('')  # Include subcategory as well
)

# Initialize the zero-shot classification pipeline with a model
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Function to classify products row by row
def classify_product(text, subcategories):
    try:
        # Classify the product's information
        result = classifier(text, subcategories)
        best_label = result['labels'][0]
        score = result['scores'][0]
        return best_label, score
    except Exception as e:
        print(f"Error during classification: {e}")
        return None, None

# Define subcategories
subcategories = category_subcategory_df['sub-category'].tolist()

# Initialize lists for results
matched_subcategories = []
confidence_scores = []

# Process each product row-by-row and log each step
for index, row in products_df.iterrows():
    combined_text = row['combined_text']
    
    # Log the row processing
    print(f"Processing Row {index + 1}/{len(products_df)}:")
    print(f"Name: {row['name']}")
    print(f"Description: {row['description']}")
    
    # Run the classification for the current row
    best_label, score = classify_product(combined_text, subcategories)
    
    # Append results to the lists
    matched_subcategories.append(best_label)
    confidence_scores.append(score)
    
    # Log the result for the current row
    print(f"Predicted Subcategory: {best_label}")
    print(f"Confidence Score: {score}")
    print("-" * 40)

# Add the new columns to the DataFrame
products_df['matched_subcategory'] = matched_subcategories
products_df['confidence_score'] = confidence_scores

# Save the updated DataFrame with the new subcategory and confidence scores
output_file = 'C:/Users/ashenoy/OneDrive - TRIAD GROUP PLC/BEIS/Taxonomy/PSD/updated_products_with_subcategories_fbbart.csv'
products_df.to_csv(output_file, index=False)

print(f"Updated products file saved to {output_file}")

# Show a few matched results as a preview
print(products_df[['name', 'description', 'category', 'subcategory', 'matched_subcategory', 'confidence_score']].head())