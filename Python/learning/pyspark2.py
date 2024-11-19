from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date
import os
os.environ["HADOOP_HOME"] = "C:\software\pyspark\Winutils"



def create_spark_session():
    """
    Create a Spark session.
    """
    spark = SparkSession.builder.master("local[*]").appName("CSVInZipProcessing").getOrCreate()

    return spark

def read_csv_in_zip(spark, source_folder):
    """
    Read a CSV file in zip format using PySpark.
    """
    # Assuming the CSV file is the first file inside the zip archive
    csv_file = f"{source_folder}/Divvy_Trips_2019_Q4.csv"
    print(csv_file)
    
    # Reading CSV in zip
    print("Reading CSV in zip format...")
    df = spark.read.csv(csv_file, header=True, inferSchema=True)
    return df

def calculate_average_trip_duration(df, output_folder):
    """
    Calculate the average trip duration per day and save the result in CSV format.
    """
    # Convert start_time to date type
    df = df.withColumn("start_date", to_date(col("start_time")))
    
    # Calculate average trip duration per day
    avg_duration_per_day = df.groupBy("start_date").agg({"tripduration": "avg"})
    
    # Rename columns for clarity
    avg_duration_per_day = avg_duration_per_day.withColumnRenamed("avg(tripduration)", "average_trip_duration")
    
    # Save the result DataFrame to a new CSV file
    output_file = f"{output_folder}/average_trip_duration.csv"
    avg_duration_per_day.write.csv(output_file, header=True, mode="overwrite")

def main():
    # Specify your source and output folders
    source_folder = "C:/Ananth_personal/Ananth_personal/data-engineering-practice/Exercises/Exercise-6/data"
    output_folder = "C:/Ananth_personal/Ananth_personal/data-engineering-practice/Exercises/Exercise-6/reports"

    # Create a Spark session
    spark = create_spark_session()
    
    # Read CSV in zip format
    
    df = read_csv_in_zip(spark, source_folder)
    print("CSV in zip format read successfully.")

    # Calculate average trip duration per day and save the result in CSV format
    print("Calculating average trip duration per day...")
    calculate_average_trip_duration(df, output_folder)
    print("Average trip duration per day calculated and saved in CSV format.")

    # Stop the Spark session
    spark.stop()

# Run the main function
if __name__ == "__main__":
    main()
