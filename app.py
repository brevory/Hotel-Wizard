import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import pycountry

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#To convert country abbreviations to their full names
def conversion(value):
    cname=""
    try:
        cname=pycountry.countries.get(alpha_3=value).name
    except Exception:
        pass
    return (cname)

#read csv's
df = pd.read_csv('hotel_bookings.csv',
                 parse_dates= {"date" : ["arrival_date_year","arrival_date_month","arrival_date_day_of_month"]},
                 keep_date_col=True)
dfGrouped = pd.read_csv('hotelgrouped.csv')
dfMarketSegment = pd.read_csv('hotelgroupedMarketSegment.csv')

#Applies the conversion function on all entries in the country column
df['country']=df['country'].apply(conversion)

# Sorting values
df = df.sort_values(by=['lead_time'],
ascending=[True]).reset_index()

#By Country Histogram data
country_data = px.histogram(df, x="country")
country_data.update_layout(
    title_text='Visitors from each Country',
    xaxis_title_text='Country',
    yaxis_title_text='Number of bookings'
)

#create people line chart
peopleLineChart = px.line(dfGrouped, x="date", y="adults", title='Number of people booking by date')

#create market segment pie chart
marketSegmentPie = px.pie(dfMarketSegment, values='count', names='market_segment',title='Market Segment Pie Chart')

#People Pie Chart
#Combine The People Columns
number_of_people=[df['adults'][i]+df['children'][i] + df['babies'][i] for i in range(len(df['adults']))]
df['number_of_people']=number_of_people

#Counter column for aggregation
counter=[]
for i in range(len(df['number_of_people'])):
        counter.append('1')
df['counter']=counter
people_data=px.pie(df, values='counter', names='number_of_people', title='Percentage of number of visitants in bookings')
people_data.update_layout(legend_title_text = "# of People")
people_data.update_traces(textposition='inside', textinfo='percent+label')

#Lead time Histogram
#Modifying entries to be more understandable with words
df.loc[df.is_canceled == 0, "is_canceled"] = "Not Cancelled"
df.loc[df.is_canceled == 1, "is_canceled"] = "Cancelled"
lead_data = px.histogram(df, x="lead_time", color="is_canceled")
lead_data.update_layout(
    title_text='Lead Time Histogram',
    xaxis_title_text='Lead Time (days)',
    yaxis_title_text='Number of visitors'
)

#html layout
app.layout = html.Div(children=[
    html.H1(children='HotelWizard',
            style={
                'textAlign': 'center'
            }),

    dcc.Graph(
        id='linechart',
        figure = peopleLineChart),
    html.Hr(),
    dcc.Graph(
        id = 'piechart',
        figure = marketSegmentPie
    ),
    html.Hr(),
    dcc.Graph(
        id="histogram",
        figure=country_data
    ),
    html.Hr(),
    dcc.Graph(
        id = 'piechart2',
        figure = people_data
    ),
    html.Hr(),
    dcc.Graph(
        id = 'histogram2',
        figure = lead_data
    ),

    html.Div([
            html.Hr(),
            html.H3(children='Budget Calculator',
                    style={'textAlign': 'left'}),
            html.Label('Enter number of rooms: '),
            dcc.Input(id='input-1-submit', type='text', placeholder='Enter a number'),
            html.Br(),
            html.Label('Enter the nightly fee: '),
            dcc.Input(id='input-2-submit', type='text', placeholder='Enter a number'),
            html.Br(),html.Br(),
            html.Button('Submit', id='btn-submit'),
            html.Br(),
            html.Label('Recommended spending (per month): '),
            html.Div(id='output-submit'),
            html.Br(), html.Hr()
    ])
])



#calculator callback
@app.callback(Output('output-submit', 'children'),
                [Input('btn-submit', 'n_clicks')],
                [State('input-1-submit', 'value'),State('input-2-submit', 'value')])
def update_output(clicked, input1, input2):
    if clicked:
        #return bills, supplies, maintenance, totalLabor, totalSpending
        a, b, c, d, e = calculator(int(input1), int(input2))
        return 'Bills: ' + str(a) + ', Supplies: ' + str(b) + ', Maintenance: ' + str(c) + ', Total labor: ' + str(d) + ', Total spending: ' + str(e)

#budget calculator logic
def calculator(numRooms, nightlyRate):
    revenue = nightlyRate * numRooms * 30 * .65  # average of 65% capacity - 30 days

    # ---spending---
    # labor, maintenance, bills, supplies

    housekeepers = 0
    housekeeperWage = 13
    clerks = 0
    clerkWage = 12
    managers = 0
    managerWage = 28
    supervisors = 0
    supervisorWage = 21
    security = 0
    securityWage = 16
    kitchen = 0
    kitchenWage = 11
    misc = 0
    miscWage = 15

    bills = 0
    supplies = 0
    maintenance = 0

    if numRooms < 10:
        housekeepers = 2
        clerks = 2
        managers = 1
        supervisors = 1
        security = 0
        kitchen = 2
        misc = 0
        bills = 2000
        supplies = 1000
        maintenance = 2000

    elif numRooms < 25 and numRooms >= 10:
        housekeepers = 5
        clerks = 2
        managers = 1
        supervisors = 1
        security = 0
        kitchen = 4
        misc = 1
        bills = 4000
        supplies = 2000
        maintenance = 4000
    elif numRooms < 50 and numRooms >= 25:
        housekeepers = 10
        clerks = 4
        managers = 1
        supervisors = 1
        security = 1
        kitchen = 4
        misc = 3
        bills = 8000
        supplies = 4000
        maintenance = 8000
    elif numRooms < 75 and numRooms >= 50:
        housekeepers = 15
        clerks = 5
        managers = 1
        supervisors = 2
        security = 2
        kitchen = 8
        misc = 5
        bills = 16000
        supplies = 8000
        maintenance = 16000
    elif numRooms >= 75:
        housekeepers = 20
        clerks = 5
        managers = 2
        supervisors = 3
        security = 4
        kitchen = 10
        misc = 10
        bills = 32000
        supplies = 16000
        maintenance = 32000

    # spending outputs
    hkCost = housekeepers * housekeeperWage * 160
    clerkCost = clerks * clerkWage * 160
    mngrCost = managers * managerWage * 160
    spCost = supervisors * supervisorWage * 160
    secCost = security * securityWage * 160
    kitchenCost = kitchen * kitchenWage * 160
    miscCost = misc * miscWage * 160
    totalLabor = hkCost + clerkCost + mngrCost + spCost + secCost + kitchenCost + miscCost
    totalSpending = totalLabor + bills + supplies + maintenance

    return bills, supplies, maintenance, totalLabor, totalSpending


if __name__ == '__main__':
    app.run_server(debug=True)