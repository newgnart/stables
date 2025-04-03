import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.database import engine


def inspect_postgres_tables():
    # Extract connection parameters
    conn_params = {
        "dbname": "postgres",  # Connect to postgres database
        "user": engine.url.username,
        "password": engine.url.password,
        "host": engine.url.host,
        "port": engine.url.port,
    }

    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Get all tables in the postgres database
        cur.execute(
            """
            SELECT table_schema, table_name, table_type
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            AND table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name;
        """
        )

        tables = cur.fetchall()

        if not tables:
            print("No user tables found in the postgres database.")
            return

        print("\nTables in postgres database:")
        print("---------------------------")
        for i, (schema, table, table_type) in enumerate(tables, 1):
            print(f"{i}. {schema}.{table}")

        # Ask which tables to drop
        table_nums = input(
            "\nEnter the numbers of tables you want to drop (comma-separated, or 'all'): "
        )

        if table_nums.lower() == "all":
            tables_to_drop = tables
        else:
            try:
                table_nums = [int(num.strip()) for num in table_nums.split(",")]
                tables_to_drop = [
                    tables[i - 1] for i in table_nums if 1 <= i <= len(tables)
                ]
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas.")
                return

        if not tables_to_drop:
            print("No tables selected to drop.")
            return

        print("\nTables to be dropped:")
        for schema, table, _ in tables_to_drop:
            print(f"- {schema}.{table}")

        # Ask for confirmation
        confirm = input("\nAre you sure you want to drop these tables? (yes/no): ")
        if confirm.lower() != "yes":
            print("Operation cancelled.")
            return

        # Drop each table
        for schema, table, _ in tables_to_drop:
            try:
                cur.execute(f'DROP TABLE IF EXISTS "{schema}"."{table}" CASCADE;')
                print(f"Successfully dropped table: {schema}.{table}")
            except Exception as e:
                print(f"Error dropping table {schema}.{table}: {str(e)}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {str(e)}")


def drop_unused_databases():
    # Extract connection parameters
    conn_params = {
        "dbname": "postgres",  # Connect to default database first
        "user": engine.url.username,
        "password": engine.url.password,
        "host": engine.url.host,
        "port": engine.url.port,
    }

    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Get all non-template databases
        cur.execute(
            """
            SELECT datname 
            FROM pg_database 
            WHERE datistemplate = false
            AND datname NOT IN ('postgres', 'stables')
            ORDER BY datname;
        """
        )

        databases_to_drop = cur.fetchall()

        if not databases_to_drop:
            print("No unused databases found to drop.")
            return

        print("Databases to be dropped:")
        for db in databases_to_drop:
            print(f"- {db[0]}")

        # Ask for confirmation
        confirm = input("\nAre you sure you want to drop these databases? (yes/no): ")
        if confirm.lower() != "yes":
            print("Operation cancelled.")
            return

        # Drop each database
        for db in databases_to_drop:
            db_name = db[0]
            try:
                # Terminate all connections to the database
                cur.execute(
                    f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{db_name}'
                    AND pid <> pg_backend_pid();
                """
                )

                # Drop the database
                cur.execute(f"DROP DATABASE IF EXISTS {db_name};")
                print(f"Successfully dropped database: {db_name}")
            except Exception as e:
                print(f"Error dropping database {db_name}: {str(e)}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    print("1. Drop unused databases")
    print("2. Inspect and drop tables in postgres database")
    choice = input("\nEnter your choice (1 or 2): ")

    if choice == "1":
        print("\nDropping unused databases...")
        drop_unused_databases()
    elif choice == "2":
        print("\nInspecting postgres database tables...")
        inspect_postgres_tables()
    else:
        print("Invalid choice. Please enter 1 or 2.")
