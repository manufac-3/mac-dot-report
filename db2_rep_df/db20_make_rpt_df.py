import pandas as pd
import numpy as np

from db5_global.db52_dtype_dict import f_types_vals

from .db21_format_rows import insert_blank_rows, sort_filter_report_df
from .db22_format_cols import reorder_dfr_cols_perm
from .db24_match_reg import detect_full_domain_match
from .db26_match_alert import detect_alerts

from .db40_term_disp import reorder_dfr_cols_for_cli

# Opt-in to the future behavior for downcasting
pd.set_option('future.no_silent_downcasting', True)

def build_report_dataframe(main_df_dict, verbose=False):
    report_dataframe = main_df_dict['full_main_dataframe'].copy()
    report_dataframe = add_report_fields(report_dataframe)

    # report_dataframe = insert_blank_rows(report_dataframe)
    report_dataframe = reorder_dfr_cols_perm(report_dataframe)

    report_dataframe = detect_full_domain_match(report_dataframe)
    report_dataframe = detect_alerts(report_dataframe)
    report_dataframe = assign_dot_state(report_dataframe)
    report_dataframe = assign_nosym_sort(report_dataframe)

    # report_dataframe = resolve_fields_master(report_dataframe)
    report_dataframe = post_build_nan_replace(report_dataframe)
    report_dataframe = sort_filter_report_df(
        report_dataframe, 
        hide_no_shows=False, 
        hide_full_matches=False, 
        hide_full_and_only=False,
        show_mstat_f=False, # m_status_result = False (Not: Full, rp-only or hm-only match)
        show_mstat_t=False, # m_status_result = True (Full, rp-only or hm-only match)
        )
    
    # Print the result to the console
    # print("🟪 DEBUG: Full Report DataFrame")
    # print(report_dataframe[['item_name_repo', 'item_type_repo', 'item_name_home', 'item_type_home', 'm_consol_dict']])
    
    report_dataframe = reorder_dfr_cols_for_cli( # Reorder columns for CLI display
        report_dataframe,
        show_all_fields=verbose,
        show_main_fields=verbose,
        show_status_fields=verbose,
        show_setup_group=verbose,  # Only show if verbose mode is enabled
    )

    return report_dataframe


def add_report_fields(report_dataframe):
    df = report_dataframe
    new_columns = { # Define the new columns to add
        'item_name_repo': f_types_vals['item_name_repo'],
        'item_type_repo': f_types_vals['item_type_repo'],
        'item_name_home': f_types_vals['item_name_home'],
        'item_type_home': f_types_vals['item_type_home'],
        'sort_out': f_types_vals['sort_out'],
        'st_docs': f_types_vals['st_docs'],
        'st_alert': f_types_vals['st_alert'],
        'dot_struc': f_types_vals['dot_struc'],
        'st_db_all': f_types_vals['st_db_all'],
        'st_misc': f_types_vals['st_misc'],
        'm_status_dict': f_types_vals['m_status_dict'],
        'm_consol_dict': f_types_vals['m_consol_dict'],
        'm_status_result': f_types_vals['m_status_result'],
        'm_consol_result': f_types_vals['m_consol_result'],
        'st_match_symb': f_types_vals['st_match_symb'],
        'dot_state': f_types_vals['dot_state'],
        'nosym_sort': f_types_vals['nosym_sort'],
    }
    
    for column, properties in new_columns.items(): # Create the new columns ( + types & vals)
        dtype = properties['dtype']
        default_value = properties['default']
        df[column] = pd.Series([default_value] * len(df), dtype=dtype)
    
    df['sort_out'] = df['sort_out'].fillna(-1) # Initialize 'sort_out' column with -1


    return df


def normalize_token(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text == "" or text.lower() in {"none", "nan"}:
        return None
    return text


def derive_dot_state(row):
    dot_struc = normalize_token(row.get('dot_struc'))
    if dot_struc is None:
        dot_struc = normalize_token(row.get('dot_struc_cf'))
    repo_scope = normalize_token(row.get('repo_scope_cf'))

    if dot_struc == 'hm':
        return 'NoSym'
    if dot_struc in {'rp', 'rp>hm'}:
        if repo_scope == 'private':
            return 'Local'
        return 'Synced'

    if repo_scope == 'private':
        return 'Local'
    if repo_scope == 'public':
        return 'Synced'
    if repo_scope == 'local':
        return 'NoSym'
    return 'NoSym'


def assign_dot_state(df):
    df['dot_state'] = df.apply(derive_dot_state, axis=1)
    df['dot_state'] = df['dot_state'].astype(f_types_vals['dot_state']['dtype'])
    return df


def assign_nosym_sort(df):
    df['nosym_sort'] = df['dot_state'].apply(lambda v: 1 if str(v).strip() == 'NoSym' else 0)
    df['nosym_sort'] = df['nosym_sort'].astype(f_types_vals['nosym_sort']['dtype'])
    return df


def post_build_nan_replace(df): # Replace NaN vals
    for column in df.columns:
        if column in f_types_vals:
            default_value = f_types_vals[column]['default']
            df[column] = df[column].fillna(default_value)
        else:
            print(f"Column '{column}' not found in dictionary")
    return df

    # First, attempt to fill NaN values using the dictionary
    df = fill_na_with_defaults(df)

    return df
