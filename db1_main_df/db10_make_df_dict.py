import os
import pandas as pd

from .db11_make_main_df import build_main_dataframe
from db2_rep_df.db20_make_rpt_df import build_report_dataframe
from db0_load.db04_load_fx import load_fx_dataframe

# Set pandas display options globally (less verbose for console output)
pd.set_option('display.max_rows', 10)  # Limit rows instead of None
pd.set_option('display.max_columns', 10)  # Limit columns instead of None
pd.set_option('display.width', 120)  # Reasonable width instead of None
pd.set_option('display.max_colwidth', 30)

SHOW_FIXTURES_ENV = "DOTREP_SHOW_TEST_FIXTURES"
TRUE_VALUES = {'1', 'true', 't', 'yes', 'y', 'on'}

def build_full_output_dict(verbose=False):
    output_df_dict = {}

    # Load original dataframes for unmatched items comparison
    from db0_load.db01_load_hm import load_hm_dataframe
    from db0_load.db03_load_cf import load_cf_dataframe

    home_df = load_hm_dataframe()
    config_df = load_cf_dataframe()
    fixtures_df = load_fx_dataframe()
    show_fixtures = should_show_fixtures_in_report()
    hide_enabled_fixtures = not show_fixtures
    enabled_fixture_names = get_enabled_fixture_names(fixtures_df)
    fixture_flags = build_fixture_flags_by_item(fixtures_df)

    full_main_dataframe = build_main_dataframe(verbose=verbose)
    output_df_dict['full_main_dataframe'] = full_main_dataframe
    # print("\n FROM DB00: Full Main DataFrame:\n", full_main_dataframe)

    report_dataframe = build_report_dataframe(output_df_dict, verbose=verbose)
    if hide_enabled_fixtures:
        report_dataframe = suppress_fixture_rows(report_dataframe, enabled_fixture_names)
    else:
        report_dataframe = apply_fixture_alert_suppression(report_dataframe, fixture_flags)
    output_df_dict['report_dataframe'] = report_dataframe
    # print("\n FROM DB00: Report DataFrame:\n", report_dataframe)

    # Create unmatched items lists
    fs_not_in_di, di_not_in_fs = find_unmatched_items(
        home_df,
        config_df,
        fixture_flags,
        enabled_fixture_names,
        hide_enabled_fixtures,
    )
    output_df_dict['fs_not_in_di'] = fs_not_in_di
    output_df_dict['di_not_in_fs'] = di_not_in_fs
    output_df_dict['test_fixtures'] = fixtures_for_markdown(fixtures_df) if show_fixtures else []

    return output_df_dict


def should_show_fixtures_in_report():
    return str(os.getenv(SHOW_FIXTURES_ENV, "")).strip().lower() in TRUE_VALUES


def normalize_bool(value):
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in TRUE_VALUES


def get_enabled_fixture_names(fixtures_df):
    names = set()
    if fixtures_df is None or fixtures_df.empty:
        return names

    for _, row in fixtures_df.iterrows():
        if not normalize_bool(row.get('enabled')):
            continue
        item_name = row.get('item_name')
        if pd.isna(item_name):
            continue
        item_name = str(item_name).strip()
        if item_name:
            names.add(item_name)
    return names


def build_fixture_flags_by_item(fixtures_df):
    flags = {}
    if fixtures_df is None or fixtures_df.empty:
        return flags

    for _, row in fixtures_df.iterrows():
        item_name = row.get('item_name')
        if pd.isna(item_name):
            continue
        item_name = str(item_name).strip()
        if not item_name:
            continue

        enabled = normalize_bool(row.get('enabled'))
        if not enabled:
            continue

        entry = flags.setdefault(
            item_name,
            {'suppress_unmatched': False, 'suppress_alert': False},
        )
        entry['suppress_unmatched'] = (
            entry['suppress_unmatched'] or normalize_bool(row.get('suppress_unmatched'))
        )
        entry['suppress_alert'] = (
            entry['suppress_alert'] or normalize_bool(row.get('suppress_alert'))
        )

    return flags


def apply_fixture_alert_suppression(report_df, fixture_flags):
    if report_df is None or report_df.empty or not fixture_flags:
        return report_df

    suppress_names = {
        item_name
        for item_name, flags in fixture_flags.items()
        if flags.get('suppress_alert', False)
    }
    if not suppress_names:
        return report_df

    mask = report_df['item_name'].isin(suppress_names)
    report_df.loc[mask, 'st_alert'] = pd.NA
    return report_df


def suppress_fixture_rows(report_df, enabled_fixture_names):
    if report_df is None or report_df.empty or not enabled_fixture_names:
        return report_df
    return report_df.loc[~report_df['item_name'].isin(enabled_fixture_names)].copy()


def fixtures_for_markdown(fixtures_df):
    if fixtures_df is None or fixtures_df.empty:
        return []

    rows = []
    for _, row in fixtures_df.iterrows():
        rows.append({
            'fixture_id': '' if pd.isna(row.get('fixture_id')) else str(row.get('fixture_id')).strip(),
            'item_name': '' if pd.isna(row.get('item_name')) else str(row.get('item_name')).strip(),
            'scope': '' if pd.isna(row.get('scope')) else str(row.get('scope')).strip(),
            'fixture_type': '' if pd.isna(row.get('fixture_type')) else str(row.get('fixture_type')).strip(),
            'enabled': normalize_bool(row.get('enabled')),
            'suppress_unmatched': normalize_bool(row.get('suppress_unmatched')),
            'suppress_alert': normalize_bool(row.get('suppress_alert')),
            'expected_state': '' if pd.isna(row.get('expected_state')) else str(row.get('expected_state')).strip(),
            'notes': '' if pd.isna(row.get('notes')) else str(row.get('notes')).strip(),
        })
    return rows


def find_unmatched_items(
    home_df,
    config_df,
    fixture_flags=None,
    enabled_fixture_names=None,
    hide_enabled_fixtures=False,
):
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
        if hide_enabled_fixtures and enabled_fixture_names and item_name in enabled_fixture_names:
            continue
        if fixture_flags and fixture_flags.get(item_name, {}).get('suppress_unmatched', False):
            continue

        # Get item type from home dataframe
        home_row = home_df[home_df['item_name_hm'] == item_name]
        item_type = home_row['item_type_hm'].iloc[0] if not home_row.empty else 'file'
        fs_not_in_di.append({
            'item_name': item_name,
            'item_type': item_type
        })

    di_not_in_fs = []
    for item_name in sorted(di_not_in_fs_names):
        if hide_enabled_fixtures and enabled_fixture_names and item_name in enabled_fixture_names:
            continue
        if fixture_flags and fixture_flags.get(item_name, {}).get('suppress_unmatched', False):
            continue

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
