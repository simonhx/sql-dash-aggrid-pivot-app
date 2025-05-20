import os
import psycopg2 # DBAPI driver for PostgreSQL, used by SQLAlchemy via 'postgresql+psycopg2://' connection string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy.exc
from db_models import Film # Import the Film model from db_models.py

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
    Connects to the database and fetches film data.
    Returns:
        tuple: (list_of_data_dicts_or_None, error_message_string_or_None)
               Returns (list_of_dicts, None) on success.
               Returns ([], None) if no data is found (query successful).
               Returns (None, error_message_string) on failure.
    """
    if DB_PASS is None:
        error_message = f"Database password could not be loaded from '{DB_PASS_FILE}'. Please check the file."
        print(error_message)
        return None, error_message

    # Construct SQLAlchemy database URL
    db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = None
    session = None
    try:
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Query using the SQLAlchemy Film model
        query_result = session.query(
            Film.film_id,
            Film.title,
            Film.description,
            Film.release_year,
            Film.rental_rate
        ).order_by(Film.film_id).limit(20).all()
        
        if not query_result:
            return [], None # No data found, but not an error
        
        data = [dict(row._mapping) for row in query_result]
        return data, None

    except sqlalchemy.exc.SQLAlchemyError as e: # Catch SQLAlchemy specific errors
        print(f"Database Error (SQLAlchemy): {e}")
        return None, f"Failed to connect to the database or execute query using SQLAlchemy: {e}"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, f"An unexpected error occurred: {e}"
    finally:
        if session:
            session.close()