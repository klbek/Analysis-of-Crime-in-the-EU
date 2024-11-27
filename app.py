from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

from eurostatlib.crimetable import EurostatCrimeTable

crime_table = EurostatCrimeTable()

geo_df = pd.read_csv(r'data\geo.csv')
iccs_df = pd.read_csv(r'data\iccs.csv')

crime_table.load_data(f'data/estat_crim_off_cat.tsv', geo_df, iccs_df)
crime_table.create_summary_df_1all()



df = pd.read_csv(r'dashboards\crime_data_df.csv')
df2 = pd.read_csv(r'dashboards\test.csv')
dfbar = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

app = Dash()

app.layout = [
    html.H1(className='row', children='Crime in EU',
            style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30}),
    html.Div([
        html.Div(children=[
            html.Div(children=[
            html.Label('Country'),
            dcc.Dropdown(crime_table.country_list_sorted,
                         crime_table.country_list_sorted[7], id='dropdown-country'),

            html.Br(),
            html.Label('Crime'),
            dcc.Dropdown(crime_table.crime_list_sorted,
                         crime_table.crime_list_sorted[1], id='dropdown-crime'),

            ], style={'maxWidth': '300px'}),
            html.Br(),
            dcc.Graph(id='plot1')  # , style= {'width': '50%'}
        ], style={'padding': 10, 'flex': 2, 'width': '66%'}),


        html.Div(children=[
            html.Label('Summarized Info'),
            html.Br(),
            html.Plaintext(
                id='summarized-info',
                style={'height': 300, 'width': '100%', 'textWrap' : 'wrap'},
            )], style={'padding': 10,
                       'flex': 1,
                       'width': '34%',
                       'display': 'flex',
                       'flexDirection': 'column' }
        )
    ], style={'display': 'flex', 'flexDirection': 'row', 'width': '100%'}  # , 'width': '50%'
    ),

    html.Div([
        html.Div(children=[
            html.Label('Barchart'),
            dcc.Graph(figure=px.histogram(dfbar, x='continent',
                      y='lifeExp', histfunc='avg'), style={'flex': 1})
        ], style={'width': '50%'}),

        html.Div(children=[
            html.Label('Table'),
            dash_table.DataTable(data=df2.to_dict(
                'records'), page_size=10, style_table={'overflowX': 'auto'}),

        ], style={'width': '50%'})
    ], style={'display': 'flex', 'flexDirection': 'row', 'gap': '20px'})]


# @callback
@app.callback(
    Output(component_id='plot1', component_property='figure'),
    Output(component_id='summarized-info', component_property='children'),
    [Input(component_id='dropdown-country', component_property='value'),
     Input(component_id='dropdown-crime', component_property='value')]
)
def update_graph(select_country, select_crime):

    crime_table.filter_data(select_country, select_crime)


    # create plot figure
    fig = px.line(crime_table.filtered_data, x='year', y='value')

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
    ])
])
    
    
    return fig, graph_info_div




if __name__ == '__main__':
    app.run(debug=True)
