import faiss
import pandas as pd
import numpy as np

def load_data(path="data/cyclists.xlsx"):
    return pd.read_excel(path, engine="openpyxl")

def prepare_meta(df):
    df_meta = df.iloc[:, :6].copy()

    # add full name
    df_meta["name"] = df_meta["gene_sz_firstname"] + " " + df_meta["gene_sz_lastname"]

    # add age
    age = (pd.to_datetime("today") -
           pd.to_datetime(df_meta["gene_i_birthdate"], format="%Y%m%d")).dt.days / 365
    df_meta["age"] = np.floor(age.astype(int))

    return df_meta

def prepare_embeddings(df):
    # cast to array structure
    df_emb = df.iloc[:, 6:]
    arr_emb = df_emb.values.astype(np.float32)  # should be an array
    arr_emb = np.ascontiguousarray(arr_emb)  # should be c-contiguous

    # prepare faiss index
    index = faiss.IndexFlatL2(arr_emb.shape[1])

    # get cleaned characteristics columns
    features = [f.replace("charac_i_", "") for f in df_emb.columns]

    return arr_emb, index, features

def update_index(index, arr_emb, df_meta, age_max, countries):
    # apply filter(s)
    if len(countries) != 0:
        pop_indices = df_meta[(df_meta.age <= age_max) &
                              (df_meta.country.isin(countries))].index
    else:
        pop_indices = df_meta[df_meta.age <= age_max].index

    arr_emb_pop = arr_emb[pop_indices]

    # update index
    index.reset()
    index.add(arr_emb_pop)

    return pop_indices

def find_closest_riders(index, arr_emb, rider, riders_all, k=5):
    # get rider info to compare against
    rider_i = riders_all.index(rider)  # list index, has nothing to do with the faiss library
    rider_i_emb = arr_emb[[rider_i]]

    # get distances (D) and indices (I)
    D, I = index.search(rider_i_emb, k+1)  # search the k closest riders (drop first, will be rider_i)

    return rider_i, D, I

def make_rider_table(idx, arr_emb, df_meta, features):
    # get cycling stats
    stats = pd.DataFrame(arr_emb[idx], index=features).T

    # construct DataFrame
    df = pd.concat([df_meta.iloc[[idx]][["name", "age", "country"]].reset_index(drop=True), stats], axis=1)

    return df

def make_output_table(idxs, arr_emb, df_meta, features, pop_indices):
    # subset first to filtered population
    df_meta = df_meta.iloc[pop_indices]
    arr_emb = arr_emb[pop_indices]

    # get cycling stats
    stats = pd.DataFrame(arr_emb[idxs[0][1:]], columns=features)

    # construct DataFrame
    df = pd.concat([df_meta.iloc[idxs[0][1:]][["name", "age", "country"]].reset_index(drop=True), stats], axis=1)

    return df
