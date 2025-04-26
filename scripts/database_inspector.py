import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from stables.core.database import engine


def drop_database():
    """Inspect databases and allow user to select which ones to drop."""
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
            SELECT datname, pg_size_pretty(pg_database_size(datname)) as size
            FROM pg_database 
            WHERE datistemplate = false
            AND datname NOT IN ('postgres')
            ORDER BY datname;
        """
        )

        available_databases = cur.fetchall()

        if not available_databases:
            print("No databases available to drop.")
            return

        print("\nAvailable databases:")
        print("-------------------")
        for i, (db_name, size) in enumerate(available_databases, 1):
            print(f"{i}. {db_name} (Size: {size})")

        while True:
            print("\nOptions:")
            print("1. Enter database numbers (e.g., '1,3,4')")
            print("2. Enter database names (e.g., 'db1,db2,db3')")
            print("3. Type 'all' to select all databases")
            print("4. Type 'q' to quit")

            choice = input("\nYour choice: ").strip().lower()

            if choice == "q":
                print("Operation cancelled.")
                return

            if choice == "all":
                databases_to_drop = [db[0] for db in available_databases]
                break

            if choice in ("1", "2"):
                db_input = input("\nEnter your selection: ").strip()

                if choice == "1":  # User entered numbers
                    try:
                        numbers = [int(n.strip()) for n in db_input.split(",")]
                        databases_to_drop = [
                            available_databases[i - 1][0]
                            for i in numbers
                            if 1 <= i <= len(available_databases)
                        ]
                    except ValueError:
                        print(
                            "Invalid input. Please enter numbers separated by commas."
                        )
                        continue
                else:  # User entered names
                    names = [name.strip() for name in db_input.split(",")]
                    databases_to_drop = [
                        name
                        for name in names
                        if any(name == db[0] for db in available_databases)
                    ]

                if not databases_to_drop:
                    print("No valid databases selected. Please try again.")
                    continue

                break

            print("Invalid choice. Please try again.")

        print("\nDatabases selected for deletion:")
        for db_name in databases_to_drop:
            size = next(size for name, size in available_databases if name == db_name)
            print(f"- {db_name} (Size: {size})")

        # Ask for confirmation with database names
        confirm = input(
            "\nType the database names to confirm deletion (comma-separated): "
        )
        confirmed_names = [name.strip() for name in confirm.split(",")]

        if set(confirmed_names) != set(databases_to_drop):
            print(
                "Confirmation failed. Database names don't match. Operation cancelled."
            )
            return

        # Drop each confirmed database
        for db_name in databases_to_drop:
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


# def inspect_postgres_database_tables():
#     """Inspect and manage tables in the postgres database."""
#     # Extract connection parameters
#     conn_params = {
#         "dbname": "postgres",  # Connect to postgres database
#         "user": engine.url.username,
#         "password": engine.url.password,
#         "host": engine.url.host,
#         "port": engine.url.port,
#     }

#     try:
#         # Connect to PostgreSQL server
#         conn = psycopg2.connect(**conn_params)
#         conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
#         cur = conn.cursor()

#         # Get all tables in the postgres database with additional info
#         cur.execute(
#             """
#             SELECT
#                 table_schema,
#                 table_name,
#                 pg_size_pretty(pg_total_relation_size(quote_ident(table_schema) || '.' || quote_ident(table_name))) as size,
#                 (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = t.table_schema AND table_name = t.table_name) as column_count
#             FROM information_schema.tables t
#             WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
#             AND table_type = 'BASE TABLE'
#             ORDER BY table_schema, table_name;
#             """
#         )

#         available_tables = cur.fetchall()

#         if not available_tables:
#             print("No user tables found in the postgres database.")
#             return

#         print("\nAvailable tables in postgres database:")
#         print("------------------------------------")
#         for i, (schema, table, size, col_count) in enumerate(available_tables, 1):
#             print(f"{i}. {schema}.{table} (Size: {size}, Columns: {col_count})")

#         while True:
#             print("\nOptions:")
#             print("1. Enter table numbers (e.g., '1,3,4')")
#             print("2. Enter table names (e.g., 'public.users,public.posts')")
#             print("3. Type 'all' to select all tables")
#             print("4. Type 'q' to quit")

#             choice = input("\nYour choice: ").strip().lower()

#             if choice == "q":
#                 print("Operation cancelled.")
#                 return

#             if choice == "all":
#                 tables_to_drop = [
#                     (schema, table) for schema, table, _, _ in available_tables
#                 ]
#                 break

#             if choice in ("1", "2"):
#                 table_input = input("\nEnter your selection: ").strip()

