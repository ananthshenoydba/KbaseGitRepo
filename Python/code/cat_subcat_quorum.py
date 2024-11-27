import pandas as pd
import json
from sentence_transformers import SentenceTransformer, util
import numpy as np
from collections import Counter

# Load the product and category files
products_df = pd.read_csv('C:/Users/ashenoy/OneDrive - TRIAD GROUP PLC/BEIS/Taxonomy/PSD/products_202410311558.csv')
category_subcategory_df = pd.read_excel('C:/Users/ashenoy/OneDrive - TRIAD GROUP PLC/BEIS/Taxonomy/PSD/category_subcategory.xlsx')

# Prepare product information
products_df['product_json'] = products_df.apply(
    lambda row: json.dumps({
        'name': row['name'],
        'description': row['description'],
        'category': row['category'],
        'subcategory': row['subcategory']
    }, ensure_ascii=False), axis=1
)

products_df['combined_text'] = (
    products_df['name'].fillna('') + ' ' + 
    products_df['description'].fillna('') + ' ' + 
    products_df['category'].fillna('') + ' ' + 
    products_df['subcategory'].fillna('')
)

# Initialize the models
model_names = [
    'all-MiniLM-L6-v2',
    'all-mpnet-base-v2',
    'all-distilroberta-v1',
    'stsb-roberta-large'
]

models = {name: SentenceTransformer(name) for name in model_names}

# Prepare to store results
results = []

# Generate embeddings and calculate similarities for each model
for model_name, model in models.items():
    print(f"Processing model: {model_name}")

    # JSON embeddings
    product_json_embeddings = model.encode(products_df['product_json'].tolist(), convert_to_tensor=True)
    subcategory_embeddings = model.encode(category_subcategory_df['sub-category'].fillna('').tolist(), convert_to_tensor=True)

    cosine_scores_json = util.pytorch_cos_sim(product_json_embeddings, subcategory_embeddings)

    # Text embeddings
    product_text_embeddings = model.encode(products_df['combined_text'].tolist(), convert_to_tensor=True)

    cosine_scores_text = util.pytorch_cos_sim(product_text_embeddings, subcategory_embeddings)

    # Store results
    for i in range(len(products_df)):
        # JSON-based results
        best_match_idx_json = cosine_scores_json[i].argmax().item()
        best_match_score_json = cosine_scores_json[i][best_match_idx_json].item()
        matched_subcategory_json = category_subcategory_df.iloc[best_match_idx_json]['sub-category']

        # Text-based results
        best_match_idx_text = cosine_scores_text[i].argmax().item()
        best_match_score_text = cosine_scores_text[i][best_match_idx_text].item()
        matched_subcategory_text = category_subcategory_df.iloc[best_match_idx_text]['sub-category']

        results.append({
            'model': model_name,
            'index': i,
            'matched_subcategory_json': matched_subcategory_json,
            'similarity_score_json': best_match_score_json,
            'matched_subcategory_text': matched_subcategory_text,
            'similarity_score_text': best_match_score_text
        })

# Create a DataFrame to analyze results
results_df = pd.DataFrame(results)

# Determine the final subcategory using quorum decision
# Determine the final subcategory using quorum decision
# Determine the final subcategory using quorum decision
final_results = []

for i in range(len(products_df)):
    subcategory_votes = results_df[results_df['index'] == i][['matched_subcategory_json', 'matched_subcategory_text']]
    scores_json = results_df[results_df['index'] == i]['similarity_score_json'].values  # Convert to numpy array
    scores_text = results_df[results_df['index'] == i]['similarity_score_text'].values  # Convert to numpy array

    # Combine votes and their scores
    combined_votes = Counter()
    
    # Use a relative index for scores access
    for rel_index, row in enumerate(subcategory_votes.iterrows()):
        combined_votes[row[1]['matched_subcategory_json']] += scores_json[rel_index]  # Access using relative index
        combined_votes[row[1]['matched_subcategory_text']] += scores_text[rel_index]  # Access using relative index

    # Determine the final subcategory and score
    final_subcategory, final_score = combined_votes.most_common(1)[0]
    final_results.append({'final_subcategory': final_subcategory, 'final_score': final_score})

# Add final results to the original products DataFrame
final_results_df = pd.DataFrame(final_results)
products_df = pd.concat([products_df, final_results_df], axis=1)

# Save the updated DataFrame
output_file = 'C:/Users/ashenoy/OneDrive - TRIAD GROUP PLC/BEIS/Taxonomy/PSD/updated_products_with_final_subcategory.csv'
products_df.to_csv(output_file, index=False)

print(f"Updated products file saved to {output_file}")

# Show a few matched results as a preview
print(products_df[['name', 'description', 'category', 'final_subcategory', 'final_score']].head())