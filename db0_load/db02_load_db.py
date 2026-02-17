import os
import pandas as pd
from db1_main_df.db14_merge_sup import get_next_unique_id
from db5_global.db52_dtype_dict import f_types_vals


def infer_repo_scope_from_source(src_path_token):
    """Infer source repo scope from Dotbot source path."""
    if "dotfiles_srb_repo_private" in src_path_token:
        return "private"
    if "dotfiles_srb_repo" in src_path_token:
        return "public"
    return "local"


def load_dotbot_yaml_dataframe():
    dotbot_yaml_path = os.path.join(os.path.expanduser("~"), "._dotfiles/dotfiles_srb_repo/install.conf.yaml")
    dotbot_entries = []

    with open(dotbot_yaml_path, 'r') as file:
        for line in file:

            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and full-line comments
                # Split the line into destination and source paths
                parts = line.split(':', 1)
                if len(parts) == 2:
                    dst, src = parts
                    dst = dst.strip()
                    src = src.strip()

                    # Ensure src is not empty before attempting to process it
                    if src:
                        src_path_token = src.split()[0]
                        # Determine the actual types for both destination and source (repo and home)
                        item_type_home = 'folder_sym' if '# folder' in src else 'file_sym'  # Symlink in Home
                        item_type_repo = 'folder' if item_type_home == 'folder_sym' else 'file'  # Actual type in Repo
                        repo_scope_db = infer_repo_scope_from_source(src_path_token)

                        # Extract just the file or folder name from the paths
                        name_dst = os.path.basename(dst)
                        name_src = os.path.basename(src_path_token)

                        dotbot_entries.append({
                            'item_name_hm_db': name_dst,  # Destination in the Home folder (symlink)
                            'item_name_rp_db': name_src,  # Source from the Repo folder
                            'item_type_hm_db': item_type_home,  # Type for Home (symlink)
                            'item_type_rp_db': item_type_repo,  # Type for Repo (actual item)
                            'repo_scope_db': repo_scope_db,
                            'unique_id_db': get_next_unique_id(),  # Assign a unique ID
                        })

    # Create the DataFrame with both home and repo item names and types
    dotbot_yaml_df = pd.DataFrame(dotbot_entries, columns=[
        'item_name_hm_db', 'item_name_rp_db', 'item_type_hm_db', 'item_type_rp_db', 'repo_scope_db', 'unique_id_db']).copy()

    # Add the new merge key column
    dotbot_yaml_df['item_name_db_m_key'] = dotbot_yaml_df.apply(
        lambda row: row['item_name_rp_db'] if pd.notna(row['item_name_rp_db']) and row['item_name_rp_db'] else row['item_name_hm_db'], axis=1
    )

    # Explicitly set data types using the f_types_vals dictionary
    dotbot_yaml_df["item_name_hm_db"] = dotbot_yaml_df["item_name_hm_db"].astype(f_types_vals["item_name_hm_db"]['dtype'])
    dotbot_yaml_df["item_name_rp_db"] = dotbot_yaml_df["item_name_rp_db"].astype(f_types_vals["item_name_rp_db"]['dtype'])
    dotbot_yaml_df["item_type_hm_db"] = dotbot_yaml_df["item_type_hm_db"].astype(f_types_vals["item_type_hm_db"]['dtype'])
    dotbot_yaml_df["item_type_rp_db"] = dotbot_yaml_df["item_type_rp_db"].astype(f_types_vals["item_type_rp_db"]['dtype'])
    dotbot_yaml_df["repo_scope_db"] = dotbot_yaml_df["repo_scope_db"].astype(f_types_vals["repo_scope_db"]['dtype'])
    dotbot_yaml_df["unique_id_db"] = dotbot_yaml_df["unique_id_db"].astype(f_types_vals["unique_id_db"]['dtype'])
    dotbot_yaml_df["item_name_db_m_key"] = dotbot_yaml_df["item_name_db_m_key"].astype(f_types_vals["item_name_rp_db"]['dtype'])

    # Input dataframe display toggle
    show_output = False  # Change to False to disable output
    show_full_df = False  # Change to True to show the full DataFrame

    if show_output:
        if show_full_df:
            print("6️⃣ DotBot DataFrame:\n", dotbot_yaml_df)
        else:
            print("6️⃣ DotBot DataFrame (First 5 rows):\n", dotbot_yaml_df.head())

    return dotbot_yaml_df
