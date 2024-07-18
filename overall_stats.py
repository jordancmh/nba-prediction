import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd

# Load data
# url = "https://raw.githubusercontent.com/jordancmh/nba-prediction/main/nba_player_stats.csv"
data = pd.read_csv("csv files/nba_player_stats.csv")

# Remove PLAYER_ID and TEAM_ID columns
data = data.drop(columns=['PLAYER_ID', 'TEAM_ID'])

# Rename "Regular%20Season" to "Regular Season"
data['Season_type'] = data['Season_type'].replace('Regular%20Season', 'Regular Season')

# Extract unique years and season types
years = data['Year'].unique()
season_types = data['Season_type'].unique()

# Define function to filter data based on year and season type
def filter_data(year, season_type):
    filtered_data = data[(data['Year'] == year) & (data['Season_type'] == season_type)]
    return filtered_data.drop(columns=['Year', 'Season_type'])

# Initialize Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("NBA Player Stats Dashboard"),
    
    html.Div([
        html.Div([
            html.Label("Season"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in years],
                value=years[0],
                style={'width': '300px'}
            ),
        ], style={'display': 'inline-block', 'margin-right': '20px'}),
        
        html.Div([
            html.Label("Season Type"),
            dcc.Dropdown(
                id='season-type-dropdown',
                options=[{'label': season_type, 'value': season_type} for season_type in season_types],
                value=season_types[0],
                style={'width': '300px'}
            ),
        ], style={'display': 'inline-block'}),
    ]),
    
    dash_table.DataTable(
        id='stats-table',
        columns=[{"name": i, "id": i} for i in data.columns if i not in ['Year', 'Season_type']],
        page_size=20,
        style_table={'overflowX': 'auto', 'margin-top': '20px'},
        style_cell_conditional=[
            {'if': {'column_id': 'PLAYER'},
             'textAlign': 'left'},
            {'if': {'column_id': 'Year'},
             'display': 'none'},
            {'if': {'column_id': 'Season_type'},
             'display': 'none'}
        ],
        style_cell={
            'textAlign': 'center',
            'padding': '5px'
        }
    )
])

# Callback to update table based on dropdown selections
@app.callback(
    Output('stats-table', 'data'),
    [Input('year-dropdown', 'value'),
     Input('season-type-dropdown', 'value')]
)
def update_table(selected_year, selected_season_type):
    filtered_data = filter_data(selected_year, selected_season_type)
    return filtered_data.to_dict('records')

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
