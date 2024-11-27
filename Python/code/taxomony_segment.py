import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz

# Step 1: Load the SIC and GPC data
def load_data(sic_file, gpc_file):
    # Load SIC data (CSV format)
    sic_data = pd.read_csv(sic_file)

    # Load GPC data (Excel format)
    gpc_data = pd.read_excel(gpc_file, sheet_name=0)  # Assuming Segment data is in the same sheet
    
    return sic_data, gpc_data

# Step 2: Clean and preprocess the data
def clean_data(sic_data, gpc_data):
    # Convert descriptions to lowercase for comparison
    sic_data['SIC_Description_Lower'] = sic_data['Description'].str.lower()
    gpc_data['SegmentTitle_Lower'] = gpc_data['SegmentTitle'].str.lower()  # Use SegmentTitle instead of BrickTitle
    
    # Remove special characters and numbers, keep only words
    sic_data['SIC_Description_Clean'] = sic_data['SIC_Description_Lower'].apply(lambda x: re.sub(r'[^a-z\s]', '', x))
    gpc_data['SegmentTitle_Clean'] = gpc_data['SegmentTitle_Lower'].apply(lambda x: re.sub(r'[^a-z\s]', '', x))
    
    return sic_data, gpc_data

# Step 3: Apply TF-IDF vectorization to compare text similarity
def tfidf_similarity(sic_data, gpc_data):
    # Combine all descriptions and Segment Titles into one corpus
    all_descriptions = pd.concat([sic_data['SIC_Description_Clean'], gpc_data['SegmentTitle_Clean']])

    # Create a TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_descriptions)

    # Separate the TF-IDF matrices for SIC and GPC descriptions
    sic_tfidf = tfidf_matrix[:len(sic_data)]
    gpc_tfidf = tfidf_matrix[len(sic_data):]

    # Compute cosine similarity between SIC descriptions and GPC Segment Titles
    similarity_matrix = cosine_similarity(sic_tfidf, gpc_tfidf)
    
    return similarity_matrix

# Step 4: Apply fuzzy matching as a backup method
def fuzzy_match(sic_description, gpc_description):
    return fuzz.token_sort_ratio(sic_description, gpc_description)

# Step 5: Match SIC codes to GPC Segment Titles
def match_sic_to_gpc(sic_data, gpc_data, similarity_matrix):
    matched_rows = []

    # For each SIC description, find the best GPC Segment match
    for i, sic_row in sic_data.iterrows():
        # Get similarity scores for the current SIC description
        similarity_scores = similarity_matrix[i]
        
        # Find the index of the best match (highest cosine similarity score)
        best_match_idx = similarity_scores.argmax()
        
        # Fuzzy matching for additional comparison
        fuzzy_score = fuzzy_match(sic_row['SIC_Description_Clean'], gpc_data.iloc[best_match_idx]['SegmentTitle_Clean'])
        
        matched_rows.append({
            'SIC Code': sic_row['SIC Code'],
            'SIC Description': sic_row['Description'],
            'GPC SegmentCode': gpc_data.iloc[best_match_idx]['SegmentCode'],
            'GPC SegmentTitle': gpc_data.iloc[best_match_idx]['SegmentTitle'],
            'Cosine Similarity Score': similarity_scores[best_match_idx],
            'Fuzzy Score': fuzzy_score
        })

    return pd.DataFrame(matched_rows)

# Step 6: Export the results
def export_results(matches, filename):
    # Export to CSV
    matches.to_csv(filename, index=False)
    print(f'Results exported to {filename}')

# Main function to run all steps
def main(sic_file, gpc_file, output_file):
    # Load the data
    sic_data, gpc_data = load_data(sic_file, gpc_file)
    
    # Clean and preprocess the data
    sic_data, gpc_data = clean_data(sic_data, gpc_data)
    
    # Compute TF-IDF similarity
    similarity_matrix = tfidf_similarity(sic_data, gpc_data)
    
    # Match SIC codes to GPC Segment Titles based on similarity
    matches = match_sic_to_gpc(sic_data, gpc_data, similarity_matrix)
    print("Matches found:")
    print(matches[['SIC Code', 'SIC Description', 'GPC SegmentCode', 'GPC SegmentTitle', 'Cosine Similarity Score', 'Fuzzy Score']].head())
    
    # Export the results
    export_results(matches, output_file)

# Run the script
if __name__ == "__main__":
    # Input files (replace with actual paths to your files)
    sic_file = 'C:\\Users\\ashenoy\\pythoncode_random\\SIC07_CH_condensed_list_en.csv'  # Path to the SIC CSV file
    gpc_file = 'C:\\Users\\ashenoy\\pythoncode_random\\GPC_as_of_May_2024_v20240603_GB.xlsx'  # Path to the GPC Excel file
    output_file = 'C:\\Users\\ashenoy\\pythoncode_random\\SIC_to_GPC_Segment_mapping.csv'  # Output file path

    # Run the main function
    main(sic_file, gpc_file, output_file)
