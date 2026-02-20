import pandas as pd

from db0_load.db00_load_rp import load_rp_dataframe
from db0_load.db01_load_hm import load_hm_dataframe
from db0_load.db02_load_db import load_dotbot_yaml_dataframe
from db0_load.db03_load_cf import load_cf_dataframe

from .db13_merge import df_merge_sequence

from db5_global.db50_global_misc import print_debug_info
from db5_global.db52_dtype_dict import f_types_vals

def build_main_dataframe(verbose=False):
    # Define individual DataFrames
    repo_df = load_rp_dataframe()
    home_df = load_hm_dataframe()
    dotbot_df = load_dotbot_yaml_dataframe()
    user_config_df = load_cf_dataframe()
    main_df = repo_df.copy() # Initialize the main_dataframe from the REPO FOLDER

    # Create global fields
    main_df['item_name'] = main_df['item_name_rp']
    main_df['item_type'] = main_df['item_type_rp']
    main_df['unique_id'] = main_df['unique_id_rp']

    print_df = 'full' if verbose else 'none'  # Specify the output level here: 'full', 'short', or 'none'

    # THE MERGE
    main_df = df_merge_sequence(main_df, home_df, dotbot_df, user_config_df, print_df) # Perform the merges

    # POST-MERGE OPERATIONS

    main_df = consolidate_item_type(main_df)

    main_df['sort_orig'] = main_df['sort_orig'].fillna(-1).astype('Int64') # sort_orig = Int64, handle missing vals

    main_df = apply_output_grouping(main_df)

    main_df = main_df.sort_values('sort_orig', ascending=True) # Sort the entire DataFrame by 'sort_orig'
    main_df = main_df.reset_index(drop=True)

    main_df = reorder_dfm_cols_perm(main_df)
    full_main_dataframe = main_df

    return full_main_dataframe


def consolidate_item_type(df):
    """Resolve consolidated item_type for rows that do not originate in repo scan."""
    type_priority = [
        "item_type",
        "item_type_rp",
        "item_type_hm",
        "item_type_rp_cf",
        "item_type_hm_cf",
        "item_type_rp_db",
        "item_type_hm_db",
    ]
    available = [col for col in type_priority if col in df.columns]
    if not available:
        return df

    # Use first non-null type across known sources.
    df["item_type"] = df[available].bfill(axis=1).iloc[:, 0]

    # Normalize variants used by symlink/alias sources for consistent display/type checks.
    normalize_map = {
        "file_sym": "file",
        "folder_sym": "folder",
        "file_alias": "file",
        "folder_alias": "folder",
    }
    df["item_type"] = df["item_type"].replace(normalize_map)
    df["item_type"] = df["item_type"].astype(f_types_vals["item_type"]['dtype'])
    return df

def apply_output_grouping(df):
    # Sort the entire DataFrame by 'sort_orig'
    df_sorted = df.sort_values('sort_orig', ascending=True)
    df_sorted = df_sorted.reset_index(drop=True)
    return df_sorted

def reorder_dfm_cols_perm(df):
    # Define the desired column order based on the provided fields
    desired_order = [
        'item_name', 'item_type', 'unique_id',
        'item_name_rp', 'item_type_rp', 'repo_scope_rp', 'git_rp', 'item_name_hm', 'item_type_hm',
        'item_name_hm_db', 'item_type_hm_db', 'item_name_rp_db', 'item_type_rp_db', 'repo_scope_db',
        'item_name_rp_cf', 'item_type_rp_cf', 'item_name_hm_cf', 'item_type_hm_cf', 'repo_scope_cf',
        'dot_struc_cf', 'cat_1_cf', 'cat_1_name_cf', 'cat_2_cf', 'comment_cf', 'no_show_cf',
        'sort_orig',
        'unique_id_rp', 'unique_id_db', 'unique_id_hm', 'unique_id_cf',
        # 'item_name_m_key', 'item_name_db_m_key', 'item_name_cf_m_key',
    ]

    # # Print the current columns in the DataFrame
    # print("Current DataFrame columns:\n", df.columns)

    # Ensure all columns in desired_order are in the DataFrame
    for col in desired_order:
        if col not in df.columns:
            print(f"Warning: Column {col} not found in DataFrame")
    
    # Reorder the DataFrame columns
    df = df[desired_order]
    return df
