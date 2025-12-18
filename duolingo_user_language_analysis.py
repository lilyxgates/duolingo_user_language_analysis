# Duolingo User Language Analysis
# Created: 12/17/2025
# Last Updated: 12/17/2025 

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table
from threading import Timer
from werkzeug.serving import make_server
import webbrowser

# -------------------------------
# Load & Prepare Data
# -------------------------------
file_path = "duolingo_language_report_2020_2025.xlsx"
data_by_country_df = pd.read_excel(file_path, sheet_name="Data by country", skiprows=1)

# Clean columns
data_by_country_df.columns = [str(c).strip() for c in data_by_country_df.columns]
data_by_country_df.rename(columns={data_by_country_df.columns[0]: 'country'}, inplace=True)
data_by_country_df['country'] = data_by_country_df['country'].astype(str).str.strip()

# Keep only language columns (pop1/pop2)
language_cols = [col for col in data_by_country_df.columns if col.startswith('pop')]
data_by_country_df = data_by_country_df[['country'] + language_cols]

# Melt to long format for charts
long_df = data_by_country_df.melt(
    id_vars='country',
    value_vars=language_cols,
    var_name='pop_year',
    value_name='language'
).dropna(subset=['language'])

# Extract rank and year
long_df['rank'] = long_df['pop_year'].str.extract(r'(pop[12])')
long_df['year'] = pd.to_numeric(long_df['pop_year'].str.extract(r'(\d{4})')[0], errors='coerce')
long_df = long_df.dropna(subset=['year'])
long_df['year'] = long_df['year'].astype(int)

# -------------------------------
# Determine top 10 languages
# -------------------------------
top_languages = (
    long_df.groupby('language')['country']
    .nunique()
    .sort_values(ascending=False)
    .head(10)
    .index.tolist()
)
filtered_df = long_df[long_df['language'].isin(top_languages)]

# -------------------------------
# Prepare line chart data
# -------------------------------
line_data = filtered_df.groupby(['year', 'language'])['country'].nunique().reset_index()
line_data.rename(columns={'country': 'num_countries'}, inplace=True)

# -------------------------------
# Prepare stacked bar chart data
# -------------------------------
bar_data = filtered_df.groupby(['year', 'language', 'rank'])['country'].nunique().reset_index()
bar_data.rename(columns={'country': 'num_countries'}, inplace=True)

# -------------------------------
# Prepare table data (Top 2 Languages per Country per Year)
# -------------------------------
table_df = data_by_country_df.copy()
pretty_col_map = {}
for col in table_df.columns:
    if col.startswith('pop1'):
        year = col[-4:]
        pretty_col_map[col] = f"Most Popular {year}"
    elif col.startswith('pop2'):
        year = col[-4:]
        pretty_col_map[col] = f"Second Most Popular {year}"
    else:
        pretty_col_map[col] = col
table_df.rename(columns=pretty_col_map, inplace=True)

# -------------------------------
# Build Dash App
# -------------------------------
app = Dash(__name__)

country_options = [{'label': c, 'value': c} for c in sorted(table_df['country'].unique())]

