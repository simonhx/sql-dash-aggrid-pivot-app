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

    # Construct SQLAlchemy database URL
    db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = None
    session = None

    try:
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Query using the SQLAlchemy Film model, selecting specific columns
        query_result = session.query(
            Film.film_id,
            Film.title,
            Film.description,
            Film.release_year,
            Film.rental_rate
        ).order_by(Film.film_id).limit(20).all()

        if not query_result:
            rowData = [{"message": "No film data found."}]
            columnDefs = [{"field": "message"}]
            return rowData, columnDefs, "No film data found."
        
        # Format data for AG Grid
        rowData = [dict(row._mapping) for row in query_result]

        # Define columnDefs with pivot capabilities
        # Base properties like sortable, filter, resizable will be set in defaultColDef in app.py
        columnDefs = [
            {"field": "film_id"}, # Gets base properties from defaultColDef
            {"field": "title", "enableRowGroup": True, "enablePivot": True}, # Allow title to be grouped or pivoted
            {"field": "description"}, # Standard column
            {
                "field": "release_year",
                "enableRowGroup": True, # Allow this column to be used for row grouping
                "rowGroup": True,       # Group by release_year by default
                "filter": "agNumberColumnFilter", # Specify filter type for numeric data
            },
            {
                "field": "rental_rate",
                "enableValue": True,    # Allow this column for aggregation
                "aggFunc": "sum",       # Default aggregation function
                "allowedAggFuncs": ["sum", "avg", "min", "max", "count"], # Specify allowed aggregation functions
                "filter": "agNumberColumnFilter", # Specify filter type for numeric data
                # For currency, format the value. Ensure params.value is handled if it could be null/undefined.
                "valueFormatter": {"function": "params.value == null ? '' : '$' + Number(params.value).toFixed(2)"}
            }
        ]
        # Example: If you wanted to hide the original 'release_year' column after grouping:
        # columnDefs[3]["hide"] = True 

    except sqlalchemy.exc.SQLAlchemyError as e: # Catch SQLAlchemy specific errors
        print(f"Database Error (SQLAlchemy): {e}")
        error_message = f"Failed to connect to the database or execute query using SQLAlchemy: {e}"
        rowData = [{"error_message": str(e)}]
        columnDefs = [{"field": "error_message"}]
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        error_message = f"An unexpected error occurred: {e}"
        rowData = [{"error_message": str(e)}]
        columnDefs = [{"field": "error_message"}]
    finally:
        if session:
            session.close()
    return rowData, columnDefs, error_message