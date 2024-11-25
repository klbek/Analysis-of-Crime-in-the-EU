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
    

    def _get_sorted_list(self, unpivot_data):
        country_list_sorted = sorted(unpivot_data['country_name'].unique())
        self.country_list_sorted = country_list_sorted

        crime_list_sorted = sorted(unpivot_data['crime_info'].unique())
        self.crime_list_sorted = crime_list_sorted

        # TODO filtrace crime dle toho, jestli ma dana zeme u crime alespon 1 vyplnenou hodnotu

    def load_data(self, path, geo_df, iccs_df):
        data = pd.read_csv(path, sep='\t')

        data = data.rename({data.columns[0]: data.columns[0].replace(
            r"\TIME_PERIOD", "")}, axis="columns")
        split_name_columns = (data.columns[0]).split(',')
        count_split_columns = len(split_name_columns)
        data[split_name_columns] = data[data.columns[0]
                                        ].str.split(',', expand=True)
        # odstraneni jiz rozdeleneho sloupce
        data = data.drop(data.columns[0], axis="columns")

        data = data.merge(geo_df, how='left', on='geo')
        data = data.merge(iccs_df, how='left', on='iccs')

        data = data.drop(columns=['geo', 'iccs'])

        # presun rozdelenych a naparovaných udaju  na zacatek df
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
        unpivot_data['value'] = unpivot_data['value'].replace(
            [': ', '0 ', '0.00 ', 0], numpy.nan).astype('float')

        self._get_sorted_list(unpivot_data)
        self.data = unpivot_data

    def _calculate_statistics(self):
        data = self.filtered_data

        stat = Statistics()
        stat._calculate_from_data(data)
        self.statistics = stat

        # overeni vyplnebych hodnot - existence range
        if pd.notna(stat.last_fill_year) and pd.notna(stat.max_range_year):
            if stat.last_fill_year != stat.max_range_year:
                info = f'Data disclosure by the country began in {
                    stat.first_fill_year} and ended in {stat.last_fill_year}.'
            elif stat.last_fill_year == stat.max_range_year:
                info = f'Data disclosure by the country began in {
                    stat.first_fill_year} and continues until {stat.max_range_year}.'
        else:
            info = 'Data disclosure information is incomplete or missing.'

        if stat.count_fill_values in [0, 1]:
            self.statistics_info = f'During a {stat.count_years}-year period, {self.country} recorded {
                stat.count_fill_values} entries for {self.crime} types of crime. {info}'
        elif stat.count_fill_values not in [0, 1]:
            self.statistics_info = f'During a {stat.count_years}-year period, {self.country} recorded {stat.count_fill_values} entries for {self.crime} types of crime. {info} Across these years, there were an average of {
                stat.mean_value} crimes per hundred thousand inhabitants each year and standard deviation was {stat.standard_deviation}. The minimum recorded crime rate per hundred thousand inhabitants was {stat.min_value} in {stat.min_value_year}, while the maximum was {stat.max_value} in {stat.max_value_year}.'

        # TODO: vyřešit info o státu/kriminalitě
        # TODO:
        # přidat dodatečné  informace o směrodané odchylce
        # přidat info o násobku z min -> max aj
        # od jakého roku začal stát poskytovat/sbírat data - zmenit automaticky range ve widgete
        # vytvorit slovnik jako zaznamnik pro porovnani s ostatnimi zememi průmery, max, min v ráci tr. činnu

    def filter_data(self, country, crime):
        self.country = country
        self.crime = crime
   
        filtered_data = self.data[(self.data['country_name'] == country) & (
                self.data['crime_info'] == crime)]
        filtered_data = filtered_data.sort_values(
                by='year', axis=0, ascending=True)
        
        self.filtered_data = filtered_data.reset_index() # vznik noveho sloupce index!!   
        self._calculate_statistics()

        crime_categories = {
        "Intentional homicide": "Visible",
        "Attempted intentional homicide": "Visible",
        "Serious assault": "Visible",
        "Kidnapping": "Visible",
        "Sexual violence": "Sensitive",
        "Rape": "Sensitive",
        "Sexual assault": "Sensitive",
        "Sexual exploitation": "Sensitive",
        "Child pornography": "Sensitive",
        "Robbery": "Visible",
        "Burglary": "Visible",
        "Burglary of private residential premises": "Visible",
        "Theft": "Visible",
        "Theft of a motorized vehicle or parts thereof": "Visible",
        "Unlawful acts involving controlled drugs or precursors": "Hidden",
        "Fraud": "Hidden",
        "Corruption": "Hidden",
        "Bribery": "Hidden",
        "Money laundering": "Hidden",
        "Acts against computer systems": "Hidden",
        "Participation in an organized criminal group": "Hidden"
        }
        self.crime_category = crime_categories.get(crime,'category not found')


    def create_summary_df_1all(self):
        dictionary_list = list()

        for country_name in self.country_list_sorted[1:]:
            for crime_name in self.crime_list_sorted[1:]:
                country_crime_dict = {
                    'country': country_name, 'crime': crime_name, 'crime_category': self.crime_category}
                
                self.filter_data(country_name, crime_name)
                self._calculate_statistics()
                output_dictionary = self.statistics.statistics_dictionary
                country_crime_dict.update(output_dictionary)
                dictionary_list.append(country_crime_dict)
        country_crime_info_11 = pd.DataFrame.from_dict(dictionary_list)

        return country_crime_info_11

    def __str__(self):
        print(f'info {self.statistics}')

    