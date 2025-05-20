import dash
from dash import html
import dash_ag_grid as dag
import psycopg2
import os # For environment variables (recommended for credentials)

# --- Database Connection Configuration ---
# IMPORTANT: Replace with your actual database credentials.
# For better security, consider using environment variables or a config file.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "dvdrental")
DB_USER = os.getenv("DB_USER", "postgres")  # E.g., 'postgres'
DB_PASS = os.getenv("DB_PASS", "gandhi")
DB_PORT = os.getenv("DB_PORT", "5432")

conn_string = f"host='{DB_HOST}' port='{DB_PORT}' dbname='{DB_NAME}' user='{DB_USER}' password='{DB_PASS}'"

rowData = []
columnDefs = []
error_message = None

try:
    # Connect to your postgres DB
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    # --- Simple SQL Query ---
    # Fetching a few details from the 'film' table
    query = "SELECT film_id, title, description, release_year, rental_rate FROM film ORDER BY film_id LIMIT 20;"
    cursor.execute(query)

    # Fetch column names from cursor.description
    colnames = [desc[0] for desc in cursor.description]

    # Fetch all rows from the query
    results = cursor.fetchall()

    # Convert query results to a list of dictionaries (rowData for AG Grid)
    rowData = [dict(zip(colnames, row)) for row in results]

    # Create column definitions for AG Grid
    columnDefs = [{"field": col, "sortable": True, "filter": True, "resizable": True} for col in colnames]

    cursor.close()
    conn.close()

except psycopg2.Error as e:
    print(f"Database Error: {e}")
    error_message = f"Failed to connect to the database or execute query: {e}"
    # Provide a fallback for the grid in case of error
    rowData = [{"error_message": str(e)}]
    columnDefs = [{"field": "error_message"}]
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    error_message = f"An unexpected error occurred: {e}"
    rowData = [{"error_message": str(e)}]
    columnDefs = [{"field": "error_message"}]

# --- Dash App Initialization ---
app = dash.Dash(__name__)

# --- App Layout ---
app.layout = html.Div([
    html.H1("DVD Rental - Film Data (AG Grid Enterprise)"),
    html.P("A simple app to display data from the dvdrental PostgreSQL database."),
    dag.AgGrid(
        id="dvd-rental-grid",
        rowData=rowData,
        columnDefs=columnDefs,
        defaultColDef={"editable": False}, # Default for all columns
        dashGridOptions={"pagination": True, "paginationPageSize": 10},
        style={"height": "600px", "width": "100%"} # Ensure the grid has dimensions
    )
])

# --- Run the App ---
if __name__ == "__main__":
    app.run(debug=True)