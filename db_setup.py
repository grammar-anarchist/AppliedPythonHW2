import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

SUPERUSER_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'port': '5432'
}

DB_NAME = 'calories_db'

def create_database_and_user():
    try:
        connection = psycopg2.connect(**SUPERUSER_CONFIG)
        connection.autocommit = True
        cursor = connection.cursor()

        confirmation = input(
            f"WARNING: This will delete the existing database '{DB_NAME}' and recreate it. Type 'YES' to confirm: "
        )
        if confirmation != 'YES':
            print("Operation cancelled.")
            return

        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
        print(f"Database '{DB_NAME}' dropped successfully (if it existed).")

        cursor.execute(f"CREATE DATABASE {DB_NAME};")
        print(f"Database '{DB_NAME}' created successfully.")

        cursor.execute(f"""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT FROM pg_catalog.pg_roles WHERE rolname = 'calorie_user'
            ) THEN
                CREATE USER calorie_user WITH PASSWORD 'calorie_pass';
            END IF;
        END $$;
        GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO calorie_user;
        """)
        print("User 'calorie_user' created and granted privileges.")

    except psycopg2.Error as e:
        print(f"Error occurred: {e}")
    finally:
        cursor.close()
        connection.close()

def create_table():
    table_schema = """
    CREATE TABLE users (
        user_id PRIMARY KEY,
        weight INTEGER NOT NULL,
        height INTEGER NOT NULL,
        age INTEGER NOT NULL,
        activity INTEGER NOT NULL,
        city TEXT NOT NULL,
        water_goal INTEGER NOT NULL,
        calorie_goal INTEGER NOT NULL,
        logged_water INTEGER NOT NULL DEFAULT 0,
        logged_calories INTEGER NOT NULL DEFAULT 0,
        burned_calories INTEGER NOT NULL DEFAULT 0,
        last_logged TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=SUPERUSER_CONFIG['user'],
            password=SUPERUSER_CONFIG['password'],
            host=SUPERUSER_CONFIG['host'],
            port=SUPERUSER_CONFIG['port']
        )
        connection.autocommit = True
        cursor = connection.cursor()

        cursor.execute(table_schema)
        print("Table 'users' created successfully.")

    except psycopg2.Error as e:
        print(f"Error occurred: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    create_database_and_user()
    create_table()
