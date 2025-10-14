import pandas as pd

from .db11_make_main_df import build_main_dataframe
from db2_rep_df.db20_make_rpt_df import build_report_dataframe

# Set pandas display options globally (less verbose for console output)
pd.set_option('display.max_rows', 10)  # Limit rows instead of None
pd.set_option('display.max_columns', 10)  # Limit columns instead of None
pd.set_option('display.width', 120)  # Reasonable width instead of None
pd.set_option('display.max_colwidth', 30)

def build_full_output_dict(verbose=False):
    output_df_dict = {}

    # Load original dataframes for unmatched items comparison
    from db0_load.db01_load_hm import load_hm_dataframe
    from db0_load.db03_load_cf import load_cf_dataframe

    home_df = load_hm_dataframe()
    config_df = load_cf_dataframe()

    full_main_dataframe = build_main_dataframe(verbose=verbose)
    output_df_dict['full_main_dataframe'] = full_main_dataframe
    # print("\n FROM DB00: Full Main DataFrame:\n", full_main_dataframe)

    report_dataframe = build_report_dataframe(output_df_dict, verbose=verbose)
    output_df_dict['report_dataframe'] = report_dataframe
    # print("\n FROM DB00: Report DataFrame:\n", report_dataframe)

    # Create unmatched items lists
    fs_not_in_di, di_not_in_fs = find_unmatched_items(home_df, config_df)
    output_df_dict['fs_not_in_di'] = fs_not_in_di
    output_df_dict['di_not_in_fs'] = di_not_in_fs

    return output_df_dict

def find_unmatched_items(home_df, config_df):
    """
    Find unmatched items between home folder and config template.

    Returns:
    - fs_not_in_di: Items in filesystem (home) but not in dotrep index (config)
    - di_not_in_fs: Items in dotrep index (config) but not in filesystem (home)
    """
    # Items in home folder
    home_items = set(home_df['item_name_hm'].dropna())

    # Items in config (both repo and home variants)
    config_repo_items = set(config_df['item_name_rp_cf'].dropna())
    config_home_items = set(config_df['item_name_hm_cf'].dropna())
    config_items = config_repo_items.union(config_home_items)

    # Filter out 'none' values
    config_items = {item for item in config_items if item != 'none'}

    # Find unmatched items
    fs_not_in_di_names = home_items - config_items  # In home but not in config
    di_not_in_fs_names = config_items - home_items  # In config but not in home

    # Create structured data for template
    fs_not_in_di = []
    for item_name in sorted(fs_not_in_di_names):
        # Get item type from home dataframe
        home_row = home_df[home_df['item_name_hm'] == item_name]
        item_type = home_row['item_type_hm'].iloc[0] if not home_row.empty else 'file'
        fs_not_in_di.append({
            'item_name': item_name,
            'item_type': item_type
        })

    di_not_in_fs = []
    for item_name in sorted(di_not_in_fs_names):
        # Get item details from config dataframe
        config_row = config_df[
            (config_df['item_name_rp_cf'] == item_name) |
            (config_df['item_name_hm_cf'] == item_name)
        ]
        if not config_row.empty:
            row = config_row.iloc[0]
            item_type = row['item_type_hm_cf'] if row['item_name_hm_cf'] == item_name else row['item_type_rp_cf']
            comment = row['comment_cf']
            di_not_in_fs.append({
                'item_name': item_name,
                'item_type': item_type,
                'cf_comment': comment
            })

    return fs_not_in_di, di_not_in_fs