import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
from dash.exceptions import PreventUpdate
import urllib.parse

# Load data
url = "https://raw.githubusercontent.com/jordancmh/nba-prediction/main/nba_player_stats.csv"
data = pd.read_csv(url)

# Remove PLAYER_ID and TEAM_ID columns
data = data.drop(columns=['PLAYER_ID', 'TEAM_ID'])

# Rename "Regular%20Season" to "Regular Season"
data['Season_type'] = data['Season_type'].replace('Regular%20Season', 'Regular Season')

# Extract unique years, season types, and players
years = data['Year'].unique()
season_types = data['Season_type'].unique()
players = data['PLAYER'].unique()

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define function to filter data based on year and season type
def filter_data(year, season_type):
    filtered_data = data[(data['Year'] == year) & (data['Season_type'] == season_type)]
    return filtered_data.drop(columns=['Year', 'Season_type'])

# Define function to get player stats
def get_player_stats(player_name):
    player_data = data[data['PLAYER'] == player_name]
    return player_data

# Layout for the overall stats page
overall_stats_layout = html.Div([
    html.H1("NBA Player Stats Dashboard"),
    
    html.Div([
        html.Div([
            html.Label("Select Year:"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in years],
                value=years[0],
                style={'width': '150px'}
            ),
        ], style={'display': 'inline-block', 'margin-right': '20px'}),
        
        html.Div([
            html.Label("Select Season Type:"),
            dcc.Dropdown(
                id='season-type-dropdown',
                options=[{'label': season_type, 'value': season_type} for season_type in season_types],
                value=season_types[0],
                style={'width': '150px'}
            ),
        ], style={'display': 'inline-block'}),
    ]),
    
    dash_table.DataTable(
        id='stats-table',
        columns=[
            {"name": i, "id": i, "presentation": "markdown"} if i == "PLAYER" else {"name": i, "id": i}
            for i in data.columns if i not in ['Year', 'Season_type']
        ],
        page_size=20,
        style_table={'overflowX': 'auto'},
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
        },
        markdown_options={"html": True}  # Allow HTML in markdown
    )
])

# Layout for individual player stats page
player_stats_layout = html.Div([
    html.H1(id='player-name-header'),
    html.Div([
        html.Label("Select Season Type:"),
        dcc.Dropdown(
            id='player-season-type-dropdown',
            options=[{'label': season_type, 'value': season_type} for season_type in season_types],
            value=season_types[0],
            style={'width': '150px'}
        ),
    ]),
    dash_table.DataTable(
        id='player-stats-table',
        columns=[{"name": i, "id": i} for i in data.columns if i not in ['PLAYER', 'Season_type']],
        style_table={'overflowX': 'auto'},
        style_cell_conditional=[
            {'if': {'column_id': 'Year'},
             'textAlign': 'left'},
        ],
        style_cell={
            'textAlign': 'center',
            'padding': '5px'
        }
    )
])

# App layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Combined callback to update overall stats table and add hyperlinks
@app.callback(
    Output('stats-table', 'data'),
    [Input('year-dropdown', 'value'),
     Input('season-type-dropdown', 'value')]
)
def update_table_with_links(selected_year, selected_season_type):
    filtered_data = filter_data(selected_year, selected_season_type)
    
    # Add hyperlinks to player names
    filtered_data['PLAYER'] = filtered_data['PLAYER'].apply(
        lambda x: f'<a href="/player/{urllib.parse.quote(x)}" target="_blank">{x}</a>'
    )
    
    return filtered_data.to_dict('records')

# Callback to update player stats table based on player and season type
@app.callback(
    [Output('player-stats-table', 'data'),
     Output('player-name-header', 'children')],
    [Input('url', 'pathname'),
     Input('player-season-type-dropdown', 'value')]
)
def update_player_stats(pathname, selected_season_type):
    if pathname.startswith('/player/'):
        player_name = urllib.parse.unquote(pathname.split('/')[-1])
        player_data = get_player_stats(player_name)
        filtered_data = player_data[player_data['Season_type'] == selected_season_type].drop(columns=['PLAYER', 'Season_type'])
        
        # Sort the data by Year in descending order
        filtered_data = filtered_data.sort_values('Year', ascending=False)
        
        return filtered_data.to_dict('records'), f"{player_name} Stats"
    raise PreventUpdate

# Callback to update page content based on URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/' or pathname == '/overall-stats':
        return overall_stats_layout
    elif pathname.startswith('/player/'):
        return player_stats_layout
    else:
        return '404 Page Not Found'

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
