import pandas as pd


# Feature table: one row per client (fixed rules only, no fit)
LEVELS = ["consommation_level_1", "consommation_level_2", "consommation_level_3", "consommation_level_4"]


def most_common(invoices, col):
    """Most common value of col per client; on a tie the smaller value wins (same as .mode())."""
    counts = invoices.groupby(["client_id", col]).size().rename("n").reset_index()
    top = counts.sort_values(["n", col], ascending=[False, True]).drop_duplicates("client_id")
    return top.set_index("client_id")[col]


def build_features(clients: pd.DataFrame, invoices:pd.DataFrame) -> pd.DataFrame:
    inv = invoices.copy()
    inv["invoice_date"] = pd.to_datetime(inv["invoice_date"])
    inv["counter_statue"] = inv["counter_statue"].astype(str)
    inv["total"] = inv[LEVELS].sum(axis=1)
    inv["zero"] = inv["total"] == 0
    inv["mismatch"] = inv["total"] != (inv["new_index"] - inv["old_index"])
    

    agg = inv.groupby("client_id").agg(
        n_invoices=("total", "size"),
        level_1_mean=("consommation_level_1", "mean"),
        level_2_mean=("consommation_level_2", "mean"),
        level_3_mean=("consommation_level_3", "mean"),
        level_4_mean=("consommation_level_4", "mean"),
        total_mean=("total", "mean"),
        total_std=("total", "std"),
        zero_share=("zero", "mean"),
        mismatch_any=("mismatch", "max"),
        first_invoice=("invoice_date", "min"),
        last_invoice=("invoice_date", "max"),
    )
    agg["history_years"] = (agg.pop("last_invoice") - agg.pop("first_invoice")).dt.days / 365.25

    cl = clients.set_index("client_id")
    feats = cl[["region", "disrict"]].copy()
    feats["catg_51"] = cl["client_catg"] == 51
    feats = feats.join(agg)
    feats["tarif_not_11"] = most_common(inv, "tarif_type") != 11
    statue = most_common(inv, "counter_statue")
    feats["statue_1"] = statue == "1"
    feats["statue_other"] = ~statue.isin(["0", "1"])

    bool_cols = feats.select_dtypes("bool").columns
    feats[bool_cols] = feats[bool_cols].astype(int)
    if "target" in cl:
        feats["target"] = cl["target"].astype(int)
    return feats