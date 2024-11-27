import pandas as pd

# Define the file paths
csv_file_path = 'C:\\Users\\ashenoy\\pythoncode_random\\rapex_mapping.csv'
html_file_path = 'C:\\Users\\ashenoy\\pythoncode_random\\searchable_dropdowns.html'

# Read the CSV file
df = pd.read_csv(csv_file_path)

# Get the column names
columns = df.columns.tolist()

# Get unique values for each column
dropdown_options = {col: df[col].dropna().unique().tolist() for col in columns}

# Generate HTML content
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Searchable Dropdowns</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/css/select2.min.css" rel="stylesheet" />
</head>
<body>
    <form>
"""

# Add dropdowns to HTML content
for col in columns:
    html_content += f"""
    <label for="{col}">{col}:</label>
    <select id="{col}" name="{col}" class="searchable-dropdown">
"""
    for option in dropdown_options[col]:
        html_content += f"""
        <option value="{option}">{option}</option>
"""
    html_content += """
    </select>
    <br><br>
"""

# Add Clear button to HTML content
html_content += """
    <button type="button" id="clear-button">Clear</button>
    <br><br>
"""

# Add JavaScript for making dropdowns searchable, dynamically filtering options, and clearing selections
html_content += """
    </form>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/js/select2.min.js"></script>
    <script>
        $(document).ready(function() {
            $('.searchable-dropdown').select2();

            var data = """ + df.to_json(orient='records') + """;

            function filterDropdowns(changedDropdownId, selectedValue) {
                var filteredData = data;

                // Filter data based on selected value
                if (selectedValue) {
                    filteredData = data.filter(function(row) {
                        return row[changedDropdownId] === selectedValue;
                    });
                }

                // Update options for other dropdowns
                $('.searchable-dropdown').each(function() {
                    var dropdownId = $(this).attr('id');
                    if (dropdownId !== changedDropdownId) {
                        var options = new Set(filteredData.map(function(row) {
                            return row[dropdownId];
                        }));
                        $(this).empty();
                        options.forEach(function(option) {
                            $(this).append(new Option(option, option));
                        }.bind(this));
                    }
                });

                // Reinitialize Select2
                $('.searchable-dropdown').select2();
            }

            $('.searchable-dropdown').change(function() {
                var selectedValue = $(this).val();
                var changedDropdownId = $(this).attr('id');
                filterDropdowns(changedDropdownId, selectedValue);
            });

            $('#clear-button').click(function() {
                $('.searchable-dropdown').val(null).trigger('change');
                $('.searchable-dropdown').each(function() {
                    var dropdownId = $(this).attr('id');
                    var options = new Set(data.map(function(row) {
                        return row[dropdownId];
                    }));
                    $(this).empty();
                    options.forEach(function(option) {
                        $(this).append(new Option(option, option));
                    }.bind(this));
                });

                // Reinitialize Select2
                $('.searchable-dropdown').select2();
            });
        });
    </script>
</body>
</html>
"""

# Save the HTML content to a file
with open(html_file_path, 'w') as file:
    file.write(html_content)

print(f"HTML file generated at: {html_file_path}")
