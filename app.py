import dash
from dash import html
import dash_ag_grid as dag
from db_utils import fetch_dvd_rental_data # Import the new utility function

# --- Fetch Data using the utility function ---
# This single call now handles database connection, querying, and error handling.
rowData, columnDefs, error_message = fetch_dvd_rental_data()

# --- Dash App Initialization ---
app = dash.Dash(__name__)

# --- App Layout ---
app.layout = html.Div([
    html.H1("DVD Rental - Film Data (AG Grid Enterprise)"),
    html.P("A simple app to display data from the dvdrental PostgreSQL database."),
    # Optionally, display the error message directly in the UI
    html.Div(error_message, style={'color': 'red', 'padding': '10px'}) if error_message else html.Div(),
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