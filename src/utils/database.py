import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()
class DatabaseUtil:

    def __init__(self, db_config):
        self.db_config = db_config

        try:
            self.connection = psycopg2.connect(**db_config)
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")
            self.connection = None

    def schema_details(self, schema_name):
        schema_info_context = f"Database Schema: {schema_name}\n"

        connection = self.connection

        if connection is None:
            return "Database connection is not available."

        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s;
                """,
                (schema_name,),
            )

            tables_list = cursor.fetchall()

            for table in tables_list:
                table_name = table[0]
                schema_info_context += f"\nTable: {table_name}\n"

                # Adding Columns & Data Types
                cursor.execute(
                    """
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = %s
                      AND table_name = %s;
                    """,
                    (schema_name, table_name),
                )

                columns_list = cursor.fetchall()

                for column_name, data_type in columns_list:
                    schema_info_context += (
                        f"  Column: {column_name}, Data Type: {data_type}\n"
                    )

                # Adding Sample Data
                cursor.execute(
                    f'SELECT * FROM "{schema_name}"."{table_name}" LIMIT 5;'
                )

                sample_data = cursor.fetchall()

                schema_info_context += "  Sample Data:\n"

                for row in sample_data:
                    schema_info_context += f"    {row}\n"

        except psycopg2.Error as e:
            print(f"Error fetching schema details: {e}")
            schema_info_context = f"Error fetching schema details: {e}"

        finally:
            cursor.close()
            connection.close()

        return schema_info_context

    def execute_sql(self, query):
        connection = self.connection
        cursor = None

        if connection is None:
            return "Database connection is not available."

        try:
            cursor = connection.cursor()
            cursor.execute(query)
            if cursor.description is None:
                connection.commit()
                return "Query executed successfully."

            return str(cursor.fetchall())
        except psycopg2.Error as e:
            connection.rollback()
            print(f"Error executing query: {e}")
            return f"Database error: {e}"
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

def handler():
    db_config = {
        "host": os.environ["DB_HOST"],
        "port": os.environ.get("DB_PORT", "5432"),
        "database": os.environ["DB_DATABASE"],
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
    }

    schema_name = os.environ.get("DB_SCHEMA", "public")

    database_util = DatabaseUtil(db_config)

    result = database_util.schema_details(schema_name)

    print(result)

    return result


if __name__ == "__main__":
    handler()
