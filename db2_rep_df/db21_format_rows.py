


import pandas as pd
from db5_global.db52_dtype_dict import f_types_vals

def insert_blank_rows(df):
    """
    NOTE: Temporarily converted numeric columns to 'object' type for display purposes to allow insertion of empty strings.
    This affects data types until conversion back to 'Int64' after display.
    """
    # Convert numeric columns to object just before adding blank rows
    numeric_cols = df.select_dtypes(include=['Int64', 'float']).columns
    df[numeric_cols] = df[numeric_cols].astype('object')
    
    # Get unique sort_out values
    unique_sort_out_values = df['sort_out'].unique()
    
    # Create a list to hold the new rows
    new_rows = []
    
    # Iterate through unique sort_out values
    for i, value in enumerate(unique_sort_out_values):
        # Get the rows with the current sort_out value
        group = df[df['sort_out'] == value]
        
        # Append the group to the new rows list
        new_rows.append(group)
        
        # Create a blank row with the correct data types (empty strings for all fields)
        blank_row = {}
        for col in df.columns:
            if col in f_types_vals:
                dtype = f_types_vals[col]['dtype']
                if dtype in ['object', 'string']:
                    blank_row[col] = ''  # Empty string for string columns
                elif dtype in ['Int64', 'float', 'boolean']:
                    blank_row[col] = ''  # Empty string for numeric/boolean columns too (now object dtype)
                else:
                    blank_row[col] = ''  # Fallback case
            else:
                blank_row[col] = ''  # Default for unhandled columns

        blank_row = pd.Series(blank_row, index=df.columns)
        
        # Append the blank row only if it's not the last group
        if i < len(unique_sort_out_values) - 1:
            new_rows.append(pd.DataFrame([blank_row]))
    
    # Concatenate the new rows into a new DataFrame
    new_df = pd.concat(new_rows, ignore_index=True)
    
    return new_df

def filter_report_df(df, hide_no_shows, hide_full_matches, hide_full_and_only, show_mstat_f, show_mstat_t):
    if hide_no_shows:
        df = df[df['no_show_cf'] == False].copy()
    if hide_full_matches:
        df = df[~df['dot_struc'].str.contains('rp>hm', na=False)].copy()
    if hide_full_and_only:
        df = df[~df['dot_struc'].str.contains('rp>hm|rp|hm', na=False)].copy()
    if show_mstat_f:
        df = df[df['m_status_result'] == False].copy()  # Corrected to filter boolean values
    if show_mstat_t:
        df = df[df['m_status_result'] == True].copy()   # Corrected to filter boolean values
    return df

def sort_report_df(df):
    # Keep subgroup ordering based on CSV sequence, then push NoSym items
    # to the bottom within each subgroup while preserving CSV order.
    df.loc[:, 'cat_1_key'] = df['cat_1_cf'].astype('string').fillna('__uncat_1__')
    df.loc[:, 'cat_2_key'] = df['cat_2_cf'].astype('string').fillna('__uncat_2__')
    df.loc[:, 'group_sort_key'] = (
        df.groupby(['cat_1_key', 'cat_2_key'], dropna=False)['sort_orig']
        .transform('min')
        .astype('Int64')
    )

    df.loc[:, 'secondary_sort_key'] = df['git_rp'].apply(lambda x: 1 if x == False else 0)
    if 'nosym_sort' not in df.columns:
        df.loc[:, 'nosym_sort'] = 0

    df = df.sort_values(
        by=['group_sort_key', 'nosym_sort', 'secondary_sort_key', 'sort_orig'],
        ascending=[True, True, True, True]
    )
    df = df.drop(columns=['cat_1_key', 'cat_2_key', 'group_sort_key', 'secondary_sort_key'])
    return df

def sort_filter_report_df(df, hide_no_shows, hide_full_matches, hide_full_and_only, show_mstat_f, show_mstat_t):
    df = filter_report_df(df, hide_no_shows, hide_full_matches, hide_full_and_only, show_mstat_f, show_mstat_t)
    df = sort_report_df(df)
    return df
