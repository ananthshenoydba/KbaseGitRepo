from pyspark.sql import SparkSession
from io import BytesIO
import zipfile

# Create a Spark session
spark = SparkSession.builder.appName("CSVProcessing").getOrCreate()

# Replace 'your_input_directory' with the path to the directory containing zip files
input_directory = 'C:\Ananth_personal\Ananth_personal\data-engineering-practice\Exercises\Exercise-6\data'

# Replace 'your_output_directory' with the path to the directory where you want to store the result
output_directory = 'C:\Ananth_personal\Ananth_personal\data-engineering-practice\Exercises\Exercise-6\reports'

# Function to process zip file content
def process_zip_content(file_name, content):
    with zipfile.ZipFile(BytesIO(content), "r") as zip_file:
        # Read all CSV content from the zip file
        all_csv_content = [zip_file.read(csv_file) for csv_file in zip_file.namelist() if csv_file.endswith('.csv')]

        # Concatenate all CSV content
        combined_csv_content = b'\n'.join(all_csv_content)

        # Convert combined CSV content to Spark DataFrame
        df = spark.read.csv(BytesIO(combined_csv_content), header=True, inferSchema=True)

        # Run a sample query (replace with your actual query)
        result_df = df.groupBy("column_name").agg(F.avg("numeric_column").alias("average_value"))

        # Show the result
        result_df.show()

        # Store the result in CSV format
        result_csv_path = f'{output_directory}/{file_name}_result.csv'
        result_df.write.csv(result_csv_path, header=True, mode="overwrite")

        print(f"Result stored in CSV format at: {result_csv_path}")

# Read binary content of each zip file
zip_files = spark.sparkContext.binaryFiles(f'{input_directory}/*.zip')

# Process each zip file
zip_files.foreach(lambda x: process_zip_content(x[0], x[1]))

# Stop the Spark session
spark.stop()
