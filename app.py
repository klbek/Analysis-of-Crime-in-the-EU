from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from eurostatlib.crimetable import EurostatCrimeTable

crime_table = EurostatCrimeTable()

geo_df = pd.read_csv(f'data/geo.csv')
iccs_df = pd.read_csv(f'data/iccs.csv')

crime_table.load_data(f'data/estat_crim_off_cat.tsv', geo_df, iccs_df)
crime_table.create_summary_df_1all()
df_all = crime_table.country_crime_info_11
df_all_visual_info = df_all[['country', 'crime', 'crime_category', 'count_years', 'quality_range_fill_data', 'quality_range_unfill_data', 'trend', 'relative_trend_strength']]

app = Dash()

app.layout = [
    html.H1(className='row', children='Crime in European Union',
            style={'backgroundColor': '#eee','textAlign': 'left', 'fontFamily': '"Open Sans", verdana, arial, sans-serif', 'fontSize': '40px', 'color': 'rgb(42, 63, 95)', 'fontWeight': 'normal', 'padding': '30px', 'paddingLeft': '80px', 'marginBottom': '10px'}),
    html.Div([
        html.Div(children=[
            html.Div(children=[
            html.Div(children=[
            html.Label('Country'),
            dcc.Dropdown(crime_table.country_list_sorted,
                         crime_table.country_list_sorted[7], id='dropdown-country'),
            ], style={'width': '300px'}),
            html.Div(children=[
            html.Label('Crime'),
            dcc.Dropdown(crime_table.crime_list_sorted,
                         crime_table.crime_list_sorted[1], id='dropdown-crime'),

            ], style={'width': '300px'})
            ], style={'marginLeft': '80px', 'display': 'flex', 'gap': '20px', 'width': '100%'}),
            html.Br(),
            dcc.Graph(id='plot1'),
        ], style={'padding': 10, 'backgroundColor': '#eee','flex': 2, 'width': '66%', 'marginRight': '10px'}),


        html.Div(children=[
            html.Plaintext(
                id='summarized-info',
                style={'height': 300, 'width': '100%', 'textWrap' : 'wrap'},
            )], style={'padding': 10,
                       'flex': 1,
                       'width': '34%',
                       'backgroundColor': '#eee',
                       'display': 'flex',
                       'flexDirection': 'column' }
        )
    ], style={'display': 'flex', 'flexDirection': 'row', 'width': '100%', 'marginBottom': '20px'}
    ),

    html.Div([
        html.Div(children=[
            dcc.Graph(id='plot2')
        ], style={'backgroundColor': '#eee','flex': 2,'width': '66%', 'marginRight': '10px', 'padding': '10px'}),

        html.Div(children=[
            html.Div(f'Summary trend table excluding subcategory and no trend', style={'fontFamily': '"Open Sans", verdana, arial, sans-serif', 'fontSize': '17px', 'color': 'rgb(42, 63, 95)', 'fontWeight': 'normal', 'fontStyle': 'normal', 'fontVariant': 'normal', 'textAlign': 'center', 'paddingBottom': '10px'}),
            dash_table.DataTable(id='table1', page_size=10, style_table={'overflowX': 'auto'}),

        ], style={'backgroundColor': '#eee', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center','flex': 1,'padding': 10,'width': '34%', 'paddingTop': '40px', 'gap': '10px'})
    ], style={'display': 'flex', 'flexDirection': 'row'}),

    html.Div([
        html.Div(children=[
            html.Div(f'Summary trend table including Subcategory', style={'fontFamily': '"Open Sans", verdana, arial, sans-serif', 'fontSize': '17px', 'color': 'rgb(42, 63, 95)', 'fontWeight': 'normal', 'fontStyle': 'normal', 'fontVariant': 'normal', 'textAlign': 'center', 'paddingBottom': '10px'}),
            dash_table.DataTable(id='table2', style_table={'overflowX': 'auto', 'textAlign': 'auto'},style_data_conditional=[
                # Podmínka pro 'decreasing' a relative_trend_strength > 0.9
                {
                    'if': {
                        'filter_query': '{trend} = "decreasing" && {relative_trend_strength} > 0.85',
                        'column_id': 'relative_trend_strength'
                    },
                    'backgroundColor': 'rgba(144, 238, 144, 0.5)',  # Světle zelená barva
                    'color': 'black' 
                },
                # Podmínka pro 'increasing' a relative_trend_strength > 0.9
                {
                    'if': {
                        'filter_query': '{trend} = "increasing" && {relative_trend_strength} > 0.85',
                        'column_id': 'relative_trend_strength'
                    },
                    'backgroundColor': 'rgba(255, 99, 71, 0.5)',  # Světle červená barva
                    'color': 'black' 
                }
            ]),

        ], style={'backgroundColor': '#eee','width': '100%', 'marginTop': '20px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'paddingTop': '40px', 'paddingBottom': '100px', 'gap': '10px'})
    ])]

@app.callback(
    Output(component_id='plot1', component_property='figure'),
    Output(component_id='summarized-info', component_property='children'),
    Output(component_id='plot2', component_property='figure'),
    Output(component_id='table1', component_property='data'),
    Output(component_id='table2', component_property='data'),
    [Input(component_id='dropdown-country', component_property='value'),
     Input(component_id='dropdown-crime', component_property='value')]
)
def update_graph(select_country, select_crime):
    crime_table.filter_data(select_country, select_crime)

    # time series plot
    if crime_table.filtered_data['value'].notna().sum() == 0:
        time_series_plot = px.line(
            title=f'Time Series for {select_country} and crime: {select_crime}<br><span style="font-size:12px;color:gray;">Crime category: {crime_table.crime_category if pd.notna(crime_table.crime_category) else "Unknown"}'
        ).add_annotation(
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            text="No data available for this crime type.",
            showarrow=False,
            font=dict(size=16, color="red"),
            align="center"
        ).update_layout(
            title_x=0.5,
            xaxis=dict(
                visible=False
            ),
            yaxis=dict(
                visible=False
            )
        )
    else:
        # Výpočet IQR
        Q1 = crime_table.filtered_data['value'].quantile(0.25)
        Q3 = crime_table.filtered_data['value'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Pokud jsou hodnoty dostupné, vytvoří graf s IQR
        time_series_plot = px.line(
            crime_table.filtered_data,
            x='year',
            y='value',
            title=f'Time Series for {select_country} and crime: {select_crime}<br><span style="font-size:12px;color:gray;">Crime category: {crime_table.crime_category if pd.notna(crime_table.crime_category) else "Unknown"}'
        ).update_traces(
            mode='lines+markers'  # Zobrazení čáry i bodů
        ).add_shape(
            type='rect',
            x0=crime_table.filtered_data['year'].min(),
            x1=crime_table.filtered_data['year'].max(),
            y0=lower_bound,
            y1=upper_bound,
            fillcolor="rgba(0, 128, 255, 0.3)",  # Zelený odstín pro IQR rozsah
            line_width=0,
            layer="below"
        ).add_annotation(
            x=crime_table.filtered_data['year'].max() + 0.5,  # Na pravý okraj osy X
            y=(upper_bound + lower_bound) / 2,  # Uprostřed rozsahu IQR
            text="IQR Range",  # Popisek
            textangle=90,
            showarrow=False,
            font=dict(size=12, color="blue"),  # Styl textu
            align="right",
            xanchor="right",
            yanchor="middle"
        ).add_annotation(
            x=crime_table.filtered_data['year'].max() - 1.5,
            y=upper_bound,
            text=f"IQR Upper Bound: {upper_bound:.2f}",
            showarrow=False,
            font=dict(size=12, color="blue"),
            align="left"
        ).add_annotation(
            x=crime_table.filtered_data['year'].max() - 1.5,
            y=lower_bound,
            text=f"IQR Lower Bound: {lower_bound:.2f}",
            showarrow=False,
            font=dict(size=12, color="blue"),
            align="left"
        ).add_shape(
        type="line",
        x0=crime_table.filtered_data['year'].min(),
        x1=crime_table.filtered_data['year'].max(),
        y0=crime_table.statistics.mean_value,
        y1=crime_table.statistics.mean_value,
        line=dict(color="red", dash="dash"),  # Červená přerušovaná čára
        xref="x",
            yref="y"
        ).add_annotation(
            x=crime_table.filtered_data['year'].max() + 0.5,  # Na pravý okraj osy X
            y=crime_table.statistics.mean_value,  # Na úroveň průměru
            text=f"Mean: {crime_table.statistics.mean_value:.2f}",  # Popisek průměru
            showarrow=False,
            font=dict(size=12, color="red"),
            align="left",
            xanchor="left",
            yanchor="bottom"
        ).update_layout(
                title_x=0.5,  # Vycentrování názvu
                xaxis=dict(
                    tickmode='array',
                    tickvals=crime_table.filtered_data['year'].unique(),  # Všechny unikátní hodnoty roku
                    title='Year'
                ),
                yaxis=dict(
                    title='P_HTHAB',
                )
            )


    # graf info
    graph_info_div = html.Div([
    html.H2("Graph information:"),
    
    html.P([
        html.B("Country: "), 
        f"{crime_table.country}"
    ]),
    
    html.P([
        html.B("Crime: "), 
        f"{crime_table.crime}"
    ]),
    
    html.P(f"{crime_table.statistics_info}"),
    
    html.P([
        html.B("The data is expressed as the number of cases per one hundred thousand inhabitants")
    ]),
    
    html.P([
        html.B("Min value: "), 
        f"{crime_table.statistics.statistics_dictionary['min_value']} ({crime_table.statistics.statistics_dictionary['min_value_year']})"
    ]),
    
    html.P([
        html.B("Max value: "), 
        f"{crime_table.statistics.statistics_dictionary['max_value']} ({crime_table.statistics.statistics_dictionary['max_value_year']})"
    ]),
    
    html.P([
        html.B("Mean value: "), 
        f"{crime_table.statistics.statistics_dictionary['mean_value']}"
    ]),
    
    html.P([
        html.B("Standard deviation: "), 
        f"{crime_table.statistics.statistics_dictionary['standard_deviation']}"
    ]),
    
    html.P([
        html.B("Crime category: "), 
        f"{crime_table.crime_category}"
    ]),
    
    html.P([
        html.B("Trend: "), 
        f"{crime_table.statistics.statistics_dictionary['trend']}"
    ]),
    
    html.P([
        html.B("Relative trend strength: "), 
        f"{crime_table.statistics.statistics_dictionary['relative_trend_strength']}"
    ]),
    html.P([
        html.B("Suspicious values: "), 
        f"{crime_table.statistics.statistics_dictionary['count_outliers']}"
    ])
])
    # filtrování pro tabulku
    filtred_table = df_all_visual_info[df_all_visual_info['country'] == f'{crime_table.country}']
    no_subcategory = filtred_table[~filtred_table['crime'].isin(['Rape', 'Sexual assault', 'Child pornography', 'Burglary of private residential premises', 'Theft of a motorized vehicle or parts thereof', 'Bribery'])]
    no_subcategory_result = (
        no_subcategory
        .groupby(['crime_category', 'trend'])['relative_trend_strength']
        .mean()
        .reset_index()
        .query("trend != 'to missing value(s)'")  # Odstranění řádků s trendem 'to missing value(s)'
        .rename(columns={'relative_trend_strength': 'avg_relative_trend_strength'})
    )
    no_subcategory_result['avg_relative_trend_strength'] = no_subcategory_result['avg_relative_trend_strength'].round(2)
    filtred_no_subcategory_table_by_country = no_subcategory_result.sort_values(by='crime_category')

    
    filtred_table_by_country = filtred_table.sort_values(by='crime_category')
    
    # bar plot
    plot = go.Figure(
    data=[
        go.Bar(
            x=filtred_table['crime'],
            y=filtred_table['quality_range_fill_data'] - filtred_table['quality_range_unfill_data'],
            name='Count fill values',
            marker_color='blue'
        ),
        go.Bar(
            x=filtred_table['crime'],
            y=filtred_table['quality_range_unfill_data'],
            name='Count unfill values',
            marker_color='orange'
        ),
        go.Scatter(
            x=filtred_table['crime'],
            y=[filtred_table['count_years'].max()] * len(filtred_table['crime']),
            mode='lines',
            name='Count year period',
            line=dict(color='red', dash='dash')
        )
    ],
    layout=go.Layout(
        barmode='stack',
        title=dict(
            text=f"Crime Trends and Data Quality Indicators in {select_country}<br><span style='font-size:12px;color:gray;'>During the Reporting Period (including Subcategory)</span>",
            x=0.5,  # Center the title and subtitle
        ),
        xaxis=dict(
            title='Crime',
            tickvals=filtred_table['crime'],
            ticktext=[x[:16] + '...' if len(x) > 16 else x for x in filtred_table['crime']],
            tickangle=45  # Rotate the X-axis labels
        ),
        yaxis=dict(title=''),
        template='plotly_white',
        annotations=[
            dict(
                x=crime,
                y=filtred_table.loc[filtred_table['crime'] == crime, 'quality_range_fill_data'].sum(),
                text = (
                    f"{trend[:3].lower().replace('to ', '') if pd.notna(trend) else '-'} "
                    f"{'⬈' if pd.notna(trend) and trend[:3].lower() == 'inc' else '⬊' if pd.notna(trend) and trend[:3].lower() == 'dec' else '-'}<br>"
                    f"<span style='font-size:10px;color:gray;'>"
                    f"{str(strength) if pd.notna(strength) else '-'}</span>"
                ),
                showarrow=False,
                font=dict(size=12, color="black"),
                xanchor="center",
                yanchor="bottom"
            )
            for crime, trend, strength in zip(filtred_table['crime'], filtred_table['trend'],filtred_table['relative_trend_strength'])
        ]
    )
)

    return time_series_plot, graph_info_div, plot, filtred_no_subcategory_table_by_country.to_dict('records'), filtred_table_by_country.to_dict('records')


if __name__ == '__main__':
    app.run(debug=True)
