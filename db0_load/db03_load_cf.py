import logging
import pandas as pd
from db1_main_df.db14_merge_sup import get_next_unique_id
from db5_global.db52_dtype_dict import f_types_vals

def correct_and_validate_user_config_df(user_config_df):
    # Correct values: Replace NaN with empty strings in 'comment_cf' field
    user_config_df['comment_cf'] = user_config_df['comment_cf'].fillna('')
    return user_config_df


def infer_repo_scope_from_dot_struc(dot_struc_val):
    """Backfill repo scope when older config files do not include repo_scope_cf."""
    if pd.isna(dot_struc_val):
        return "local"
    if dot_struc_val in ("rp>hm", "rp"):
        return "public"
    if dot_struc_val == "hm":
        return "local"
    return "local"

def load_cf_dataframe():
    try:
        user_config_file_path = "./data/dotrep_config.csv"
        
        # Load the CSV with explicit data types for the columns using the 'dtype' value from f_types_vals
        user_config_df = pd.read_csv(user_config_file_path, dtype={
            "item_name_rp_cf": f_types_vals["item_name_rp_cf"]['dtype'],
            "item_name_hm_cf": f_types_vals["item_name_hm_cf"]['dtype'],
            "dot_struc_cf": f_types_vals["dot_struc_cf"]['dtype'],
            "item_type_rp_cf": f_types_vals["item_type_rp_cf"]['dtype'],
            "item_type_hm_cf": f_types_vals["item_type_hm_cf"]['dtype'],
            "cat_1_cf": f_types_vals["cat_1_cf"]['dtype'],
            "cat_1_name_cf": f_types_vals["cat_1_name_cf"]['dtype'],
            "cat_2_cf": f_types_vals["cat_2_cf"]['dtype'],
            "comment_cf": f_types_vals["comment_cf"]['dtype'],
            "no_show_cf": f_types_vals["no_show_cf"]['dtype']
        }).copy()

        # Backward-compatible repo scope support:
        # - If column is missing, infer from dot_struc_cf.
        # - If present but blank, backfill from dot_struc_cf.
        if "repo_scope_cf" not in user_config_df.columns:
            user_config_df["repo_scope_cf"] = user_config_df["dot_struc_cf"].apply(infer_repo_scope_from_dot_struc)
        else:
            user_config_df["repo_scope_cf"] = user_config_df["repo_scope_cf"].fillna(
                user_config_df["dot_struc_cf"].apply(infer_repo_scope_from_dot_struc)
            )
            user_config_df["repo_scope_cf"] = user_config_df["repo_scope_cf"].replace(
                to_replace=["", "None", "nan"], value=pd.NA
            )
            user_config_df["repo_scope_cf"] = user_config_df["repo_scope_cf"].fillna(
                user_config_df["dot_struc_cf"].apply(infer_repo_scope_from_dot_struc)
            )
        user_config_df["repo_scope_cf"] = user_config_df["repo_scope_cf"].astype(
            f_types_vals["repo_scope_cf"]['dtype']
        )

        # Record the original order of rows
        user_config_df['sort_orig'] = (user_config_df.index + 1).astype(f_types_vals["sort_orig"]['dtype'])  # Convert to Int64 explicitly

        # Assign unique IDs
        user_config_df['unique_id_cf'] = user_config_df.apply(lambda row: get_next_unique_id(), axis=1)
        user_config_df["unique_id_cf"] = user_config_df["unique_id_cf"].astype(f_types_vals["unique_id_cf"]['dtype'])

        # Apply the correction and validation function
        user_config_df = correct_and_validate_user_config_df(user_config_df)

        # Add the new merge key column
        user_config_df['item_name_cf_m_key'] = user_config_df.apply(
            lambda row: row['item_name_rp_cf'] if pd.notna(row['item_name_rp_cf']) and row['item_name_rp_cf'] != "none" else row['item_name_hm_cf'], axis=1
        )

        user_config_df["item_name_cf_m_key"] = user_config_df["item_name_cf_m_key"].astype(f_types_vals["item_name_rp_cf"]['dtype'])

        # Input dataframe display toggle
        show_output = False
        show_full_df = False

        if show_output:
            if show_full_df:
                print("7️⃣ user_config DataFrame:\n", user_config_df)
            else:
                print("7️⃣ user_config DataFrame (First 5 rows):\n", user_config_df.head())

        return user_config_df
    except Exception as e:
        logging.error(f"Error loading user_config CSV: {e}")
        return pd.DataFrame()