#                 if choice == "1":  # User entered numbers
#                     try:
#                         numbers = [int(n.strip()) for n in table_input.split(",")]
#                         tables_to_drop = [
#                             (available_tables[i - 1][0], available_tables[i - 1][1])
#                             for i in numbers
#                             if 1 <= i <= len(available_tables)
#                         ]
#                     except ValueError:
#                         print(
#                             "Invalid input. Please enter numbers separated by commas."
#                         )
#                         continue
#                 else:  # User entered schema.table names
#                     names = [name.strip() for name in table_input.split(",")]
#                     tables_to_drop = []
#                     for name in names:
#                         try:
#                             schema, table = name.split(".")
#                             if any(
#                                 s == schema and t == table
#                                 for s, t, _, _ in available_tables
#                             ):
#                                 tables_to_drop.append((schema, table))
#                         except ValueError:
#                             print(
#                                 f"Invalid table name format: {name}. Use 'schema.table' format."
#                             )
#                             continue

#                 if not tables_to_drop:
#                     print("No valid tables selected. Please try again.")
#                     continue

#                 break

#             print("Invalid choice. Please try again.")

#         print("\nTables selected for deletion:")
#         for schema, table in tables_to_drop:
#             size = next(
#                 size for s, t, size, _ in available_tables if s == schema and t == table
#             )
#             col_count = next(
#                 col_count
#                 for s, t, _, col_count in available_tables
#                 if s == schema and t == table
#             )
#             print(f"- {schema}.{table} (Size: {size}, Columns: {col_count})")

#         # Ask for confirmation with table names
#         print(
#             "\nTo confirm deletion, please type the full table names (schema.table) separated by commas"
#         )
#         print("Example: public.users,public.posts")
#         confirm = input("\nType the table names to confirm deletion: ")
#         confirmed_names = {name.strip() for name in confirm.split(",")}
#         tables_to_drop_names = {f"{schema}.{table}" for schema, table in tables_to_drop}

#         if confirmed_names != tables_to_drop_names:
#             print("Confirmation failed. Table names don't match. Operation cancelled.")
#             print("Expected:", ", ".join(sorted(tables_to_drop_names)))
#             print("Received:", ", ".join(sorted(confirmed_names)))
#             return

#         # Drop each confirmed table
#         for schema, table in tables_to_drop:
#             try:
#                 cur.execute(f'DROP TABLE IF EXISTS "{schema}"."{table}" CASCADE;')
#                 print(f"Successfully dropped table: {schema}.{table}")
#             except Exception as e:
#                 print(f"Error dropping table {schema}.{table}: {str(e)}")

#         cur.close()
#         conn.close()

#     except Exception as e:
#         print(f"Error: {str(e)}")


def drop_tables(database_name: str):
    """Drop tables in a specific database."""
    # Extract connection parameters
    conn_params = {
        "dbname": database_name,
        "user": engine.url.username,
        "password": engine.url.password,
        "host": engine.url.host,
        "port": engine.url.port,
    }

    try:
        # Connect to the specified database
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Get all tables in the database
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
            print(f"No user tables found in the {database_name} database.")
            return

        print(f"\nTables in {database_name} database:")
        print("-" * (20 + len(database_name)))
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


