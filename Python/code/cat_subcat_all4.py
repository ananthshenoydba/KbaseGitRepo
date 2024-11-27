import pandas as pd
import json
from sentence_transformers import SentenceTransformer, util

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

# Prepare to store results for each model
for model_name, model in models.items():
    print(f"Processing model: {model_name}")

    # JSON embeddings
    product_json_embeddings = model.encode(products_df['product_json'].tolist(), convert_to_tensor=True)
    subcategory_embeddings = model.encode(category_subcategory_df['sub-category'].fillna('').tolist(), convert_to_tensor=True)

    cosine_scores_json = util.pytorch_cos_sim(product_json_embeddings, subcategory_embeddings)

    # Text embeddings
    product_text_embeddings = model.encode(products_df['combined_text'].tolist(), convert_to_tensor=True)

    cosine_scores_text = util.pytorch_cos_sim(product_text_embeddings, subcategory_embeddings)

    # Store the results of each model for each product
    matched_subcategory_json = []
    matched_subcategory_text = []
    similarity_score_json = []
    similarity_score_text = []

    for i in range(len(products_df)):
        # JSON-based results
        best_match_idx_json = cosine_scores_json[i].argmax().item()
        best_match_score_json = cosine_scores_json[i][best_match_idx_json].item()
        matched_subcategory_json.append(category_subcategory_df.iloc[best_match_idx_json]['sub-category'])
        similarity_score_json.append(best_match_score_json)

        # Text-based results
        best_match_idx_text = cosine_scores_text[i].argmax().item()
        best_match_score_text = cosine_scores_text[i][best_match_idx_text].item()
        matched_subcategory_text.append(category_subcategory_df.iloc[best_match_idx_text]['sub-category'])
        similarity_score_text.append(best_match_score_text)

    # Add columns for this model's results to the products_df DataFrame
    products_df[f'{model_name}_subcat_json'] = matched_subcategory_json
    products_df[f'{model_name}_score_json'] = similarity_score_json
    products_df[f'{model_name}_subcat_text'] = matched_subcategory_text
    products_df[f'{model_name}_score_text'] = similarity_score_text

# Save the updated DataFrame with results from all models
output_file = 'C:/Users/ashenoy/OneDrive - TRIAD GROUP PLC/BEIS/Taxonomy/PSD/updated_products_with_all_models_2024.csv'
products_df.to_csv(output_file, index=False)

print(f"Updated products file saved to {output_file}")

# Show a few matched results as a preview
print(products_df.head())