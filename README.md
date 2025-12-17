# Duolingo Analysis of Top Languages Learned (2020-2025)

**Written by:** Lily Gates

---
## Project Overview
This project analyzes public data from the **Duolingo Language Report (2020–2025)** to explore global trends in language learning. Using Python and Plotly, it visualizes which languages are most popular in different countries over time and highlights trends in language adoption.



## Data Sources
**Duolingo Language Report [2020–2025]: Public data** (`duolingo_language_report_2020_2025.xlsx`)
- **Overview Sheet:** Contains global summary metrics and key statistics.
- **Data by Country Sheet:** Contains detailed language popularity data for each country per year (columns: `pop1_2020`, `pop2_2020`, … `pop2_2025`).



## Features
**Data Cleaning & Preparation**
  - Converts wide-format country-language data into a tidy long-form dataframe.
  - Safely extracts year from column names for analysis.

**Interactive Visualizations (Plotly)**
1. **Line Chart / Multi-Line Plot**  
- Shows the number of countries teaching each language over time (2020–2025).  
2. **Stacked Area Chart**  
- Displays composition of languages per year and overall trends.  
3. **Overall Distribution Bar Chart**  
- Shows total number of countries teaching each language across all years.



## Dependencies

This project requires the following Python packages:

- **Python 3.10+** – Recommended version for compatibility.
- **[pandas](https://pandas.pydata.org/)** – For data manipulation and cleaning.
- **[plotly](https://plotly.com/python/)** – For interactive visualizations.
- **[openpyxl](https://openpyxl.readthedocs.io/)** – To read Excel files (`.xlsx` format).

You can install all dependencies using pip:

```
pip install pandas plotly openpyxl
```