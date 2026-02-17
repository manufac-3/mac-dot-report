import pandas as pd
from db5_global.db52_dtype_dict import f_types_vals


def reorder_dfr_cols_perm(df):  # Defines both order and PRESENCE of columns
    desired_order = [
        'item_name',
        'item_type',
        'unique_id',
        'item_name_rp',
        'item_type_rp',
        'repo_scope_rp',
        'git_rp',
        'item_name_hm',
        'item_type_hm',
        'item_name_hm_db',
        'item_type_hm_db',
        'item_name_rp_db',
        'item_type_rp_db',
        'repo_scope_db',
        'item_name_rp_cf',
        'item_type_rp_cf',
        'item_name_hm_cf',
        'item_type_hm_cf',
        'repo_scope_cf',
        'dot_struc_cf',
        'cat_1_cf',
        'cat_1_name_cf',
        'cat_2_cf',
        'comment_cf',
        'no_show_cf',
        'sort_orig',
        'unique_id_rp',
        'unique_id_db',
        'unique_id_hm',
        'unique_id_cf',
        'item_name_repo',
        'item_type_repo',
        'item_name_home',
        'item_type_home',
        'sort_out',
        'st_docs',
        'st_alert',
        'dot_struc',
        'st_db_all',
        'st_misc',
        'm_status_dict',
        'm_consol_dict',
        'm_status_result',
        'm_consol_result',
        'st_match_symb',
    ]
    # Ensure all columns in desired_order are in the DataFrame
    for col in desired_order:
        if col not in df.columns:
            print(f"Warning: Column {col} not found in DataFrame. Adding it with default values.")
            df[col] = None  # Add the missing column with default values
    
    # Reorder columns
    df = df[desired_order]
    
    return df
