# Duolingo User Language Analysis
# Created: 12/17/2025
# Last Updated: 12/17/2025 

import pandas as pd
import os
import re
import plotly.express as px
from dash import Dash, dcc, html, Input, Output


# ------------------------------- #
# Helper Function for File Naming #
# ------------------------------- #

# Ensure snake_case and proper naming convention
def to_snake_case(s):
    """
    Convert a string to snake_case suitable for filenames:
    - lowercase
    - spaces and hyphens replaced with underscores
    - remove parentheses, slashes, colons, and other special characters
    - collapse multiple underscores
    """
    s = s.lower()                      # lowercase
    s = re.sub(r"[ /\\\-]", "_", s)    # replace space, /, \, - with _
    s = re.sub(r"[^a-z0-9_]", "", s)   # remove all non-alphanumeric and non-underscore chars
    s = re.sub(r"_+", "_", s)          # collapse multiple underscores
    s = s.strip("_")                    # remove leading/trailing underscores
    return s

# ------------------------------------- #
# Loading Duolingo Language Report Data
# ------------------------------------- #

# Load "Duolingo Language Report [2020-2025]: Public data"
file_path = "duolingo_language_report_2020_2025.xlsx"

# --- Overview Sheet --- #
overview_sheet = "Overview"
overview_sheet_df = pd.read_excel(file_path, sheet_name=overview_sheet, skiprows=0)

# --- Data by Country Sheet --- #
data_by_country_sheet = "Data by country"
data_by_country_df = pd.read_excel(file_path, sheet_name=data_by_country_sheet, skiprows=1)

# -------------------------------
# Inspect & Clean Columns
# -------------------------------
# Strip whitespace from all column names
data_by_country_df.columns = [str(c).strip() for c in data_by_country_df.columns]

# Rename first column to 'country'
data_by_country_df.rename(columns={data_by_country_df.columns[0]: 'country'}, inplace=True)

# Strip whitespace from country names
data_by_country_df['country'] = data_by_country_df['country'].astype(str).str.strip()

print(data_by_country_df['country'])

# -------------------------------
# Keep only language columns
# -------------------------------
language_cols = [col for col in data_by_country_df.columns if col.startswith('pop')]
data_by_country_df = data_by_country_df[['country'] + language_cols]

# -------------------------------
# Melt to long-form tidy data
# -------------------------------
long_df = data_by_country_df.melt(
    id_vars='country',
    value_vars=language_cols,
    var_name='pop_year',
    value_name='language'
).dropna(subset=['language'])

# Extract year safely
long_df['year'] = pd.to_numeric(long_df['pop_year'].str.extract(r'(\d{4})')[0], errors='coerce')
long_df = long_df.dropna(subset=['year'])
long_df['year'] = long_df['year'].astype(int)



# ==================================
# ======= DATA VIZUALIZATION =======
# ==================================

# --------------------------------------------------------
# LINE CHART
# Number of Countries Teaching Each Language Over Time
# --------------------------------------------------------
line_data = long_df.groupby(['year', 'language'])['country'].nunique().reset_index()

fig_line = px.line(
    line_data,
    x='year',
    y='country',
    color='language',
    markers=True,
    title='Number of Countries Teaching Each Language Over Time',
    labels={'country': 'Number of Countries', 'year': 'Year', 'language': 'Language'}
)
fig_line.update_layout(legend_title_text='Language')
fig_line.show()

# --------------------------------------------------------
# STACKED BAR GRAPH
# --------------------------------------------------------

# --- Extract rank and year ---
long_df['rank'] = long_df['pop_year'].str.extract(r'(pop[12])')
long_df['year'] = pd.to_numeric(long_df['pop_year'].str.extract(r'(\d{4})')[0], errors='coerce')
long_df = long_df.dropna(subset=['year'])
long_df['year'] = long_df['year'].astype(int)

# --- Determine top 5 languages ---
top_languages = (
    long_df.groupby('language')['country']
    .nunique()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

# Optional: force a custom order
custom_order = top_languages

# --- Filter for top 5 languages ---
filtered_df = long_df[long_df['language'].isin(top_languages)]

# --- Group data for stacked bar ---
bar_data = filtered_df.groupby(['year', 'language', 'rank'])['country'].nunique().reset_index()
bar_data.rename(columns={'country': 'num_countries'}, inplace=True)

# --- Horizontal stacked bar chart with improved titles ---
fig = px.bar(
    bar_data,
    y='language',
    x='num_countries',
    color='rank',
    facet_col='year',
    facet_col_wrap=3,
    orientation='h',
    category_orders={'language': custom_order},
    title='Top 5 Languages by Popularity Rank Across Countries (2020–2025)',
    labels={
        'num_countries': 'Number of Countries Teaching Language',
        'language': 'Language',
        'rank': 'Popularity Rank'
    },
    color_discrete_map={'pop1': 'steelblue', 'pop2': 'orange'}  # Optional: consistent colors
)

# Clean up facet titles to show just the year
for anno in fig.layout.annotations:
    anno.text = anno.text.split('=')[-1]

# Update layout for readability
fig.update_layout(
    legend_title_text='Popularity Rank',
    title_font_size=18,
    xaxis_title_font_size=14,
    yaxis_title_font_size=14
)

fig.show()
