import pandas as pd


def remove_consolidated_columns(report_dataframe):
    # Remove extra unique_id fields


    columns_to_remove = ['unique_id_rp', 'unique_id_hm', 'unique_id_db', 'unique_id_cf']
    columns_to_remove = [col for col in columns_to_remove if col in report_dataframe.columns]
    report_dataframe.drop(columns=columns_to_remove, inplace=True)

    # Remove source fields for name and type
    columns_to_remove = [
        'item_name_rp', 'item_type_rp', 'item_name_hm', 'item_type_hm',
        'item_name_rp_db', 'item_type_rp_db', 'item_name_hm_db', 'item_type_hm_db',
        'item_name_rp_cf', 'item_type_rp_cf', 'item_name_hm_cf', 'item_type_hm_cf',
        'item_name', 'item_type'
    ]
    columns_to_remove = [col for col in columns_to_remove if col in report_dataframe.columns]

    report_dataframe.drop(columns=columns_to_remove, inplace=True) # THIS IS WHERE WE LOSE THE .zsh_sessions_TEST_ITEM🔵

    return report_dataframe

def reorder_dfr_cols_for_cli(report_dataframe, show_all_fields, show_main_fields, show_status_fields, show_setup_group):
    # PROVIDES DATAFRAME FIELD _GROUPS_ TO DISPLAY IN CLI W/O EXCEEDING WIDTH
    
    # All Fields Group
    all_fields_columns = report_dataframe.columns.tolist()

    # Final Output Group
    regular_field_columns = [
        'unique_id',
        'st_alert',
        'item_name_repo',
        'item_name_home',
        'dot_struc',
        'dot_state',
        'dot_struc_cf',
        'repo_scope_cf',
        'item_type_repo',
        'item_type_home',
        'cat_1_cf',
        'cat_1_name_cf',
        'cat_2_cf',
        'comment_cf',
        'git_rp',
        'st_db_all', 'st_docs',
        'st_misc',
        'sort_orig', 'sort_out',
        # 'm_consol_dict'
    ]

    # Field Merge Group
    status_field_columns = [
        'item_name_repo', 'item_name_home',
        'st_misc', 'st_alert', 'st_db_all', 'st_docs', 'dot_struc',
        'sort_out', 'sort_orig',
        'm_consol_dict'
    ]

    # Setup Group
    setup_group_columns = [
        # 'item_name',
        # 'item_name_repo',
        # 'item_name_home',
        # 'item_type_repo',
        # 'item_type_home',
        # 'item_type',
        # 'unique_id',
        'item_name_rp',
        'item_type_rp',
        'repo_scope_rp',
        # 'git_rp',
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
        'dot_state',
        'dot_struc',
        'st_match_symb',
        'dot_struc_cf',
        # 'cat_1_cf',
        # 'cat_1_name_cf',
        # 'cat_2_cf',
        # 'comment_cf',
        # 'unique_id_rp',
        # 'unique_id_db',
        # 'unique_id_hm',
        # 'unique_id_cf',
        # 'sort_out',
        # 'st_docs',
        'st_alert',
        # 'st_db_all',
        'st_misc',
        'm_status_dict',
        'm_consol_dict',
        'm_status_result',
        'm_consol_result',
        
        # 'no_show_cf',
        # 'sort_orig',
    ]

    # Display Complete Report_Dataframe
    if show_all_fields:
        print_dataframe_section(report_dataframe, all_fields_columns, "Report_Dataframe, Complete")

    # Display Report_Dataframe
    if show_main_fields:
        print_dataframe_section(report_dataframe, regular_field_columns, "Report_Dataframe")

    # Display Report_Dataframe Status Fields
    if show_status_fields:
        print_dataframe_section(report_dataframe, status_field_columns, "Report_Dataframe Merge Status Fields")

    # Display Setup Group
    if show_setup_group:
        print_dataframe_section(report_dataframe, setup_group_columns, "Report_Dataframe Setup Group")

    # Return reordered DataFrame if needed
    return report_dataframe

def print_dataframe_section(df, columns, title):
    print(f"{title}:")
    print(df[columns])
    print("\n" * 2)

    # print(f"{title} (Data Types):")
    # data_types_df = df[columns].apply(lambda col: col.apply(lambda x: type(x).__name__))
    # print(data_types_df)
    # print("\n" * 2)
