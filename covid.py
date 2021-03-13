#Madi Abzhanov
#20028754

import pycountry
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.express as px
from dash.dependencies import Output, Input

data = pd.read_csv("transformed_data.csv")
df1 = pd.read_csv("transformed_data.csv") #Make one more data for world map
data["DATE"] = pd.to_datetime(data["DATE"], format="%Y-%m-%d")
data.sort_values("DATE", inplace=True)



#clean the dataset
data.columns = map(str.lower, data.columns) #for convenience convert all capitals to lower cases
df1.columns = map(str.lower, df1.columns) 
data["tc"]=2.72**data["tc"] #INVERSE LOGARITHMIC FUNCTION for total cases and total deaths
data["td"]=2.72**data["td"]

df1["tc"]=2.72**df1["tc"] #INVERSE LOGARITHMIC FUNCTION for total cases and total deaths
df1["td"]=2.72**df1["td"]

#new column for latest data only
latestdata = data.query("date == '2020-10-19'")
latestdata["date"] = pd.to_datetime(data["date"], format="%Y-%m-%d")
latestdata.sort_values("date", inplace=True)
sorted_data = latestdata.sort_values('tc', ascending=False).head(10)

#--This Part of code is for the Map with slider only
#Make a list of all countries
list_countries = df1['country'].unique().tolist()
# print(list_countries) # Uncomment to see list of countries
d_country_code = {}  # To hold the country names and their ISO

for country in list_countries:
    try:
        country_data = pycountry.countries.search_fuzzy(country)
        # country_data is a list of objects of class pycountry.db.Country
        # The first item  ie at index 0 of list is best fit
        # object of class Country have an alpha_3 attribute
        country_code = country_data[0].alpha_3
        d_country_code.update({country: country_code})
    except:
        #print('could not add ISO 3 code for ->', country)
        # If could not find country, make ISO code ' '
        d_country_code.update({country: ' '})

# print(d_country_code) # Uncomment to check dictionary  

# create a new column iso_alpha in the df
# and fill it with appropriate iso 3 code
for k, v in d_country_code.items():
    df1.loc[(df1.country == k), 'iso_alpha'] = v



#DASH PART
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Covid Analytics: Explore COVID-19 affects on world-wide economics"

app.layout = html.Div(
    children=[
        


        html.Div(
            children=[
                html.P(children="👨‍⚕️🔬🦠", className="header-emoji",
                       style = {"text-align": "center"},
                ),
                html.H1(
                    children="COVID-19 ANALYTICS", className="header-title",
                    style = {"color": "white", "font-family":"courier", "background-color":"indigo", "margin": "4px auto", "text-align": "center", "max-width": "384px"},
                ),
                html.P(
                    children="Analyze the COVID-19 impact"
                    " on different countries around the world",
                    className="header-description",
                    style = {"color": "#black", "font-family":"courier", "margin": "4px auto", "text-align": "center", "max-width": "384px"},
                ),
                html.P(
                    children="By Madi Abzhanov",
                    className="header-description",
                    style = {"color": "red", "font-family":"courier", "margin": "4px auto", "font-size":"12px", "text-align": "center", "max-width": "384px"},
                ),
            ],
            className="header",
        ),

        html.Div(
            children=[
                html.P(
                    children="What is the total cases and total deaths for a specific country?",
                    className="header-description",
                    style = {"color": "black", "font-family":"verdana", "margin": "100px auto 20px", "font-size":"20px", "text-align": "center", "max-width": "384px"},
                ),

                html.Div(
                    children=[
                        html.Div(children="Choose the country:", className="menu-title",
                                 style = {"font-family":"verdana", "margin": "auto auto 10px", "font-weight": "bold"}),
                        dcc.Dropdown(
                            id="country-filter",
                            options=[
                                {"label": country, "value": country}
                                for country in np.sort(data.country.unique())
                            ],
                            value="Afghanistan",
                            clearable=False,
                            className="dropdown",
                            style = {"font-family":"verdana"},
                        ),
                    ]
                ),

                html.Div(
                    children=[
                        html.Div(
                            children="Specify Date Range:", className="menu-title",
                            style = {"font-family":"verdana", "margin": "15px auto 10px", "font-weight": "bold"}
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.date.min().date(),
                            max_date_allowed=data.date.max().date(),
                            start_date=data.date.min().date(),
                            end_date=data.date.max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="volumechart1",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="volumechart2",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),

        html.P(
            children="What are the most affected countries?",
            className="header-description",
            style = {"color": "black", "font-family":"verdana", "margin": "100px auto 20px", "font-size":"20px", "text-align": "center", "max-width": "384px"},
        ),

        dcc.Graph(
            figure = px.scatter(sorted_data.head(10), x='country', y='tc', size='tc', color='country', 
                                hover_name='country', size_max = 60, title = "Top 10 countries with the most cases")
        ),

        html.P(
            children="Which countries have strict policies responses throughout the year?",
            className="header-description",
            style = {"color": "black", "font-family":"verdana", "margin": "100px auto 20px", "font-size":"20px", "text-align": "center", "max-width": "384px"},
        ),
        
        dcc.Graph(
            figure = px.choropleth(data_frame = df1, 
                     locations= "iso_alpha",
                     color= "sti",  # value in column 'Confirmed' determines color
                     hover_name= "country",
                     color_continuous_scale= 'RdYlGn',  #  color scale red, yellow green
                     animation_frame= "date", title = "World map by stringency index")
        ),
    ]
)


@app.callback(
    [Output("volumechart1", "figure"), Output("volumechart2", "figure")],
    [
        Input("country-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_charts(country, start_date, end_date):
    mask = (
        (data.country == country)
        & (data.date >= start_date)
        & (data.date <= end_date)
    )
    filtered_data = data.loc[mask, :]
    price_chart_figure = {
        "data": [
            {
                "x": filtered_data["date"],
                "y": filtered_data["tc"],
                "type": "lines",
                "hovertemplate": "%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Total cases",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    volume_chart_figure = {
        "data": [
            {
                "x": filtered_data["date"],
                "y": filtered_data["td"],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {"text": "Total deaths", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return price_chart_figure, volume_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True)