app.layout = html.Div([
    html.H1("Duolingo Top Languages Dashboard", style={'textAlign': 'center'}),
    
    # ---------------- Line Chart ----------------
    html.H2("Language Trends Over Time"),
    dcc.Graph(
        id='line-chart',
        figure=px.line(
            line_data,
            x='year',
            y='num_countries',
            color='language',
            markers=True,
            labels={'num_countries': 'Number of Countries', 'year': 'Year', 'language': 'Language'},
            title='Number of Countries Teaching Top 10 Languages Over Time'
        ).update_layout(legend_title_text='Language')
    ),
    
    # ---------------- Stacked Bar Chart ----------------
    html.H2("Top 10 Languages by Year"),
    html.Label("Select Year:"),
    dcc.Slider(
        id='year-slider',
        min=int(bar_data['year'].min()),
        max=int(bar_data['year'].max()),
        step=1,
        value=int(bar_data['year'].min()),
        marks={int(y): str(int(y)) for y in sorted(bar_data['year'].unique())},
        tooltip={"placement": "bottom", "always_visible": True}
    ),
    dcc.Graph(id='stacked-bar-graph'),
    
    # ---------------- Interactive Table ----------------
    html.H2("Top 2 Languages per Country"),
    html.Label("Select Countries:"),
    dcc.Dropdown(
        id='country-selector',
        options=country_options,
        multi=True,
        value=[],
        placeholder="Select one or more countries..."
    ),
    dash_table.DataTable(
        id='top2-table',
        columns=[{"name": col, "id": col} for col in table_df.columns],
        data=table_df.to_dict('records'),
        style_table={'overflowX': 'auto', 'marginTop': '20px'},
        style_cell={'textAlign': 'center', 'padding': '5px'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
        page_size=15,
        sort_action='native',
        filter_action='native',
        # Highlight "Most Popular" cells
        style_data_conditional=[
            {
                'if': {
                    'filter_query': f'{{{col}}} = "Most Popular {col[-4:]}"',
                    'column_id': col
                },
                'backgroundColor': 'lightgreen',
                'fontWeight': 'bold'
            } for col in table_df.columns if col != 'country'
        ]
    ),
    
    # ---------------- Footer ----------------
    html.Div(
        [
            "Data source: ",
            html.A(
                "Duolingo Language Report (2020-2025)",
                href="https://docs.google.com/spreadsheets/d/1CndYC5ZovYfmPuMN9T9Jxfa4CQXOzZrfQ2kAUaWG1ZU/edit?ref=blog.duolingo.com&gid=532174835#gid=532174835",
                target="_blank",
                style={"textDecoration": "underline", "color": "blue"}
            )
        ],
        style={"textAlign": "center", "fontSize": 12, "marginTop": 20, "color": "gray"}
    )
])

# -------------------------------
# Callback for stacked bar chart
# -------------------------------
@app.callback(
    Output('stacked-bar-graph', 'figure'),
    Input('year-slider', 'value')
)
def update_bar(selected_year):
    selected_year = int(selected_year)
    year_df = bar_data[bar_data['year'] == selected_year].copy()
    rank_map = {'pop1': 'Most Popular', 'pop2': 'Second Most Popular'}
    year_df['rank_pretty'] = year_df['rank'].map(rank_map)
    
    if year_df.empty:
        fig = px.bar(
            x=[0], y=['No data'], orientation='h',
            labels={'x': 'Number of Countries', 'y': 'Language'},
            title=f"No data available for {selected_year}"
        )
        return fig

    fig = px.bar(
        year_df,
        y='language',
        x='num_countries',
        color='rank_pretty',
        orientation='h',
        category_orders={'language': top_languages},
        color_discrete_map={'Most Popular': 'steelblue', 'Second Most Popular': 'orange'},
        labels={'num_countries': 'Number of Countries Teaching Language',
                'language': 'Language',
                'rank_pretty': 'Popularity Rank'}
    )
    fig.update_layout(
        title=f"Top 10 Languages in {selected_year} (Most Popular vs Second Most Popular)",
        legend_title_text='Popularity Rank',
        yaxis={'categoryorder': 'total ascending'}
    )
    return fig

# -------------------------------
# Callback for table filtering
# -------------------------------
@app.callback(
    Output('top2-table', 'data'),
    Input('country-selector', 'value')
)
def update_table(selected_countries):
    if not selected_countries:
        filtered = table_df
    else:
        filtered = table_df[table_df['country'].isin(selected_countries)]
    return filtered.to_dict('records')

# -------------------------------
# Auto-launch browser
# -------------------------------
def open_browser(url):
    webbrowser.open_new(url)

if __name__ == "__main__":
    port = 0
    server = make_server("127.0.0.1", port, app.server)
    actual_port = server.socket.getsockname()[1]
    Timer(1, lambda: open_browser(f"http://127.0.0.1:{actual_port}/")).start()
    server.serve_forever()


"""
TODO: 
- Increase bar graph to include top 20 instead of top 10
- CSS better font consistency
- CSS border padding
- 2023 bar colors are switched
"""