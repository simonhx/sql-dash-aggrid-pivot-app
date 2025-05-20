import dash
from dash import html
import dash_ag_grid as dag
from db_utils import fetch_dvd_rental_data # Import the new utility function

# --- Fetch Data ---
# fetch_dvd_rental_data() now returns (data_list_or_None, error_string_or_None)
fetched_data, db_error_message = fetch_dvd_rental_data()

# --- Initialize AG Grid properties and UI messages ---
grid_rowData = []
grid_columnDefs = []
ui_message = db_error_message # Message to display above the grid (can be error or info)

if db_error_message:
    # An error occurred during data fetching
    grid_rowData = [{"error": db_error_message}]
    grid_columnDefs = [{"field": "error", "headerName": "Error", "flex": 1}]
elif fetched_data is None or not fetched_data: # No DB error, but no data or data is None/empty
    no_data_message = "No film data found."
    grid_rowData = [{"message": no_data_message}]
    grid_columnDefs = [{"field": "message", "headerName": "Info", "flex": 1}]
    if not ui_message: # If there wasn't a DB error, set this info message for the UI
        ui_message = no_data_message
else:
    # Data successfully fetched
    grid_rowData = fetched_data
    # Define columnDefs for actual data here
    # Base properties like sortable, filter, resizable will be set in defaultColDef
    grid_columnDefs = [
        {"field": "film_id"},
        {"field": "title", "enableRowGroup": True, "enablePivot": True},
        {"field": "description"},
        {
            "field": "release_year",
            "enableRowGroup": True,
            "rowGroup": True,       # Group by release_year by default
            "filter": "agNumberColumnFilter",
        },
        {
            "field": "rental_rate",
            "enableValue": True,
            "aggFunc": "sum",
            "allowedAggFuncs": ["sum", "avg", "min", "max", "count"],
            "filter": "agNumberColumnFilter",
            "valueFormatter": {"function": "params.value == null ? '' : '$' + Number(params.value).toFixed(2)"}
        }
    ]

# --- Dash App Initialization ---
app = dash.Dash(__name__)

# --- App Layout ---
app.layout = html.Div([
    html.H1("DVD Rental - Film Data (AG Grid Enterprise)"),
    html.P("A simple app to display data from the dvdrental PostgreSQL database."),
    html.Div(ui_message, style={'color': 'red' if db_error_message else 'blue', 'padding': '10px'}) if ui_message else html.Div(),
    dag.AgGrid(
        id="dvd-rental-grid",
        enableEnterpriseModules=True, # Enable AG Grid Enterprise features
        rowData=grid_rowData,
        columnDefs=grid_columnDefs,
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