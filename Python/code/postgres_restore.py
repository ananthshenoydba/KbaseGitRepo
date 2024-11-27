"""
    Script to restore the dump of the database/schema/tables taken using postgres_dump.py
    usage: postgres_restore.py [-h] -v DESTINATION -f FILENAME -H HOST -U USERNAME [-d DATABASE] [--port PORT] [--region REGION] [-n SCHEMAS] [--clean] [--run]
    The parameters -v, -H, -U, -f are definetely needed. 
    -d if not specified a new database is created called unit_test_YYYYDDMM
    example
    python postgres_restore.py -v /home/cloudshell-user/testbackup -H "sample-dbhost.amazon.com" -U cds_dev_owner_role -f fulldb_291024_1556.dump
    If the command is run as above it just constructs the command it will run and print it. If its run with the --run option it executes and restores the backup dump.

"""

import argparse
import os
import socket
import subprocess
import sys
import logging
from datetime import datetime
import psycopg

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_host(host):
    try:
        socket.gethostbyname(host)
        return True
    except socket.gaierror:
        return False

def verify_file(filename, destination):
    filepath = os.path.join(destination, filename)
    return os.path.isfile(filepath)

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

def create_database_if_missing(host, port, username, region):
    db_name = f"unit_test_{datetime.now().strftime('%Y%m%d')}"
    token = generate_db_auth_token(host, "cds_dbcreator_role", port, region)
    
    try:
        conn = psycopg.connect(
            host=host,
            port=port,
            dbname="postgres",
            user="cds_dbcreator_role",
            password=token
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        cursor.execute("select 1 from pg_database where datname = %s", (db_name,))
        if cursor.fetchone() is None:
            cursor.execute(f"create database {db_name}")
            logger.info(f"Database '{db_name}' created successfully.")
        else:
            logger.info(f"Database '{db_name}' already exists.")

        return db_name
    except psycopg.Error as e:
        logger.error(f"Error creating the database: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

def construct_restore_command(host, username, password, destination, filename, database, schemas=None, clean=False):
    command = f"""docker run --rm \
    -v {destination}:/tmp \
    -e PGPASSWORD="{password}" \
    postgres:16 \
    pg_restore -h {host} -U {username} -d {database} -F c /tmp/{filename} -v"""
    
    if clean:
        command += " --clean"

    if schemas:
        for schema in parse_list(schemas):
            command += f" -n {schema}"

    log_filename = f"pg_restore_{datetime.now().strftime('%d%m%y_%H%M')}.log"
    command += f" > {destination}/{log_filename} 2>&1"
    
    return command, log_filename

def main():
    parser = argparse.ArgumentParser(description="Construct Docker pg_restore command")
    parser.add_argument("-v", "--destination", required=True, help="Destination volume")
    parser.add_argument("-f", "--filename", required=True, help="Dump file to restore")
    parser.add_argument("-H", "--host", required=True, help="Database host")
    parser.add_argument("-U", "--username", required=True, help="Database username")
    parser.add_argument("-d", "--database", help="Database name (if not provided, will create a new one)")
    parser.add_argument("--port", default="5432", help="Database port (default: 5432)")
    parser.add_argument("--region", default="eu-west-2", help="AWS region (default: eu-west-2)")
    parser.add_argument("-n", "--schemas", help="Schema names to restore (single or comma-separated)")
    parser.add_argument("--clean", action="store_true", help="Drop database objects before recreating them")
    parser.add_argument("--run", action="store_true", help="Execute the generated command")

    try:
        args = parser.parse_args()

        # Verify host existence
        if not verify_host(args.host):
            logger.error(f"Unable to resolve host '{args.host}'. Please check the hostname and try again.")
            sys.exit(1)

        # Verify destination directory and file
        if not verify_file(args.filename, args.destination):
            logger.error(f"File '{args.filename}' does not exist in '{args.destination}'")
            sys.exit(1)

        # If no database provided, create one with dbcreator
        if not args.database:
            logger.info("No database specified. Creating a new database...")
            args.database = create_database_if_missing(args.host, args.port, "cds_dbcreator_role", args.region)
            args.username = "cds_dbcreator_role"

        # Generate DB auth token for restore operation
        password = generate_db_auth_token(args.host, args.username, args.port, args.region)

        # Construct restore command
        command, log_filename = construct_restore_command(
            args.host,
            args.username,
            password,
            args.destination,
            args.filename,
            args.database,
            args.schemas,
            args.clean
        )

        log_filepath = os.path.join(args.destination, log_filename)
        if args.run:
            logger.info("Executing command...")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Command executed successfully.")
                logger.info(f"Restore log file: '{log_filepath}'")
            else:
                logger.error("Command failed.")
                logger.error("Error: %s", result.stderr)
                logger.info(f"Restore log file: '{log_filepath}'")
        else:
            logger.info("Command constructed successfully.")
            logger.info(f"Log file will be generated at: '{log_filepath}'")
            logger.info(command)

    except argparse.ArgumentError as e:
        logger.error(f"Argument error: {e}")
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()