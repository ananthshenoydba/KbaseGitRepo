import pandas as pd
import json
from sentence_transformers import SentenceTransformer, util

# Load the product and category files
products_df = pd.read_csv('C:/Users/ashenoy/OneDrive - TRIAD GROUP PLC/BEIS/Taxonomy/PSD/products_202410171145.csv')
category_subcategory_df = pd.read_excel('C:/Users/ashenoy/OneDrive - TRIAD GROUP PLC/BEIS/Taxonomy/PSD/category_subcategory.xlsx')

# Method 1: Convert each row into a JSON object with 'name', 'description', 'category', 'subcategory'
products_df['product_json'] = products_df.apply(
    lambda row: json.dumps({
        'name': row['name'],
        'description': row['description'],
        'category': row['category'],
        'subcategory': row['subcategory']
    }, ensure_ascii=False), axis=1
)

# Method 2: Concatenate 'name', 'description', 'category', and 'subcategory' into a single string
products_df['combined_text'] = (
    products_df['name'].fillna('') + ' ' + 
    products_df['description'].fillna('') + ' ' + 
    products_df['category'].fillna('') + ' ' + 
    products_df['subcategory'].fillna('')
)

# Initialize the pre-trained transformer model (Sentence-BERT)
model = SentenceTransformer('paraphrase-MPNet-base-v2')  # You can replace with any model of your choice

# Method 1: Encode the product data (each JSON object) into embeddings
print("Generating embeddings for products (JSON based)...")
product_json_embeddings = model.encode(products_df['product_json'].tolist(), convert_to_tensor=True)

# Method 2: Encode the concatenated text into embeddings
print("Generating embeddings for products (concatenated string based)...")
product_text_embeddings = model.encode(products_df['combined_text'].tolist(), convert_to_tensor=True)

# Encode the subcategory descriptions from the category_subcategory file into embeddings
print("Generating embeddings for subcategories...")
subcategory_embeddings = model.encode(category_subcategory_df['sub-category'].fillna('').tolist(), convert_to_tensor=True)

# Compute cosine similarity between each product (JSON object) and each subcategory (Method 1)
print("Calculating cosine similarities for JSON-based matching...")
cosine_scores_json = util.pytorch_cos_sim(product_json_embeddings, subcategory_embeddings)

# Compute cosine similarity between each product (concatenated text) and each subcategory (Method 2)
print("Calculating cosine similarities for concatenated-text-based matching...")
cosine_scores_text = util.pytorch_cos_sim(product_text_embeddings, subcategory_embeddings)

# Method 1: For each product, find the index of the subcategory with the highest similarity score (JSON-based)
best_match_indices_json = cosine_scores_json.argmax(dim=1).tolist()  # Convert tensor to list
best_match_scores_json = cosine_scores_json.max(dim=1).values.tolist()  # Get max similarity score for each product

# Method 2: For each product, find the index of the subcategory with the highest similarity score (Concatenated string-based)
best_match_indices_text = cosine_scores_text.argmax(dim=1).tolist()  # Convert tensor to list
best_match_scores_text = cosine_scores_text.max(dim=1).values.tolist()  # Get max similarity score for each product

# Add the matched subcategory and similarity score (JSON-based) back to the products dataframe
products_df['matched_subcategory_json'] = [category_subcategory_df.iloc[idx]['sub-category'] for idx in best_match_indices_json]
products_df['similarity_score_json'] = best_match_scores_json

# Add the matched subcategory and similarity score (Concatenated string-based) back to the products dataframe
products_df['matched_subcategory_text'] = [category_subcategory_df.iloc[idx]['sub-category'] for idx in best_match_indices_text]
products_df['similarity_score_text'] = best_match_scores_text

# Save the updated DataFrame with both classification results (JSON and concatenated text) and their respective scores
output_file = 'C:/Users/ashenoy/OneDrive - TRIAD GROUP PLC/BEIS/Taxonomy/PSD/updated_products_with_ai_subcategories_json_and_text.csv'
products_df.to_csv(output_file, index=False)

print(f"Updated products file saved to {output_file}")

# Show a few matched results as a preview
print(products_df[['name', 'description', 'category', 'matched_subcategory_json', 'similarity_score_json', 
                   'matched_subcategory_text', 'similarity_score_text']].head())
