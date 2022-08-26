import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output
from dash import dash_table as dt
# from dash_bootstrap_templates import load_figure_template

from src.helpers import load_data, prepare_meta, prepare_embeddings, \
    select_features, get_pop_indices, find_closest_riders, \
    make_rider_table, make_output_table, make_spider_plot


app = Dash(__name__,
           meta_tags=[
               {"name": "viewport", "content": "width=device-width, initial-scale=1"}],
           external_stylesheets=[dbc.themes.SANDSTONE]  # UNITED, SANDSTONE, MORPH
           )
# load_figure_template("LUX")

server = app.server


############################## load & prepare data
df = load_data()
df_meta = prepare_meta(df)
arr_emb, features = prepare_embeddings(df)

RIDERS = df_meta["name"].tolist()
COUNTRIES = df_meta["country"].unique().tolist()
##################################################


app.layout = dbc.Container([
    
    ### HEADER ###
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Find similar pro cyclists"),
                dcc.Markdown("This is a tiny tool to find similar cyclists given a chosen rider. "
                             "You can limit the pool based on age, country, and characteristics. "
                             "The data come from a community-created database for the game Pro Cycling Manager 2022. "
                             "Have fun!")
            ], style={"padding-top": "15px"})
        ], width=8),
        dbc.Col([
            html.Div([
                dcc.Markdown("Find more info on GitHub [here](https://github.com/DataWanderers/find-a-similar-pro-cyclist).")
            ], style={"text-align": "right"})
        ])
    ], align="end"),
    
    html.Hr(style={"margin-top": "0px", "opacity": "unset"}),

    dbc.Row([
        ### INPUT SELECTED RIDER ###
        dbc.Col([
            html.Div([
                html.H3("Pick a cyclist"),
                dcc.Dropdown(
                    RIDERS,
                    "Jasper Philipsen",  # default value
                    id="rider"
                )
            ], style={"margin-bottom": "5px"})
        ], width=3),

        ### OUTPUT SELECTED RIDER ###
        dbc.Col([
            html.Div(id="main-rider")
        ], width=9)  # or True
    ]),

    html.Hr(),

    dbc.Row([
        ### OTHER INPUTS ###
        dbc.Col([
            
            html.Div([
                html.Div([
                    html.H6("Similar cyclists"),
                    dcc.Input(
                        id="n_cyclists",
                        type="number",
                        value=5,
                        min=1
                    )
                ], style={"width": "70%", "margin-bottom": "10px"}),
                html.Div([
                    html.H6("Maximum age"),
                    dcc.Input(
                        id="max_age",
                        type="number",
                        value=35,
                        min=18
                    )
                ], style={"width": "70%", "margin-bottom": "10px"}),
                html.Div([
                    html.H6("Country"),
                    dcc.Dropdown(
                        COUNTRIES,
                        "",  # default value
                        multi=True,
                        id="countries",
                    )
                ], style={"margin-bottom": "10px"}),
                html.Div([
                    html.H6("Characteristics"),
                    dcc.Dropdown(
                        features,
                        "",  # default value
                        multi=True,
                        id="features"
                    )
                ], style={})
            ], style={})
            
        ], width=2),

        ### OUTPUT SIMILAR RIDERS ###
        dbc.Col([
            html.Div([
                dcc.Graph(id="similar-riders-plot")
            ], style={"verticalAlign": "top"})
        ], width=5),
        dbc.Col([
            html.Div([
                html.Div(id="similar-riders", style={"padding-bottom": "10px"})
            ])
        ], width=5)
    ])

], style={"backgroundColor": "white"})


@app.callback(
    Output("main-rider", "children"),
    Output("similar-riders", "children"),
    Output("similar-riders-plot", "figure"),
    Input("rider", "value"),
    Input("n_cyclists", "value"),
    Input("max_age", "value"),
    Input("countries", "value"),
    Input("features", "value")
)
def update_similar_riders(rider, k=10, age_max=30, countries="", features_in=""):
    # apply filtering
    arr_emb_, features_out = select_features(arr_emb, features, features_in)
    pop_indices = get_pop_indices(df_meta, age_max=age_max, countries=countries)

    # find the closest riders
    rider_i, D, I, pop_indices = find_closest_riders(arr_emb_, pop_indices, rider=rider, riders_all=RIDERS, k=k)

    # make main rider output
    out_rider = make_rider_table(rider_i, arr_emb_, df_meta, features_out)

    # make similar riders output
    out_simil = make_output_table(I, arr_emb_, df_meta, features_out, pop_indices)

    # make spider plot
    fig = make_spider_plot(out_rider, out_simil)

    return dbc.Table.from_dataframe(out_rider, bordered=True, hover=True,responsive=True, striped=True, style={}), \
           dbc.Table.from_dataframe(out_simil, bordered=True, hover=True, responsive=True, striped=True, style={}), \
           fig


if __name__ == "__main__":
    app.run_server(debug=True)
