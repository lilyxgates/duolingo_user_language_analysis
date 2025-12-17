# Duolingo Analysis of Top Languages Learned (2020-2025)

**Author:** Lily Gates  
**Data Source:** [Duolingo Language Report (2020–2025)](https://docs.google.com/spreadsheets/d/1CndYC5ZovYfmPuMN9T9Jxfa4CQXOzZrfQ2kAUaWG1ZU/edit?ref=blog.duolingo.com&gid=532174835#gid=532174835)  

---

## Project Overview
This project analyzes public data from the **Duolingo Language Report (2020–2025)** to explore global trends in language learning. Using Python and Plotly, it visualizes which languages are most popular in different countries over time and highlights patterns in language adoption.


## Data Sources
**Duolingo Language Report [2020–2025]: Public data** (`duolingo_language_report_2020_2025.xlsx`)  

- **Overview Sheet:** Contains global summary metrics and key statistics.  
- **Data by Country Sheet:** Detailed language popularity data per country and per year (columns: `pop1_2020`, `pop2_2020`, … `pop2_2025`).


## Features

### Data Cleaning & Preparation
- Converts wide-format country-language data into a tidy long-form dataframe.  
- Safely extracts the year from column names for consistent analysis.  
- Filters top languages for visualization clarity.

### Interactive Visualizations (Plotly / Dash)
1. **Line Chart / Multi-Line Plot**  
   - Shows the number of countries teaching each language over time (2020–2025).  
2. **Horizontal Stacked Bar Chart**  
   - Displays the top languages per year with “Most Popular” and “Second Most Popular” ranks.  
   - Interactive slider allows filtering by year.  
3. **Overall Distribution Bar Chart**  
   - Shows total number of countries teaching each language across all years.  



## Dependencies

This project requires the following Python packages:

- **Python 3.10+** – Recommended version for compatibility.  
- **[pandas](https://pandas.pydata.org/)** – For data manipulation and cleaning.  
- **[plotly](https://plotly.com/python/)** – For interactive visualizations.  
- **[openpyxl](https://openpyxl.readthedocs.io/)** – To read Excel files (`.xlsx` format).  
- **[dash](https://dash.plotly.com/)** – For building interactive dashboards.  

You can install all dependencies using pip:

```
pip install pandas plotly openpyxl dash
```

## Usage
1. **Clone the repository:**  
```
git clone <repo_url>
cd duolingo_user_language_analysis
```
2. **Add the Excel data file:**
* Ensure the file `duolingo_language_report_2020_2025.xlsx` is placed in the project folder.

3. **Install dependencies** (if not already installed):
`pip install pandas plotly openpyxl dash`

4. **Run the Dash app:**
```
python duolingo_user_language_analysis.py
```

5. **View the dashboard:**
* The dashboard will automatically open in your default web browser.
* Use the slider to filter by year and explore the top languages per country.