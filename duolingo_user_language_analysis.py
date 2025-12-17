# Duolingo User Language Analysis
# Created: 12/17/2025
# Last Updated: 12/17/2025 
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
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

# Melt to long format
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
# Build Dash App
# -------------------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Duolingo Top 10 Languages Dashboard", style={'textAlign': 'center'}),
    
    # ---------------- Line chart ----------------
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
    
    # ---------------- Stacked bar chart ----------------
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
    
    # Map ranks to pretty labels
    rank_map = {'pop1': 'Most Popular', 'pop2': 'Second Most Popular'}
    year_df['rank_pretty'] = year_df['rank'].map(rank_map)
    
    # If empty, show placeholder
    if year_df.empty:
        fig = px.bar(
            x=[0],
            y=['No data'],
            orientation='h',
            labels={'x': 'Number of Countries', 'y': 'Language'},
            title=f"No data available for {selected_year}"
        )
        return fig

    # Horizontal stacked bar chart
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

    # Hover info
    fig.update_traces(
        hovertemplate="<b>Language:</b> %{y}<br><b>Rank:</b> %{customdata[0]}<br><b>Number of Countries:</b> %{x}<extra></extra>",
        customdata=year_df[['rank_pretty']]
    )

    fig.update_layout(
        title=f"Top 10 Languages in {selected_year} (Most Popular vs Second Most Popular)",
        legend_title_text='Popularity Rank',
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

# -------------------------------
# Auto-launch browser
# -------------------------------
def open_browser(url):
    webbrowser.open_new(url)

if __name__ == "__main__":
    # Dynamic port
    port = 0
    server = make_server("127.0.0.1", port, app.server)
    actual_port = server.socket.getsockname()[1]
    
    # Open browser after 1 second
    Timer(1, lambda: open_browser(f"http://127.0.0.1:{actual_port}/")).start()
    
    # Start Dash server
    server.serve_forever()
