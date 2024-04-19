import boto3
import gzip

# Create an S3 client
s3 = boto3.client('s3')

# Specify the bucket name and key of the file to download
bucket_name = 'commoncrawl'
key = 'crawl-data/CC-MAIN-2022-05/wet.paths.gz'
filename = key.split("/")[-1] 
file_location = 'c:/Ananth_personal/Ananth_personal/data-engineering-practice/Exercises/Exercise-3'
dest_file = file_location + '/' + filename

# Download the file
s3.download_file(bucket_name, key, dest_file)



# Specify the path of the downloaded gz file
gz_file_path = 'c:/Ananth_personal/Ananth_personal/data-engineering-practice/Exercises/Exercise-3/wet.paths.gz'

# Specify the path where you want to extract the file
extracted_file_path = 'c:/Ananth_personal/Ananth_personal/data-engineering-practice/Exercises/Exercise-3/wet.paths'

# Open the gz file in read mode
with gzip.open(dest_file, 'rb') as gz_file:
    # Read the contents of the gz file
    gz_content = gz_file.read()

# Write the extracted content to a new file
with open(extracted_file_path, 'wb') as extracted_file:
    extracted_file.write(gz_content)

    # Read the first line of the extracted file
with open(extracted_file_path, 'r') as extracted_file:
        first_line = extracted_file.readline().strip()

filename = first_line.split("/")[-1] 
file_location = 'c:/Ananth_personal/Ananth_personal/data-engineering-practice/Exercises/Exercise-3'
dest_file = file_location + '/' + filename

# Download the file mentioned in the first line
s3.download_file(bucket_name, first_line, dest_file)

# Open the gz file in read mode
with gzip.open(dest_file, 'rb') as gz_file:
    # Read and print the contents line by line
    for line in gz_file:
        print(line.decode().strip())