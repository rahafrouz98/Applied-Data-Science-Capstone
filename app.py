# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

launch_sites_df= spacex_df.groupby(['Launch Site'], as_index=False).first()['Launch Site']
sites_success_rating = spacex_df.groupby(['Launch Site'])['class'].mean()

sites_performance = spacex_df[['Launch Site','class']]
sites_performance = pd.get_dummies(sites_performance, columns=["class"])
sites_performance.columns = ['Launch Site','0','1']
sites_performance[['0','1']]= sites_performance[['0','1']].astype(int)
sites_performance = sites_performance.groupby('Launch Site').sum()
sites_performance.reset_index(inplace=True)


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',options=[
                                    {'label':'All Sites','value':'All'}, 
                                    {'label':launch_sites_df[0], 'value':launch_sites_df[0]},
                                    {'label':launch_sites_df[1], 'value':launch_sites_df[1]},
                                    {'label':launch_sites_df[2], 'value':launch_sites_df[2]},
                                    {'label':launch_sites_df[3], 'value':launch_sites_df[3]}
                                    ],
                                    value = 'All',
                                    placeholder ='place holder here', searchable = True ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=20000, step=1000,
                                                marks={0:'0',
                                                       100:'100'},
                                                value = [min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'All':
        fig = px.pie(sites_success_rating, values='class', 
        names=launch_sites_df, 
        title='Sites Success Rate')
        return fig
    else:
        filtered_data = sites_performance[sites_performance['Launch Site'] == entered_site]
        newlist = filtered_data[['0','1']].iloc[0].tolist()
        fig = px.pie(values=newlist, 
        names=['0','1'], 
        title='site performance for '+entered_site)
        return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] > low) & (spacex_df['Payload Mass (kg)'] < high)
    filtered_df = spacex_df[mask]
    if entered_site == 'All':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
        title='Payload vs. Outcome for all sites')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
        title='Payload vs. Outcome for '+entered_site)
        return fig
# Run the app
if __name__ == '__main__':
    app.run()