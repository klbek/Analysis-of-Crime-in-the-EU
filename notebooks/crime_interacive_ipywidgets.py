import ipywidgets as widgets
from IPython.display import display, HTML
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from eurostatlib.crimetable import EurostatCrimeTable

crime_table = EurostatCrimeTable()

geo_df = pd.read_csv(f'../data/geo.csv')
iccs_df = pd.read_csv(f'../data/iccs.csv')

crime_table.load_data(f'../data/estat_crim_off_cat.tsv', geo_df, iccs_df)


country = widgets.Dropdown(
    options=crime_table.country_list_sorted,
    value=crime_table.country_list_sorted[0],
    description='Country:',
    disabled=False,
)

crime = widgets.Dropdown(
    options=crime_table.crime_list_sorted,
    value=crime_table.crime_list_sorted[0],
    description='Crime:',
    disabled=False,
)


output = widgets.Output()


def update_output(*args):
    with output:
        output.clear_output()

        select_country = country.value
        select_crime = crime.value

        crime_table.filter_data(select_country, select_crime)

        crime_dict_info = crime_table.statistics.statistics_dictionary
        text = f"""
        <h2>Graph information:</h2>
        <p><b>Country:</b> {select_country}</p>
        <p><b>Crime:</b> {select_crime}</p>
        <p>{crime_table.statistics_info}</p>
        <p><b>The data is expressed as the number of cases per one hundred thousand inhabitants</b></p>
        <p><b>min value:</b> {crime_dict_info['min_value']} ({crime_dict_info['min_value_year']})</p>
        <p><b>max value:</b> {crime_dict_info['max_value']} ({crime_dict_info['max_value_year']})</p>
        <p><b>mean value:</b> {crime_dict_info['mean_value']}</p>
        <p><b>standard deviation:</b> {crime_dict_info['standard_deviation']}</p>
        <p><b>crime category:</b> {crime_table.crime_category}</p>
        <p><b>trend:</b> {crime_dict_info['trend']}</p>
        <p><b>relative trend strength:</b> {crime_dict_info['relative_trend_strength']}</p>
        <p><b>suspicious values:</b> {crime_dict_info['count_outliers']}</p>
        """
        display(HTML(text))

        if crime_table.filtered_data.empty:
            print("No data available for the selected country and crime.")
            return

        min_year = crime_table.statistics.min_range_year
        max_year = crime_table.statistics.max_range_year

        if not (np.isfinite(min_year) and np.isfinite(max_year)):
            min_year, max_year = 0, 1

        plt.figure(figsize=(10, 6))
        plt.plot(crime_table.filtered_data['year'],
                 crime_table.filtered_data['value'], marker='o')
        plt.title(f"Time Series for {select_country} and crime: {select_crime}")
        plt.xlabel("Year")
        plt.ylabel("Value")
        plt.grid(True)
        plt.xlim(min_year, max_year)
        plt.show()


country.observe(update_output, names='value')
crime.observe(update_output, names='value')


display(widgets.HBox([country, crime]))
display(output)


update_output()
