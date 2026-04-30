import pandas as pd
from auth import get_activity

def get_login_stats():
    data = get_activity()

    if not data:
        return pd.DataFrame({"No Data": [0]})

    df = pd.DataFrame(data, columns=["user", "action", "time"])

    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    # group by date
    stats = df.groupby(df["time"].dt.date).size()

    return stats