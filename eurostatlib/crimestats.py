import pandas as pd
import numpy
from dataclasses import dataclass


@dataclass
class Statistics:
    count_years: int = pd.NA
    count_fill_values: int = pd.NA
    first_fill_year: int = pd.NA
    last_fill_year: int = pd.NA
    mean_value: float = numpy.nan
    median_value: float = numpy.nan
    max_value: float = numpy.nan
    max_value_year: int = pd.NA
    min_value: float = numpy.nan
    min_value_year: int = pd.NA
    standard_deviation: float = numpy.nan
    quality_range_fill_data: int = pd.NA
    quality_range_unfill_data: int = pd.NA
    missing_values_info: str = pd.NA
    trend: str = pd.NA
    relative_trend_strength: float = numpy.nan
    min_range_year: int = pd.NA
    max_range_year: int = pd.NA
    statistics_dictionary: dict = None

    def get_statistics_dict_info(self):
        self.statistics_dictionary = {
            'count_years': self.count_years,
            'count_fill_values': self.count_fill_values,
            'first_fill_year': self.first_fill_year,
            'last_fill_year': self.last_fill_year,
            'mean_value': self.mean_value,
            'median_value': self.median_value,
            'max_value': self.max_value,
            'max_value_year': self.max_value_year,
            'min_value': self.min_value,
            'min_value_year': self.min_value_year,
            'standard_deviation': self.standard_deviation,
            'quality_range_fill_data': self.quality_range_fill_data,
            'quality_range_unfill_data': self.quality_range_unfill_data,
            'missing_values_info': self.missing_values_info,
            'trend': self.trend,
            'relative_trend_strength': self.relative_trend_strength,
            'min_range_year': self.min_range_year,
            'max_range_year': self.max_range_year
        }

    def _check_trend(self, data):
        if self.quality_range_unfill_data != 0:
            self.trend = 'to missing value(s)'
        else:
            diffs = numpy.diff(data)
            sum_positive_number = numpy.sum(diffs[diffs > 0])
            sum_negative_number = numpy.sum(diffs[diffs < 0])

            # Pokud je soucet kladnych rozdilu vetsi nez soucet absolutnich hodnot zapornych rozdilu
            if sum_positive_number > abs(sum_negative_number):
                self.trend = 'increasing'
                self.relative_trend_strength = round(
                    sum_positive_number / (sum_positive_number + abs(sum_negative_number)), 2)

            elif abs(sum_negative_number) > sum_positive_number:
                self.trend = 'decreasing'
                self.relative_trend_strength = round(
                    abs(sum_negative_number) / (sum_positive_number + abs(sum_negative_number)), 2)

        # TODO: možno upravit fci tak, aby u ojediněle chybějících hodnot doplnila pomocí lineární interpolace hodnoty.

    def _detect_missing_values(self, data=None, idx_first_fill_year=None, idx_last_fill_year=None):
        if self.count_fill_values == 0:
            self.missing_values_info = f'No record for crime.'

        elif self.count_fill_values == 1:
            self.missing_values_info = f'Only 1 record for crime.'

        else:
            count_fill_values_range = data[idx_first_fill_year:(
                idx_last_fill_year + 1)]['value'].count()
            count_fill_year_range = data[idx_first_fill_year:(
                idx_last_fill_year + 1)]['year'].count()
            self.quality_range_fill_data = count_fill_year_range
            self.quality_range_unfill_data = count_fill_year_range - count_fill_values_range

            if count_fill_values_range == count_fill_year_range:
                self.missing_values_info = 'The time series has no missing values within the data disclosure period.'
            else:
                number = count_fill_year_range - count_fill_values_range
                self.missing_values_info = f'The time series has {
                    number} missing value(s) within the data disclosure period.'
            self._check_trend(data['value'])

    def _calculate_from_data(self, data):
        value_column = data['value']
        year_column = data['year']

        self.count_years = year_column.count()
        self.count_fill_values = value_column.count()

        self.min_range_year = year_column.min()
        self.max_range_year = year_column.max()

        if value_column.count() > 1:
            idx_first_fill_year = value_column.first_valid_index()
            self.first_fill_year = year_column[idx_first_fill_year]

            idx_last_fill_year = value_column.last_valid_index()
            self.last_fill_year = year_column[idx_last_fill_year]

            self.mean_value = round(value_column.mean(), 2)
            self.median_value = value_column.median()

            max_value_row = data.loc[data['value'].idxmax()]
            min_value_row = data.loc[data['value'].idxmin()]

            self.max_value, self.max_value_year = max_value_row[[
                'value', 'year']]
            self.min_value, self.min_value_year = min_value_row[[
                'value', 'year']]

            # ddof=1 ->nastavení na výběrovou směrodatnou odchylku, bez toho populační směrodatná odchylka
            self.standard_deviation = round(numpy.std(value_column, ddof=1), 2)

            self._detect_missing_values(
                data, idx_first_fill_year, idx_last_fill_year)
            self.get_statistics_dict_info()

        elif value_column.count() == 1:
            idx_first_fill_year = value_column.first_valid_index()
            self.min_value = data.loc[idx_first_fill_year, 'value']
            self.min_value_year = data.loc[idx_first_fill_year, 'year']
            self._detect_missing_values(data)
            self.get_statistics_dict_info()

        else:
            self._detect_missing_values(data)
            self.get_statistics_dict_info()
