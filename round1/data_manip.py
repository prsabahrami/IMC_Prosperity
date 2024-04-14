import pandas as pd

df = pd.read_csv("prices_round_1_day_0.csv", sep=";")
df.fillna(0, inplace=True)

df["bidavg"] = (
    df["bid_price_1"] * df["bid_volume_1"]
    + df["bid_price_2"] * df["bid_volume_2"]
    + df["bid_price_3"] * df["bid_volume_3"]
) / (df["bid_volume_1"] + df["bid_volume_2"] + df["bid_volume_3"])

df["askavg"] = (
    df["ask_price_1"] * df["ask_volume_1"]
    + df["ask_price_2"] * df["ask_volume_2"]
    + df["ask_price_3"] * df["ask_volume_3"]
) / (df["ask_volume_1"] + df["ask_volume_2"] + df["ask_volume_3"])

df.to_csv("prices_round_1_day_0_mod.csv")