"""
    Script to take the pg_dump of the database/schema/tables
    usage: postgres_dump.py [-h] -v DESTINATION -H HOST -U USERNAME -d DATABASE -f FILENAME [-n SCHEMAS] [-t TABLES] [--port PORT] [--region REGION] [--run]
    The parameters -v, -H, -U, -d -f are definetely needed. 
    example
    python postgres_dump.py -v /home/cloudshell-user/testbackup -H "sample-dbhost.amazon.com" -U cds_test_owner_role -d opss_datapipe_test_cds -f fulldb.dump.
    If the command is run as above it just constructs the command it will run and print it. If its run with the --run option it executes and takes the backup dump.

"""

import argparse
import os
import socket
import subprocess
import sys
import logging
from datetime import datetime
import psycopg

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_host(host):
    try:
        socket.gethostbyname(host)
        return True
    except socket.gaierror:
        return False

def verify_destination(destination):
    return os.path.isdir(destination)

def parse_list(input_string):
    return [item.strip() for item in input_string.split(',')] if input_string else []

def generate_db_auth_token(hostname, username, port, region):
    try:
        cmd = f"aws rds generate-db-auth-token --hostname {hostname} --port {port} --region {region} --username {username}"
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating DB auth token: {e}")
        sys.exit(1)

def verify_schemas_and_tables(host, port, database, username, password, schemas, tables):
    try:
        conn = psycopg.connect(
            host=host,
            port=port,
            dbname=database,
            user=username,
            password=password
        )
        cursor = conn.cursor()

        # Check schemas
        if schemas:
            schema_list = parse_list(schemas)
            placeholders = ','.join(['%s'] * len(schema_list))
            cursor.execute(f"select schema_name from information_schema.schemata where schema_name in ({placeholders})", schema_list)
            existing_schemas = set(row[0] for row in cursor.fetchall())
            non_existing_schemas = set(schema_list) - existing_schemas
            if non_existing_schemas:
                logger.error(f"The following schemas do not exist in the database: {', '.join(non_existing_schemas)}")
                return False

        # Check tables
        if tables:
            table_list = parse_list(tables)
            non_existing_tables = []
            for table in table_list:
                schema, table_name = table.split('.') if '.' in table else ('public', table)
                cursor.execute("select 1 from information_schema.tables where table_schema = %s and table_name = %s", (schema, table_name))
                if cursor.fetchone() is None:
                    non_existing_tables.append(table)
            
            if non_existing_tables:
                logger.error(f"The following tables do not exist in the database: {', '.join(non_existing_tables)}")
                return False

        return True
    except psycopg.Error as e:
        logger.error(f"Error connecting to the database: {e}")
        return False
    finally:
        if conn:
            conn.close()

def construct_docker_command(host, username, password, destination, database, filename, schemas=None, tables=None):
    # Add date-time suffix to the filename
    current_time = datetime.now().strftime("%d%m%y_%H%M")
    filename_with_suffix = f"{os.path.splitext(filename)[0]}_{current_time}{os.path.splitext(filename)[1]}"
    
    command = f"""docker run --rm \
    -v {destination}:/tmp \
    -e PGPASSWORD="{password}" \
    postgres:16 \
    pg_dump -h {host} -U {username} -d {database} -F c -f /tmp/{filename_with_suffix} -v"""

    # Add -n option for schemas
    if schemas:
        for schema in parse_list(schemas):
            command += f" -n {schema}"
    #elif not tables:
        # Exclude aws_commons and aws_s3 schemas for full database dump
    #    command += " -N 'aws_commons' -N 'aws_s3'"

    # Add -t option for tables
    if tables:
        for table in parse_list(tables):
            command += f" -t {table}"

    log_filename = f"pg_dump_{current_time}.log"
    command += f" > {destination}/{log_filename} 2>&1"
    
    return command, filename_with_suffix, log_filename

def main():
    parser = argparse.ArgumentParser(description="Construct Docker pg_dump command")
    parser.add_argument("-v", "--destination", required=True, help="Destination volume")
    parser.add_argument("-H", "--host", required=True, help="Database host")
    parser.add_argument("-U", "--username", required=True, help="Database username")
    parser.add_argument("-d", "--database", required=True, help="Database name")
    parser.add_argument("-f", "--filename", required=True, help="Base dump filename")
    parser.add_argument("-n", "--schemas", help="Schema names (single or comma-separated)")
    parser.add_argument("-t", "--tables", help="Table names (single or comma-separated)")
    parser.add_argument("--port", default="5432", help="Database port (default: 5432)")
    parser.add_argument("--region", default="eu-west-2", help="AWS region (default: eu-west-2)")
    parser.add_argument("--run", action="store_true", help="Execute the generated command")

    try:
        args = parser.parse_args()

        # Verify host existence
        if not verify_host(args.host):
            logger.error(f"Unable to resolve host '{args.host}'. Please check the hostname and try again.")
            sys.exit(1)

        # Verify destination existence
        if not verify_destination(args.destination):
            logger.error(f"Destination directory '{args.destination}' does not exist or is not accessible. Please check the path and try again.")
            sys.exit(1)

        # Generate DB auth token
        password = generate_db_auth_token(args.host, args.username, args.port, args.region)

        # Verify schemas and tables
        if not verify_schemas_and_tables(args.host, args.port, args.database, args.username, password, args.schemas, args.tables):
            sys.exit(1)

        # Construct the command
        command, filename_with_suffix, log_filename = construct_docker_command(
            args.host,
            args.username,
            password,
            args.destination,
            args.database,
            args.filename,
            args.schemas,
            args.tables
        )

        if args.run:
            logger.info("Executing command...")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Command executed successfully.")
                logger.info(f"Backup saved as '{filename_with_suffix}' with log file at '{log_filename}'")
            else:
                logger.error("Command failed.")
                logger.error("Error: %s", result.stderr)
        else:
            logger.info("Command constructed successfully.")
            logger.info(command)

    except argparse.ArgumentError as e:
        logger.error(f"Argument error: {e}")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()