def list_databases():
    """List all available databases and let user choose one to inspect."""
    conn_params = {
        "dbname": "postgres",
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
            ORDER BY datname;
        """
        )

        databases = cur.fetchall()

        if not databases:
            print("No databases found.")
            return None

        print("\nAvailable databases:")
        print("-------------------")
        for i, db in enumerate(databases, 1):
            print(f"{i}. {db[0]}")

        # Ask user to choose a database
        while True:
            try:
                choice = input(
                    "\nEnter the number of the database to inspect (or 'q' to quit): "
                )
                if choice.lower() == "q":
                    return None

                choice = int(choice)
                if 1 <= choice <= len(databases):
                    selected_db = databases[choice - 1][0]
                    return selected_db
                else:
                    print("Invalid choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number or 'q' to quit.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def inspect_table_details(database_name: str):
    """Inspect detailed information about tables in a specific database."""
    conn_params = {
        "dbname": database_name,
        "user": engine.url.username,
        "password": engine.url.password,
        "host": engine.url.host,
        "port": engine.url.port,
    }

    try:
        # Connect to the specified database
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Get all tables with additional info
        cur.execute(
            """
            SELECT 
                table_schema,
                table_name,
                pg_size_pretty(pg_total_relation_size(quote_ident(table_schema) || '.' || quote_ident(table_name))) as size,
                (SELECT COUNT(*) FROM information_schema.columns 
                 WHERE table_schema = t.table_schema AND table_name = t.table_name) as column_count,
                obj_description((quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass::oid) as table_comment
            FROM information_schema.tables t
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            AND table_type = 'BASE TABLE'
            ORDER BY table_schema, table_name;
            """
        )

        available_tables = cur.fetchall()

        if not available_tables:
            print(f"No user tables found in the {database_name} database.")
            return

        print(f"\nAvailable tables in {database_name} database:")
        print("-" * (20 + len(database_name)))
        for i, (schema, table, size, col_count, comment) in enumerate(
            available_tables, 1
        ):
            comment_str = f" - {comment}" if comment else ""
            print(
                f"{i}. {schema}.{table} (Size: {size}, Columns: {col_count}){comment_str}"
            )

        while True:
            print("\nOptions:")
            print("1. Enter table number")
            print("2. Enter table name (e.g., 'public.users')")
            print("3. Type 'q' to quit")

            choice = input("\nYour choice: ").strip().lower()

            if choice == "q":
                print("Operation cancelled.")
                return

            if choice in ("1", "2"):
                table_input = input("\nEnter your selection: ").strip()
                selected_table = None

                if choice == "1":  # User entered number
                    try:
                        number = int(table_input)
                        if 1 <= number <= len(available_tables):
                            selected_table = available_tables[number - 1]
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                        continue
                else:  # User entered schema.table name
                    try:
                        schema, table = table_input.split(".")
                        selected_table = next(
                            (
                                t
                                for t in available_tables
                                if t[0] == schema and t[1] == table
                            ),
                            None,
                        )
                    except ValueError:
                        print("Invalid table name format. Use 'schema.table' format.")
                        continue

                if not selected_table:
                    print("Table not found. Please try again.")
                    continue

                schema, table = selected_table[0], selected_table[1]

                # Get column information
                cur.execute(
                    """
                    SELECT 
                        column_name,
                        data_type,
                        character_maximum_length,
                        column_default,
                        is_nullable,
                        col_description(
                            (quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass::oid,
                            ordinal_position
                        ) as column_comment
                    FROM information_schema.columns c
                    WHERE table_schema = %s
                    AND table_name = %s
                    ORDER BY ordinal_position;
                    """,
                    (schema, table),
                )
                columns = cur.fetchall()

                # Get constraint information
                cur.execute(
                    """
                    SELECT 
                        con.conname as constraint_name,
                        con.contype as constraint_type,
                        pg_get_constraintdef(con.oid) as definition
                    FROM pg_constraint con
                    JOIN pg_class rel ON rel.oid = con.conrelid
                    JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
                    WHERE nsp.nspname = %s
                    AND rel.relname = %s;
                    """,
                    (schema, table),
                )
                constraints = cur.fetchall()

                # Get index information
                cur.execute(
                    """
                    SELECT
                        i.relname as index_name,
                        am.amname as index_type,
                        pg_get_indexdef(i.oid) as index_definition,
                        pg_size_pretty(pg_relation_size(i.oid)) as index_size
                    FROM pg_index x
                    JOIN pg_class i ON i.oid = x.indexrelid
                    JOIN pg_class t ON t.oid = x.indrelid
                    JOIN pg_am am ON i.relam = am.oid
                    JOIN pg_namespace n ON n.oid = t.relnamespace
                    WHERE n.nspname = %s
                    AND t.relname = %s;
                    """,
                    (schema, table),
                )
                indexes = cur.fetchall()

                # Get row count estimate
                cur.execute(
                    """
                    SELECT reltuples::bigint as estimate
                    FROM pg_class
                    JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
                    WHERE nspname = %s
                    AND relname = %s;
                    """,
                    (schema, table),
                )
                row_count = cur.fetchone()[0]

                # Print table details
                print(f"\nTable: {schema}.{table}")
                print("=" * (len(schema) + len(table) + 7))
                print(f"Size: {selected_table[2]}")
                print(f"Estimated row count: {row_count:,}")
                if selected_table[4]:  # Table comment
                    print(f"Description: {selected_table[4]}")

                print("\nColumns:")
                print("-" * 80)
                for col in columns:
                    name, dtype, max_length, default, nullable, comment = col
                    length_str = f"({max_length})" if max_length else ""
                    nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                    default_str = f" DEFAULT {default}" if default else ""
                    comment_str = f" - {comment}" if comment else ""
                    print(
                        f"  {name}: {dtype}{length_str} {nullable_str}{default_str}{comment_str}"
                    )

                if constraints:
                    print("\nConstraints:")
                    print("-" * 80)
                    for con_name, con_type, definition in constraints:
                        type_map = {
                            "p": "PRIMARY KEY",
                            "f": "FOREIGN KEY",
                            "u": "UNIQUE",
                            "c": "CHECK",
                        }
                        con_type = type_map.get(con_type, con_type)
                        print(f"  {con_name} ({con_type}):")
                        print(f"    {definition}")

                if indexes:
                    print("\nIndexes:")
                    print("-" * 80)
                    for idx_name, idx_type, idx_def, idx_size in indexes:
                        print(f"  {idx_name} ({idx_type}, Size: {idx_size}):")
                        print(f"    {idx_def}")

                break

            print("Invalid choice. Please try again.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    print("1. Drop database")
    print("2. Drop tables in a specific database")
    print("3. View detailed table information")
    choice = input("\nEnter your choice (1, 2, or 3): ")

    if choice == "1":
        print("\nDropping databases...")
        drop_database()
    elif choice == "2":
        print("\nListing available databases...")
        selected_db = list_databases()
        if selected_db:
            print(f"\nDropping tables in {selected_db}...")
            drop_tables(selected_db)
    elif choice == "3":
        print("\nListing available databases...")
        selected_db = list_databases()
        if selected_db:
            print(f"\nInspecting tables in {selected_db}...")
            inspect_table_details(selected_db)
    else:
        print("Invalid choice. Please enter 1, 2, or 3")
