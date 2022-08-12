from dash import Dash, dcc, html, Input, Output
from dash import dash_table as dt
from src.helpers import load_data, prepare_meta, prepare_embeddings, \
    get_pop_indices, find_closest_riders, make_rider_table, make_output_table

app = Dash(__name__,
           meta_tags=[
               {"name": "viewport", "content": "width=device-width, initial-scale=1"}
           ])
server = app.server

############################## load & prepare data
df = load_data()
df_meta = prepare_meta(df)
arr_emb, features = prepare_embeddings(df)

RIDERS = df_meta["name"].tolist()
COUNTRIES = df_meta["country"].unique().tolist()
##################################################


app.layout = html.Div([
    ### HEADER ###
    html.Div([

        html.Div([
            html.H2("Find similar pro cyclists"),
            dcc.Markdown("This is a tiny tool to find similar cyclists given a chosen rider. "
                         "You can limit the pool based on age and country of origin. "
                         "The data come from a community-created database for the game Pro Cycling Manager. "
                         "Find more info on GitHub [here](https://github.com/DataWanderers/find-a-similar-pro-cyclist). "
                         "Have fun!")
        ], style={"width": "45%"})

    ]),

    ### INPUT ###
    html.Div([

        html.Div([
            html.H3("Pick a cyclist"),
            dcc.Dropdown(
                RIDERS,
                "Jasper Philipsen",  # default value
                id="rider"
            )
        ], style={"width": "30%", "margin-bottom": "5px"}),

        html.Div(id="main-rider",
                 style={"margin-top": "15px", "width": "80%"}),

        html.Div([
            html.Div([
                html.H4("Country"),
                dcc.Dropdown(
                    COUNTRIES,
                    "",  # default value
                    multi=True,
                    id="countries",
                )], style={"width": "25%", "padding-right": "20px", "float": "left", "display": "inline-block"}),
            html.Div([
                html.H4("# of similar cyclists"),
                dcc.Input(
                    id="n_cyclists",
                    type="number",
                    value=5,
                    min=1
                )], style={"width": "12%", "display": "inline-block", "vertical-align": "top"}),
            html.Div([
                html.H4("Maximum age"),
                dcc.Input(
                    id="max_age",
                    type="number",
                    value=29,
                    min=18
                )], style={"width": "12%", "display": "inline-block", "vertical-align": "top"})
        ], style={"padding-bottom": "15px"})

    ]),

    ### OUTPUT ###
    html.Div([

        html.Div(id="similar-riders",
                 style={"margin-top": "15px", "padding-bottom": "10px", "width": "80%"})

    ])
], style={"backgroundColor": "white"})


@app.callback(
    Output("main-rider", "children"),
    Output("similar-riders", "children"),
    Input("rider", "value"),
    Input("n_cyclists", "value"),
    Input("max_age", "value"),
    Input("countries", "value")
)
def update_similar_riders(rider, k=10, age_max=30, countries=""):
    pop_indices = get_pop_indices(df_meta, age_max=age_max, countries=countries)
    rider_i, D, I = find_closest_riders(arr_emb, pop_indices, rider=rider, riders_all=RIDERS, k=k)

    # make main-rider output
    out_rider = make_rider_table(rider_i, arr_emb, df_meta, features)
    data_rider = out_rider.to_dict("rows")

    # make similar-riders output
    out_simil = make_output_table(I, arr_emb, df_meta, features, pop_indices)
    data_simil = out_simil.to_dict("rows")

    columns = [{"name": j, "id": j,} for j in (out_rider.columns)]

    return dt.DataTable(data=data_rider, columns=columns), dt.DataTable(data=data_simil, columns=columns)


if __name__ == "__main__":
    app.run_server(debug=True)
