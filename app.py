from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

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
            dcc.Dropdown(df['country_name'].unique(),
                         'Albania', id='dropdown-country'),

            html.Br(),
            html.Label('Crime'),
            dcc.Dropdown(df['crime_info'].unique(),
                         'Intentional homicide', id='dropdown-crime'),

            ], style={'maxWidth': '300px'}),
            html.Br(),
            dcc.Graph(id='plot1')  # , style= {'width': '50%'}
        ], style={'padding': 10, 'flex': 2, 'width': '66%'}),


        html.Div(children=[
            html.Label('Summarized Info'),
            html.Br(),
            dcc.Textarea(
                id='textarea-example',
                value='Textarea content initialized\nwith multiple lines of text',
                style={'height': 300, 'resize': 'none', 'width': '100%'},
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
    [Input(component_id='dropdown-country', component_property='value'),
     Input(component_id='dropdown-crime', component_property='value')]
)
def update_graph(select_country, select_crime):

    dff = df[(df['country_name'] == select_country)
             & (df['crime_info'] == select_crime)]
    # create plot figure
    fig = px.line(dff, x='year', y='value')

    return fig


if __name__ == '__main__':
    app.run(debug=True)
