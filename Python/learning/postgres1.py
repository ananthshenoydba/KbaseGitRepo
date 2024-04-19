import psycopg
import os
from psycopg import sql

# Function to execute SQL files
def execute_sql_file(cursor, file_path):
    with open(file_path, "r") as file:
        sql = file.read()
        cursor.execute(sql)

def convert_sqlfilename_to_csv(file_name):
    if file_name.endswith(".sql"):
        #csv_file_name = file_name.rstrip(".sql") + ".csv"
        csv_file_name = os.path.splitext(file_name)[0]+'.csv'
        return csv_file_name
    else:
        return None  # Return None if the input file name doesn't end with ".sql"

# Connect to the database
conn = psycopg.connect(
    host="localhost",
    dbname="pytest",
    user="postgres",
    password="poochu",
    options="-c search_path=pytest,public"
)

# Create a cursor object
cursor = conn.cursor()

# Path to the master SQL file
master_sql_file = "C:/Ananth_personal/Ananth_personal/data-engineering-practice/Exercises/Exercise-5/data/master.sql"

# Read the master SQL file and get the list of SQL files
with open(master_sql_file, "r") as file:
    sql_files = file.read().splitlines()

# Execute each SQL file
for sql_file in sql_files:
    sql_file_path = os.path.join(os.path.dirname(master_sql_file), sql_file)
    execute_sql_file(cursor, sql_file_path)
    print(f"Executed: {sql_file}")
    csv_name = convert_sqlfilename_to_csv(sql_file)
    table_name = sql_file.split('/')[-1].split('.')[0]
    if os.path.isfile(csv_name):
        with open(csv_name) as f:
            with cursor.copy(sql.SQL('COPY {} FROM STDIN WITH(FORMAT CSV, HEADER)').format(sql.Identifier(table_name))) as copy:
                while data := f.read(100):
                    print(data)
                    copy.write(data)
        conn.commit()
    else:
        print(f"CSV file not found for table: {table_name}")

# Commit the changes and close the cursor and connection
conn.commit()
cursor.close()
conn.close()
