import os
import psycopg2

# --- Database Connection Configuration ---
# For better security, consider using environment variables or a more robust config management.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "dvdrental")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_PASS_FILE = "db_password.txt" # Assumes this file is in the same directory as the script being run (app.py)

def _load_password_from_file(filepath):
    """
    Tries to load a password directly from a file.
    Returns the password string if successful, or None otherwise.
    Internal helper function.
    """
    try:
        # This path is relative to the Current Working Directory (CWD),
        # which is typically where app.py is executed.
        with open(filepath, 'r') as f:
            password = f.read().strip()
            if password:
                return password
        print(f"Warning: Password file '{filepath}' is empty.")
        return None
    except FileNotFoundError:
        print(f"Info: Password file '{filepath}' not found. Ensure it exists in the application's root directory.")
        return None
    except Exception as e:
        print(f"Warning: Error reading password file '{filepath}': {e}.")
        return None

DB_PASS = _load_password_from_file(DB_PASS_FILE)

def fetch_dvd_rental_data():
    """
    Connects to the database, fetches film data, and prepares it for AG Grid.
    Returns:
        tuple: (rowData, columnDefs, error_message)
    """
    rowData = []
    columnDefs = []
    error_message = None

    if DB_PASS is None:
        error_message = f"Database password could not be loaded from '{DB_PASS_FILE}'. Please check the file."
        print(error_message)
        rowData = [{"error_message": error_message}]
        columnDefs = [{"field": "error_message"}]
        return rowData, columnDefs, error_message

    conn_string = f"host='{DB_HOST}' port='{DB_PORT}' dbname='{DB_NAME}' user='{DB_USER}' password='{DB_PASS}'"

    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        query = "SELECT film_id, title, description, release_year, rental_rate FROM film ORDER BY film_id LIMIT 20;"
        cursor.execute(query)
        colnames = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        rowData = [dict(zip(colnames, row)) for row in results]
        columnDefs = [{"field": col, "sortable": True, "filter": True, "resizable": True} for col in colnames]
        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"Database Error: {e}")
        error_message = f"Failed to connect to the database or execute query: {e}"
        rowData = [{"error_message": str(e)}]
        columnDefs = [{"field": "error_message"}]
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        error_message = f"An unexpected error occurred: {e}"
        rowData = [{"error_message": str(e)}]
        columnDefs = [{"field": "error_message"}]

    return rowData, columnDefs, error_message