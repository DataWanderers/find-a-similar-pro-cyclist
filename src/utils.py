import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.neighbors import NearestNeighbors


def load_data(path="data/cyclists_{year}.csv", year=2022):
    return pd.read_csv(path.format(year=year), encoding="latin-1", sep=";")


def prepare_meta(df):
    df_meta = df.iloc[:, :6].copy()

    # add full name
    df_meta["name"] = df_meta["gene_sz_firstname"] + " " + df_meta["gene_sz_lastname"]

    # add age
    age = (
        pd.to_datetime("today")
        - pd.to_datetime(df_meta["gene_i_birthdate"], format="%Y%m%d")
    ).dt.days / 365
    df_meta["age"] = np.floor(age.astype(int))

    return df_meta


def prepare_embeddings(df):
    # cast to array structure
    df_emb = df.iloc[:, 6:]
    arr_emb = df_emb.values.astype(np.float32)  # should be an array
    arr_emb = np.ascontiguousarray(arr_emb)  # should be c-contiguous

    # get cleaned characteristics columns
    features = [f.replace("charac_i_", "") for f in df_emb.columns]

    return arr_emb, features


def select_features(arr_emb, features, features_in):
    if len(features_in) != 0:
        features_idxs = [features.index(f) for f in features_in]
        arr_emb = arr_emb[:, features_idxs]

        features = features_in  # features_out

    return arr_emb, features


def get_pop_indices(df_meta, age_max, countries):
    # apply filter(s)
    if len(countries) != 0:
        pop_indices = df_meta[
            (df_meta.age <= age_max) & (df_meta.country.isin(countries))
        ].index
    else:
        pop_indices = df_meta[df_meta.age <= age_max].index

    return pop_indices


def find_closest_riders(arr_emb, pop_indices, rider, riders_all, k=5):
    # get rider info to compare against
    rider_i = riders_all.index(rider)  # list index
    rider_i_emb = arr_emb[[rider_i]]

    # only use embeddings of filtered population
    if rider_i in pop_indices:
        pop_indices = np.delete(
            pop_indices, np.argwhere(pop_indices == rider_i)
        )  # remove rider_i if present

    arr_emb_pop = arr_emb[pop_indices]

    # search k closest riders
    neigh = NearestNeighbors(n_neighbors=k)
    neigh.fit(arr_emb_pop)

    # get distances (D) and indices (I)
    D, I = neigh.kneighbors(rider_i_emb, return_distance=True)

    return rider_i, D, I, pop_indices


def make_rider_table(idx, arr_emb, df_meta, features):
    stats = pd.DataFrame(arr_emb[idx], index=features).T

    df = pd.concat(
        [df_meta.iloc[[idx]][["name", "age", "country"]].reset_index(drop=True), stats],
        axis=1,
    )

    return df


def make_output_table(idxs, arr_emb, df_meta, features, pop_indices):
    # subset first to filtered population
    df_meta = df_meta.iloc[pop_indices]
    arr_emb = arr_emb[pop_indices]

    stats = pd.DataFrame(arr_emb[idxs[0]], columns=features)

    df = pd.concat(
        [
            df_meta.iloc[idxs[0]][["name", "age", "country"]].reset_index(drop=True),
            stats,
        ],
        axis=1,
    )

    return df


def make_spider_plot(df_rider, df_riders_simil):  # also called radar charts
    fig = go.Figure()

    df_riders = pd.concat([df_rider, df_riders_simil], axis=0)

    categories = df_riders.columns[3:].tolist()  # drop name, age, country
    for r, cyclist in enumerate(df_riders["name"]):
        points = df_riders.iloc[r][categories].tolist()

        fig.add_trace(
            go.Scatterpolar(
                r=points + [points[0]],  # repeat first point to close line
                theta=categories + [categories[0]],
                # fill="toself",
                name=cyclist,
            )
        )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[50, 85])),
        showlegend=False,
        margin=dict(l=80, r=70, t=0, b=5),
    )

    return fig
