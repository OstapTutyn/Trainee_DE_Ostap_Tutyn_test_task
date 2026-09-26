import pandas as pd

def load_daily(path, day):
    df = pd.read_csv(path)
    df = df[df.event_time.str.startswith(day)] # якщо буде NaN у event_time, то буде помилка. Має бути str
    df["revenue_usd"] = df["revenue_usd"].astype(float) # якщо буде NaN або "" або 7,5, то буде помилка.
    totals = {}
    for i, row in df.iterrows():
        key = row["app_id"] + "-" + row["media_source"]       # якщо буде NaN, Null, число або "", то
                                                              # буде помилка. Має бути str.
        totals[key] = totals.get(key, 0) + row["revenue_usd"]

    return pd.DataFrame([{"key": k, "revenue": v} for k, v in totals.items()]).sort_values("revenue", ascending=False)
    # якщо не надійдуть дані і totals буде пустим, то повернеться порожній датафрейм і буде помилка.