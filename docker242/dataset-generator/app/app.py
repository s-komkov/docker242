import psycopg2
import time
import os
import random
from psycopg2 import sql
from datetime import datetime
from setup_logging import *


MAX_ROWS = os.environ.get("MAX_ROWS", "300")
DATA_INSERTION_DELAY = os.environ.get("DATA_INSERTION_DELAY", "5")
try:
    MAX_ROWS = int(MAX_ROWS)
except Exception:
    logger.error(f"Variable 'MAX_ROWS' is not valid! Set default value 300")
    MAX_ROWS = 300
try:
    DATA_INSERTION_DELAY = int(DATA_INSERTION_DELAY)
except Exception:
    logger.error(f"Variable 'DATA_INSERTION_DELAY' is not valid! Set default value 5")
    DATA_INSERTION_DELAY = 5


def get_connection_params() -> dict:
    connection_parameters = {}
    connection_parameters["user"] = os.environ.get("POSTGRES_USER", "postgres")
    connection_parameters["password"] = os.environ.get("POSTGRES_PASSWORD", "postgres")
    connection_parameters["database"] = os.environ.get("POSTGRES_DB", "homework")
    connection_parameters["host"] = os.environ.get("POSTGRES_HOST", "127.0.0.1")
    connection_parameters["port"] = os.environ.get("POSTGRES_PORT", "5432")
    try:
        int(connection_parameters["port"])
    except Exception:
        logger.error(
            f"Port '{connection_parameters['port']}' is not valid! Set default port 5432"
        )
        connection_parameters["port"] = "5432"

    logger.info(f"Connection parameters are intialized {connection_parameters}")
    return connection_parameters


def get_connection(connection_params: dict):
    connection = psycopg2.connect(
        dbname=connection_params["database"],
        user=connection_params["user"],
        password=connection_params["password"],
        host=connection_params["host"],
        port=connection_params["port"],
    )
    cursor = connection.cursor()
    return (connection, cursor)


def check_database_existence(cursor, db_name: str):
    cursor.execute(
        "SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = lower(%s)",
        (db_name,),
    )
    if cursor.fetchone():
        return True
    return False


def check_table_existence(cursor, table_name: str):
    cursor.execute(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)",
        (table_name,),
    )
    if cursor.fetchone()[0]:
        return True
    return False


def print_table():
    first_print = False

    def _print_table(dataset: dict):
        nonlocal first_print
        if not first_print:
            first_print = True
            print("| {:^4} | {:^26} | {:^40} |".format("id", "timestamp", "record"))
            print("-" * 80)
        print(
            "| {:^4} | {:^26} | {:^40} |".format(
                dataset["id"], str(dataset["timestamp"]), dataset["record"]
            )
        )

    return _print_table


def create_database(cursor, db_name: str):
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))


def add_data_to_table(connection, cursor, dataset: dict):
    query = """UPDATE data SET timestamp=%(timestamp)s, record=%(record)s WHERE id=%(id)s;
               INSERT INTO data (id,timestamp, record)
                SELECT %(id)s, %(timestamp)s, %(record)s 
                WHERE NOT EXISTS (SELECT 1 FROM data WHERE id=%(id)s);"""
    cursor.execute(query, dataset)
    connection.commit()


def get_last_row_id(cursor) -> int:
    cursor.execute("SELECT COUNT(*) FROM data")
    row_count = cursor.fetchone()[0]
    if row_count > 0:
        cursor.execute("SELECT id FROM data ORDER BY timestamp DESC LIMIT 1")
        last_id = cursor.fetchone()[0]
    else:
        last_id = 1
    return last_id


def prepare_database(connection_params: dict) -> bool:
    logger.info(
        f"Connect to database 'postgres' {connection_params['host']}:{connection_params['port']} with user '{connection_params['user']}'"
    )
    _connection_params = dict(connection_params)
    _connection_params["database"] = "postgres"
    connection, cursor = get_connection(_connection_params)
    connection.autocommit = True
    logger.info(
        f"Checking the existence of a database '{connection_params['database']}'"
    )
    database_exists = check_database_existence(cursor, connection_params["database"])
    if database_exists:
        logger.info(f"Database '{connection_params['database']}' already exists")
    else:
        create_database(cursor, connection_params["database"])
        logger.info(f"Database '{connection_params['database']}' succesfully created")
    connection.close()
    return True


def prepare_table(connection_params: dict) -> bool:
    logger.info(
        f"Connect to database '{connection_params['database']}' {connection_params['host']}:{connection_params['port']} with user '{connection_params['user']}'"
    )
    connection, cursor = get_connection(connection_params)
    logger.info("Checking the existence of a table named 'data'")
    table_exists = check_table_existence(cursor, "data")
    if not table_exists:
        cursor.execute(
            """
            CREATE TABLE data (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                record VARCHAR(250))"""
        )
        connection.commit()
        logger.info("Table 'data' succesfully created")
    else:
        logger.info("Table 'data' already exists")
    return (True, connection)


def insert_data(connection, connection_params: dict, max_rows: int, time_delay: int):
    table_view = print_table()
    dataset = {}
    cursor = connection.cursor()
    try:
        last_id = get_last_row_id(cursor)
    except Exception as error:
        logger.error(f"Error fetching last id {error}")
        last_id = 1
    else:
        logger.info(f"Starting add values from id {last_id} \n")
    while True:
        try:
            dataset["timestamp"] = datetime.now()
            dataset["record"] = f"dataset {random.getrandbits(128):08x}"
            dataset["id"] = last_id
            add_data_to_table(connection, cursor, dataset)
            table_view(dataset)
        except psycopg2.InterfaceError as error:
            logger.error(f"Values insertion in table 'data' error: {error}")
            time.sleep(5)
            try:
                logger.info(f"Trying to create a new connection")
                connection.close()
                connection, cursor = get_connection(connection_params)
                table_view = print_table()
                logger.info(f"Connection successfull, return to normal operation \n")
            except Exception as error:
                logger.error(f"Error while opening new connection: {error}")
        except Exception as error:
            logger.error(f"Values insertion in table 'data' error: {error}")
            time.sleep(5)
        else:
            last_id += 1
            if last_id > max_rows:
                last_id = 1
            time.sleep(time_delay)


if __name__ == "__main__":
    connection_params = get_connection_params()
    database_ok = False
    table_ok = False

    while not database_ok:
        try:
            database_ok = prepare_database(connection_params)
        except Exception as error:
            logger.error(
                f"Database check error:{error} Waiting 5 seconds to try again..."
            )
            time.sleep(5)

    while not table_ok:
        try:
            table_ok, database_connection = prepare_table(connection_params)
        except Exception as error:
            logger.error(f"Table check error:{error} Waiting 5 seconds to try again...")
            time.sleep(5)
    try:
        insert_data(
            database_connection, connection_params, MAX_ROWS, DATA_INSERTION_DELAY
        )
    except KeyboardInterrupt:
        print("Interrupted. Closing connection")
        database_connection.close()
