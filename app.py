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
        enableEnterpriseModules=True, # Enable AG Grid Enterprise features
        rowData=rowData,
        columnDefs=columnDefs,
        defaultColDef={
            "editable": False,      # Keep cells non-editable by default
            "sortable": True,       # Allow sorting on all columns
            "filter": True,         # Allow filtering on all columns
            "resizable": True,      # Allow columns to be resized
            "floatingFilter": True, # Enable floating filters for a better UX
        },
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": 10,
            "pivotMode": True,          # Enable pivot mode
            "groupDefaultExpanded": -1, # Expand all row groups by default
            "autoGroupColumnDef": {     # Configuration for the auto-generated group column
                "headerName": "Data Groups", # Custom header name for the group column
                "minWidth": 230,         # Give the group column a bit more space
                "cellRendererParams": {
                    "suppressCount": False, # Show the count of rows in each group
                    # "checkbox": True, # Example: if you want checkboxes for group selection
                },
            },
            "sideBar": {                # Configure the sidebar for pivot and column controls
                "toolPanels": [
                    {
                        "id": "columns",
                        "labelDefault": "Columns",
                        "labelKey": "columns",
                        "iconKey": "columns",
                        "toolPanel": "agColumnsToolPanel",
                        "toolPanelParams": { # Parameters for the columns tool panel
                            "suppressRowGroups": False,  # Show Row Groups section
                            "suppressValues": False,     # Show Values section (for aggregations)
                            "suppressPivots": False,     # Show Pivot Columns section
                            "suppressPivotMode": False,  # Show Pivot Mode selection
                        },
                    },
                ],
                "defaultToolPanel": "columns", # Open the 'Columns' tool panel by default
            },
        },
        style={"height": "600px", "width": "100%"} # Ensure the grid has dimensions
    )
])

# --- Run the App ---
if __name__ == "__main__":
    app.run(debug=True)