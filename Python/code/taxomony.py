import pandas as pd
from fuzzywuzzy import fuzz

# Step 1: Load the data
def load_data(sic_file, gpc_file):
    # Load SIC data (CSV format)
    sic_data = pd.read_csv(sic_file)

    # Load GPC data (Excel format)
    gpc_data = pd.read_excel(gpc_file, sheet_name=0)
    
    return sic_data, gpc_data

# Step 2: Clean and prepare the data
def clean_data(sic_data, gpc_data):
    # Convert descriptions to lowercase for keyword matching
    sic_data['SIC_Description_Lower'] = sic_data['Description'].str.lower()
    gpc_data['BrickTitle_Lower'] = gpc_data['BrickTitle'].str.lower()
    return sic_data, gpc_data

# Step 3: Perform direct keyword matching
def keyword_matching(sic_data, gpc_data):
    # Merge based on matching descriptions
    matches = pd.merge(sic_data, gpc_data, left_on='SIC_Description_Lower', right_on='BrickTitle_Lower', how='inner')
    return matches

# Step 4: Fuzzy matching (optional)
def get_best_match(sic_desc, gpc_brick_titles):
    best_match = None
    highest_score = 0
    for title in gpc_brick_titles:
        score = fuzz.ratio(sic_desc, title)
        if score > highest_score:
            highest_score = score
            best_match = title
    return best_match

def fuzzy_matching(sic_data, gpc_data):
    # Apply fuzzy matching
    sic_data['Best_GPC_Match'] = sic_data['SIC_Description_Lower'].apply(lambda x: get_best_match(x, gpc_data['BrickTitle_Lower']))
    
    # Merge based on the best GPC match found
    fuzzy_matches = pd.merge(sic_data, gpc_data, left_on='Best_GPC_Match', right_on='BrickTitle_Lower', how='inner')
    return fuzzy_matches

# Step 5: Export the results
def export_results(matches, filename):
    # Export to CSV
    matches.to_csv(filename, index=False)
    print(f'Results exported to {filename}')

# Main function to run all steps
def main(sic_file, gpc_file, output_file):
    # Load the data
    sic_data, gpc_data = load_data(sic_file, gpc_file)
    
    # Clean the data
    sic_data, gpc_data = clean_data(sic_data, gpc_data)
    
    # Perform keyword matching
    keyword_matches = keyword_matching(sic_data, gpc_data)
    print("Keyword matches found:")
    print(keyword_matches[['SIC Code', 'Description', 'BrickCode', 'BrickTitle']].head())
    
    # If you want to perform fuzzy matching, uncomment the following lines:
    # fuzzy_matches = fuzzy_matching(sic_data, gpc_data)
    # print("Fuzzy matches found:")
    # print(fuzzy_matches[['SIC Code', 'Description', 'BrickCode', 'BrickTitle']].head())

    # Export the results (keyword matches)
    export_results(keyword_matches, output_file)

# Run the script
if __name__ == "__main__":
    # Input files (replace with actual paths to your files)
    sic_file = 'C:\\Users\\ashenoy\\pythoncode_random\\SIC07_CH_condensed_list_en.csv'  # Path to the SIC CSV file
    gpc_file = 'C:\\Users\\ashenoy\\pythoncode_random\\GPC_as_of_May_2024_v20240603_GB.xlsx'  # Path to the GPC Excel file
    output_file = 'C:\\Users\\ashenoy\\pythoncode_random\\SIC_to_GPC_mapping.csv'  # Output file path

    # Run the main function
    main(sic_file, gpc_file, output_file)
