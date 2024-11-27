import boto3
import pg8000
import os
from pg8000.legacy import Connection
import json


######## CONSTANTS ########
ENVIRONMENT_STACK = os.getenv('ENVIRONMENT_STACK').lower()
REGION_NAME = os.getenv('REGION_NAME').lower()
RDS_ENDPOINT = os.getenv('RDS_ENDPOINT').lower().format(stack=ENVIRONMENT_STACK)
RDS_DEFAULT_DB = os.getenv('RDS_DEFAULT_DB').lower().format(stack=ENVIRONMENT_STACK)
RDS_USERNAME = os.getenv('RDS_USERNAME').lower().format(stack=ENVIRONMENT_STACK)
RDS_PORT = os.getenv('RDS_PORT').lower()


def connect_to_cds(rds_database) -> (pg8000.legacy.Connection, str):
    """
    Connects to CDS PostgreSQL RDS
    NOTE: Connection set to Autocommit

    Keyword Arguments:
    database: database to connect to

    Returns:
    Connection object
    """

    # Open AWS session
    print(f"Opening AWS session for region: {REGION_NAME}")
    aws_session = boto3.Session(region_name=REGION_NAME)


    print(f"Creating RDS client & generating auth token")
    rds_client = aws_session.client('rds')
    rds_token = rds_client.generate_db_auth_token(
       DBHostname=RDS_ENDPOINT,
       Port=RDS_PORT,
       DBUsername=RDS_USERNAME,
       Region=REGION_NAME)
    print(rds_token)


    print(f"Connecting to RDS host: {RDS_ENDPOINT}")
    rds_connection = None
    try:
        rds_connection = pg8000.connect(
            database=RDS_DEFAULT_DB,
            user=RDS_USERNAME,
            password=rds_token,
            host=RDS_ENDPOINT,
            port=RDS_PORT,
            ssl_context=True
        )
        # Turn on autocommit
        rds_connection.autocommit = True

    except Exception as e:
        print("Database connection failed due to {}".format(e))
        raise e

    return rds_connection, RDS_USERNAME


def lambda_handler(event, context):
    """
    Lambda handler function
    """
    try:
        cds_connection, cds_user = connect_to_cds('opss_datapipe_prod_cds')
        # Perform any additional operations with the connection if needed
        print("Connected to the database:", cds_connection)
        print("Username:", cds_user)
        # Close the database connection when done
        cds_connection.close()
    except Exception as e:
        print("Error:", e)
        raise e
