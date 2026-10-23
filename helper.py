import numpy as np
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

    month = inv["invoice_date"].dt.month
    summer = inv[month.isin([6, 7, 8])].groupby("client_id")["total"].mean()
    winter = inv[month.isin([12, 1, 2])].groupby("client_id")["total"].mean()
    

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



######################## Code below needed for flag each client for seasonal suspicous behaviour ########################
# Use like this:
#   import helper as h
#
#   # learn the peer-group medians/MADs from train only
#   stats = h.fit_peer_stats(train_clients, train_invoices)
#
#   # apply the same stats to both sets and add to new column in existing feature set
#   train_features["n_signals"] = h.consumption_signals(train_clients, train_invoices, stats, min_prev=2)
#   holdout_features["n_signals"] = h.consumption_signals(holdout_clients, holdout_invoices, stats, min_prev=2)
#
# To check how the fraudster rate is for the newly flagged clients:
#
#   for name, feats in [("train", train_features), ("holdout", holdout_features)]:
#       print(f"{name} (overall fraud ratio: {feats['target'].mean():.4f})")
#       print(h.fraud_rate_by_signals(feats), "\n")
#########################################################################################################################


# Suspicious-consumption signals: peer comparison + own history
SEASONS = {12: "winter", 1: "winter", 2: "winter", 3: "spring", 4: "spring", 5: "spring",
           6: "summer", 7: "summer", 8: "summer", 9: "autumn", 10: "autumn", 11: "autumn"}
PEER_KEYS = ["disrict", "client_catg", "counter_type", "season"]
MAD_TO_STD = 1.4826  # makes the Median Absolute Deviation comparable to a Standard Deviation for normal data


def get_season_table(invoices: pd.DataFrame) -> pd.DataFrame:
    """Log mean consumption per invoice per client, counter type and season-year (December counts to the next winter)."""
    inv = invoices.copy()
    date = pd.to_datetime(inv["invoice_date"])
    inv["season"] = date.dt.month.map(SEASONS)
    inv["season_year"] = date.dt.year + (date.dt.month == 12)
    inv["total"] = inv[LEVELS].sum(axis=1)
    tab = inv.groupby(["client_id", "counter_type", "season", "season_year"]).agg(season_mean=("total", "mean"))
    tab["rate"] = np.log1p(tab["season_mean"])
    return tab["rate"].reset_index()


def fit_peer_stats(clients: pd.DataFrame, invoices: pd.DataFrame) -> pd.DataFrame:
    """Median, MAD and size per peer group (disrict x client_catg x counter_type x season). Fit on train only."""
    season_table = get_season_table(invoices).merge(clients[["client_id", "disrict", "client_catg"]], on="client_id")
    # absolute deviation of each rate from its peer-group median: groupby -> transform -> abs
    season_table["dev"] = (season_table["rate"] - season_table.groupby(PEER_KEYS)["rate"].transform("median")).abs()
    return season_table.groupby(PEER_KEYS).agg(median=("rate", "median"), mad=("dev", "median"), n=("rate", "size"))


def history_drop(season_table: pd.DataFrame, drop_cut: float = np.log(0.5), min_prev: int = 1) -> pd.Series:
    """True per client_id if the latest season-year fell clearly below the client's own earlier ones.

    season_table is the output of get_season_table (columns client_id, counter_type, season, season_year, rate).
    Per client, counter type and season the latest rate is compared with the median of the earlier
    season-years (at least min_prev of them); a log difference below drop_cut (default: halved) counts.
    """
    season_table = season_table.sort_values("season_year")
    keys = ["client_id", "counter_type", "season"]
    is_last = ~season_table.duplicated(keys, keep="last")
    prev = season_table[~is_last].groupby(keys)["rate"].agg(prev_median="median", n_prev="size")
    last = season_table[is_last].set_index(keys)["rate"].rename("last")
    cmp = prev.join(last, how="inner")
    cmp["drop"] = (cmp["n_prev"] >= min_prev) & (cmp["last"] - cmp["prev_median"] < drop_cut)
    # one flag per client (any season type dropped), padded with False for clients without a comparable season: groupby -> any -> reindex
    return cmp.groupby("client_id")["drop"].any().reindex(season_table["client_id"].unique(), fill_value=False)


def consumption_signals(clients: pd.DataFrame, invoices: pd.DataFrame, stats: pd.DataFrame,
                        z_cut: float = 3.0, min_hits: int = 2, min_group: int = 30,
                        drop_cut: float = np.log(0.5), min_prev: int = 1) -> pd.Series:
    """Number of suspicious-consumption signals per client (0, 1 or 2).

    Signal 1: robust z (median/MAD) below -z_cut against the peer group in at least min_hits season-years.
    Signal 2: history_drop. stats comes from fit_peer_stats (train); apply it to train, holdout and test alike.
    """
    season_table = get_season_table(invoices)
    peers = season_table.merge(clients[["client_id", "disrict", "client_catg"]], on="client_id").merge(stats.reset_index(), on=PEER_KEYS, how="left")
    usable = (peers["n"] >= min_group) & (peers["mad"] > 0)
    z = (peers["rate"] - peers["median"]) / (MAD_TO_STD * peers["mad"])
    peers["low"] = usable & (z < -z_cut)
    peer_signal = peers.groupby("client_id")["low"].sum() >= min_hits

    out = pd.DataFrame({"peer": peer_signal, "history": history_drop(season_table, drop_cut, min_prev)}).reindex(clients["client_id"])
    # missing signal = no signal; count the signals per client: fillna -> astype -> sum -> rename
    return out.fillna(False).astype(int).sum(axis=1).rename("n_signals")


def fraud_rate_by_signals(features: pd.DataFrame, signals: list = (1, 2)) -> pd.DataFrame:
    """Fraud ratio per number of suspicious-consumption signals (features needs the columns n_signals and target).

    Returns one row per requested signal count with the number of clients, the fraudsters among them and their ratio.
    """
    sub = features[features["n_signals"].isin(signals)]
    out = sub.groupby("n_signals")["target"].agg(clients="size", fraudsters="sum", fraud_ratio="mean")
    return out.reindex(list(signals))
