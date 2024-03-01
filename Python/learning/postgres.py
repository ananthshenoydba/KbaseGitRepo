import psycopg
from psycopg import sql

# Connect to the PostgreSQL database
conn = psycopg.connect(
    host="localhost",
    dbname="pytest",
    user="postgres",
    password="poochu",
    options="-c search_path=pytest,public"
)

# Create a cursor object
cur = conn.cursor()

# Read the .sql file
with open("C:/Ananth_personal/Ananth_personal/data-engineering-practice/Exercises/Exercise-5/data/accounts.sql", "r") as file:
    # Execute the SQL commands in the file
    cur.execute(sql.SQL(file.read()))

# Commit the changes
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
