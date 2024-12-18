import pandas as pd
import numpy
from dataclasses import dataclass
from eurostatlib.crimestats import Statistics


@dataclass
class EurostatCrimeTable:
    data: pd.DataFrame = None
    country_list_sorted: list = None
    crime_list_sorted: list = None
    country: str = None
    crime: str = None
    crime_category: str = None
    filtered_data: pd.DataFrame = None
    statistics: Statistics = None
    statistics_info: str = None
    country_crime_info_11: pd.DataFrame = None

    def _get_sorted_list(self, unpivot_data):
        country_list_sorted = sorted(unpivot_data['country_name'].unique())
        self.country_list_sorted = country_list_sorted

        crime_list_sorted = sorted(unpivot_data['crime_info'].unique())
        self.crime_list_sorted = crime_list_sorted


    def load_data(self, path, geo_df, iccs_df):
        data = pd.read_csv(path, sep='\t')

        data = data.rename({data.columns[0]: data.columns[0].replace(
            '\\TIME_PERIOD', '')}, axis='columns')
        split_name_columns = (data.columns[0]).split(',')
        count_split_columns = len(split_name_columns)
        data[split_name_columns] = data[data.columns[0]
                                        ].str.split(',', expand=True)

        # odstraneni jiz rozdeleneho sloupce
        data = data.drop(data.columns[0], axis='columns')

        data = data.merge(geo_df, how='left', on='geo')
        data = data.merge(iccs_df, how='left', on='iccs')

        data = data.drop(columns=['geo', 'iccs'])

        # presun rozdelenych a naparovaných udaju na zacatek df
        reorg_columns = data.columns.tolist()
        final_reorg_columns = reorg_columns[-(count_split_columns):] + \
            reorg_columns[:-(count_split_columns)]
        data = data[final_reorg_columns]

        # podminka, ze se nejedna o rocni data
        no_anual = data[data['freq'] != 'A'].index
        data = data.drop(index=no_anual)

        # podminka, ze se nejedna o udaj na 100tis obyvatel
        no_p_hthab = data[data['unit'] != 'P_HTHAB'].index
        data = data.drop(index=no_p_hthab)

        years_list = data.columns[(count_split_columns):]
        info_list = data.columns[:(count_split_columns)]

        unpivot_data = pd.melt(
            data, id_vars=info_list, value_vars=years_list, var_name='year', value_name='value')

        unpivot_data['year'] = unpivot_data['year'].astype('int')
        unpivot_data['value'] = unpivot_data['value'].replace([': '], numpy.nan)
        unpivot_data['value'] = unpivot_data['value'].replace(['0 ', '0.00 ', 0], 0).astype('float')
        

        self._get_sorted_list(unpivot_data)

        #odstraneni zaznamu, protoze od roku 2019 oficialne tyto zeme/uzemni celky neposkytuji data
        unpivot_data = unpivot_data[ ~((unpivot_data['year'] >= 2019) & (unpivot_data['country_name'].isin(['Scotland (NUTS 2021)', 'England and Wales', 'Northern Ireland (UK) (NUTS 2021)'])))]

        self.data = unpivot_data

    def _calculate_statistics(self):
        data = self.filtered_data

        stat = Statistics()
        stat._calculate_from_data(data)
        self.statistics = stat

        # overeni vyplnenych hodnot - existence range
        if pd.notna(stat.last_fill_year) and pd.notna(stat.max_range_year):
            info = f'Between {stat.first_fill_year} and {stat.last_fill_year}, {self.country} reported {stat.count_fill_values} recorded entries for {self.crime} in the {stat.count_years}-year period. '

        else:
            info = 'Data disclosure information is incomplete or missing. '

        if stat.count_fill_values in [0, 1]:
            self.statistics_info = f'During a {stat.count_years}-year period, {self.country} recorded {
                stat.count_fill_values} entries for {self.crime} types of crime. {info} '

        elif stat.count_fill_values not in [0, 1]:
            trend = self.statistics.statistics_dictionary['trend']
            category = self.crime_category
            trend_stregth = self.statistics.statistics_dictionary['relative_trend_strength']
            unfill_values = self.statistics.statistics_dictionary['quality_range_unfill_data']
            fill_values = self.statistics.statistics_dictionary['quality_range_fill_data']
            crime = self.crime
            outliers =  self.statistics.count_outliers


            # Trend info
            if pd.notna(trend):
                if trend == 'increasing':
                    info_trend = 'The crime trend is increasing '
                elif trend == 'decreasing':
                    info_trend = 'The crime trend is decreasing '
                else:
                    info_trend = 'The trend is unclear due to missing data. '
            else:
                info_trend = 'The trend is unclear due to missing data. '

            # Trend strength info
            if pd.notna(trend):
                if trend == 'to missing value(s)':
                    info_trend_strength = ''
                elif trend_stregth >= 0.8:
                    info_trend_strength = 'and very strong. '
                elif 0.5 < trend_stregth < 0.8:
                    info_trend_strength = 'and is moderately strong. '
                else:
                    info_trend_strength = 'and its weak nature suggests the possibility of slight movement in the opposite direction. '
            else:
                info_trend_strength = 'The strength of the trend cannot be determined due to missing or incomplete data. '

            # Crime category info
            if category == 'visible':
                category_info = 'As this crime falls into the "visible" category, an increasing trend likely reflects a genuine rise in occurrence, while a decrease may indicate an actual reduction in this type of crime. '
            elif category == 'sensitive':
                category_info = 'Since this crime falls into the "sensitive" category, an increasing trend may reflect improved reporting of these crimes, while a decrease may indicate underreporting or changes in reporting practices. '
            elif category == 'hidden':
                category_info = 'This crime is classified as "hidden", indicating high uncertainty in the data. An increasing trend may suggest better detection, while a decrease might reflect persistent underreporting or undetected cases. '
            else:
                category_info = 'The crime category is missing or invalid. '

            # Outliers info
            if outliers >= 1:
                outliers_info = f'The data exhibits {outliers} suspicious values. '
            else:
                outliers_info = ''

            # Unfill/missing values
            if unfill_values > 0:
                relative_unfill = round(
                    (unfill_values / (unfill_values + fill_values)) * 100, 2)
                unfill_info = f'During the observed period, {relative_unfill}% of the values were missing. This proportion of unfilled data may introduce biases into the results, warranting further investigation into the causes of these gaps. '
            else:
                unfill_info = f'During the observed period, there were no missing values. '

            # subcategory info
            if crime in ['Rape', 'Sexual assault']:
                subcategory = 'A criminal offense is a subcategory of the offense "Sexual violence"'
            elif crime == 'Child pornography':
                subcategory = 'A criminal offense is a subcategory of the offense "Sexual exploitation"'
            elif crime == 'Burglary of private residential premises':
                subcategory = 'A criminal offense is a subcategory of the offense "Burglary"'
            elif crime == 'Theft of a motorized vehicle or parts thereof':
                subcategory = 'A criminal offense is a subcategory of the offense "Theft"'
            elif crime == 'Bribery':
                subcategory = 'A criminal offense is a subcategory of the offense "Corruption"'
            else:
                subcategory = ''

            self.statistics_info = info + info_trend + info_trend_strength + \
                category_info + outliers_info + unfill_info + subcategory

    def filter_data(self, country, crime):
        self.country = country
        self.crime = crime

        filtered_data = self.data[(self.data['country_name'] == country) & (
            self.data['crime_info'] == crime)]
        filtered_data = filtered_data.sort_values(
            by='year', axis=0, ascending=True)

        self.filtered_data = filtered_data.reset_index()  # vznik noveho sloupce index!!

        crime_categories = {
            'Intentional homicide': 'visible',
            'Attempted intentional homicide': 'visible',
            'Serious assault': 'visible',
            'Kidnapping': 'visible',
            'Sexual violence': 'sensitive',
            'Rape': 'sensitive',
            'Sexual assault': 'sensitive',
            'Sexual exploitation': 'sensitive',
            'Child pornography': 'sensitive',
            'Robbery': 'visible',
            'Burglary': 'visible',
            'Burglary of private residential premises': 'visible',
            'Theft': 'visible',
            'Theft of a motorized vehicle or parts thereof': 'visible',
            'Unlawful acts involving controlled drugs or precursors': 'hidden',
            'Fraud': 'hidden',
            'Corruption': 'hidden',
            'Bribery': 'hidden',
            'Money laundering': 'hidden',
            'Acts against computer systems': 'hidden',
            'Participation in an organized criminal group': 'hidden'
        }
        self.crime_category = crime_categories.get(crime, 'category not found')

        self._calculate_statistics()

    def create_summary_df_1all(self):
        dictionary_list = list()

        for country_name in self.country_list_sorted:
            for crime_name in self.crime_list_sorted:
                self.filter_data(country_name, crime_name)
                self._calculate_statistics()
                country_crime_dict = {
                    'country': country_name, 'crime': crime_name, 'crime_category': self.crime_category}
                output_dictionary = self.statistics.statistics_dictionary
                country_crime_dict.update(output_dictionary)
                dictionary_list.append(country_crime_dict)
        country_crime_info_11 = pd.DataFrame.from_dict(dictionary_list)

        self.country_crime_info_11 = country_crime_info_11

