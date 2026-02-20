import os
import pandas as pd


FIXTURE_CSV_PATH = "./data/test_fixtures.csv"
FIXTURE_COLUMNS = [
    "fixture_id",
    "item_name",
    "scope",
    "fixture_type",
    "enabled",
    "suppress_unmatched",
    "suppress_alert",
    "expected_state",
    "notes",
]
BOOL_COLUMNS = {"enabled", "suppress_unmatched", "suppress_alert"}


def parse_bool(value):
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def load_fx_dataframe(path=FIXTURE_CSV_PATH):
    if not os.path.exists(path):
        return pd.DataFrame(columns=FIXTURE_COLUMNS)

    df = pd.read_csv(path, dtype="string").copy()

    for col in FIXTURE_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    df = df[FIXTURE_COLUMNS]

    for col in FIXTURE_COLUMNS:
        if col in BOOL_COLUMNS:
            df[col] = df[col].apply(parse_bool)
        else:
            df[col] = df[col].astype("string").str.strip()

    return df
