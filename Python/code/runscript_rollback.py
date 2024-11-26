"""
     Bootstrap script to upgrade PSD pipeline to v-01-01..
     Autocommit is set to True as the actions cannot be run inside a transaction block
"""

import boto3
import os
import json
import pg8000
from pg8000.legacy import Connection

rds_endpoint = 'localhost'
rds_port = '5432'
rds_default_db = 'psddw'
sql_relative_base_directory = 'C:/Users/ashenoy/sqltestscripts'
log_file = "C:/Users/ashenoy/sqltestscripts/bootstrap-rollback-v-01-01.log"


# List all scripts to run in correct sequence
sql_scripts = [
    {
        "database" : "psddw",
        "script" : [
            # Run the scripts for the changes
            "/rollback-DA-990.sql"
        ]
    }
]


def connect_to_cds(rds_database) -> (Connection, str):
    """
         Connects to CDS PostgreSQL RDS
         NOTE: Connection set to Autocommit

         Keyword Arguments:
         database: database to connect to

         Returns:
         Connection object
    """
    rds_username='postgres'
    rds_password='poochu'
    print(f"Connecting to RDS host: {rds_endpoint}")
    rds_connection = None
    try:
        rds_connection = pg8000.connect(
            database=rds_database,
            user=rds_username,
            password=rds_password,
            host=rds_endpoint,
            port=rds_port,
            ssl_context=False
        )
        # Turn on autocommit
        rds_connection.autocommit = True

    except Exception as e:
        print("Database connection failed due to {}".format(e))
        raise e

    return rds_connection,rds_username


def execute_cds_query(db_connection, script) -> {}:
    """
         Executes sql statements in script files.

         Keyword Arguments:
         None

         Returns:
         dict -- dictionary containing the Glue options to use
    """

    print(f"Opening script: {script}")
    with open(script) as sql_file_obj:
        sql_query = sql_file_obj.read()
        # Following query used just to check SSL was used for connection
        #sql_query = (
        #                "select "
        #                "        session.client_addr"
        #                "        ,session.datname"
        #                "        ,session.usename"
        #                "        ,session.state"
        #                "        ,session.backend_start"
        #                "        ,session.backend_type"
        #                "        ,case when ssl_status.ssl then 'Yes' else 'No' end as ssl_in_use"
        #                "        ,ssl_status.version"
        #                "        ,ssl_status.cipher"
        #                "    from"
        #                "        pg_stat_activity session"
        #                "        left join pg_roles role"
        #                "            on role.oid = session.usesysid"
        #                "        left join pg_stat_ssl ssl_status"
        #                "            on ssl_status.pid = session.pid"
        #                "    where"
        #                "        session.client_addr = inet_client_addr()"
        #                "        and session.client_port = inet_client_port()"
        #)

    print(f"Executing SQL from script: {script}")
    query_status = None
    try:

        query_response = db_connection.run(sql_query)
        query_status = 'COMPLETED'

    except Exception as e:

        print("SQL execution failed due to {}".format(e))
        query_response = e
        query_status = 'FAILED'

    return {"script":script, "state":str(query_status),"response":str(query_response)}


# Open & truncate output log, create if not exists
log_file_flags = os.O_WRONLY | os.O_TRUNC | os.O_CREAT
opened_file = os.open(log_file, log_file_flags)
print(f'Log file opened: {log_file}')

sql_script_log = {}
sequence_no = 0
for sql_file_set in sql_scripts:

    cds_database = sql_file_set["database"]
    # Connect to CDS RDS
    cds_connection, cds_user = connect_to_cds(cds_database)

    for sql_file in sql_file_set["script"]:
        sequence_no += 1
        step = f'step-{sequence_no}'
        sql_script_log[step] = execute_cds_query(
            cds_connection,
            f'{sql_relative_base_directory}{sql_file}'
        )
        sql_script_log[step]['connected_database'] = cds_database
        sql_script_log[step]['connected_user'] = cds_user

    cds_connection.close()

os.write(opened_file, json.dumps(sql_script_log).encode(encoding='UTF-8'))

# Close the log
os.close(opened_file)