from sqlalchemy import inspect, create_engine, text
from app.database import engine
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import platform
import socket


def inspect_database():
    # Get database URL from engine
    db_url = str(engine.url)

    # Extract connection parameters
    conn_params = {
        "dbname": "postgres",  # Connect to default database first
        "user": engine.url.username,
        "password": engine.url.password,
        "host": engine.url.host,
        "port": engine.url.port,
    }

    try:
        # Print system information
        print("\nSystem Information:")
        print("------------------")
        print(f"Hostname: {socket.gethostname()}")
        print(f"OS: {platform.system()} {platform.release()}")
        print(f"Python Version: {platform.python_version()}")

        # Print PostgreSQL server information
        print("\nPostgreSQL Server Information:")
        print("----------------------------")
        print(f"Host: {conn_params['host']}")
        print(f"Port: {conn_params['port']}")
        print(f"User: {conn_params['user']}")

        # Connect to PostgreSQL server
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Get PostgreSQL version
        cur.execute("SELECT version();")
        print(f"PostgreSQL Version: {cur.fetchone()[0]}")

        # Get all databases
        cur.execute(
            """
            SELECT datname, pg_size_pretty(pg_database_size(datname)) as size
            FROM pg_database 
            WHERE datistemplate = false
            ORDER BY datname;
        """
        )

        print("\nAvailable Databases:")
        print("-------------------")
        for db in cur.fetchall():
            print(f"- {db[0]} (Size: {db[1]})")

        # Get current database tables
        print("\nCurrent Database Tables:")
        print("----------------------")
        inspector = inspect(engine)
        for table_name in inspector.get_table_names():
            print(f"\nTable: {table_name}")
            print("Columns:")
            for column in inspector.get_columns(table_name):
                print(f"  - {column['name']}: {column['type']}")

            print("\nIndexes:")
            for index in inspector.get_indexes(table_name):
                print(f"  - {index['name']}: {index['column_names']}")

        # Get database statistics
        print("\nDatabase Statistics:")
        print("------------------")
        cur.execute(
            """
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) as total_size,
                pg_size_pretty(pg_relation_size(schemaname || '.' || tablename)) as table_size,
                pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename) - pg_relation_size(schemaname || '.' || tablename)) as index_size
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC;
        """
        )

        print("\nTable Sizes:")
        for table in cur.fetchall():
            print(
                f"- {table[1]}: Total={table[2]}, Table={table[3]}, Indexes={table[4]}"
            )

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    print("Inspecting PostgreSQL server and databases...")
    inspect_database()
