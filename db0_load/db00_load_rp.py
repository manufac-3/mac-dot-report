import os
import logging
import pandas as pd
import fnmatch

from db1_main_df.db14_merge_sup import get_next_unique_id
from .db05_get_filetype import determine_item_type
from db5_global.db52_dtype_dict import f_types_vals

EXCLUDED_REPO_ITEMS = {".git", ".gitignore", ".DS_Store"}


def get_repo_scope_paths():
    """Return configured repo roots for multi-repo dotfiles scanning."""
    home_dir_path = os.path.expanduser("~")
    return {
        "public": os.path.join(home_dir_path, "._dotfiles/dotfiles_srb_repo"),
        "private": os.path.join(home_dir_path, "._dotfiles/dotfiles_srb_repo_private"),
    }


def load_rp_dataframe():
    repo_items = []
    item_sources = {}
    repo_scope_paths = get_repo_scope_paths()

    for repo_scope, repo_path in repo_scope_paths.items():
        if not os.path.isdir(repo_path):
            logging.info(f"Repo path not found for scope '{repo_scope}': {repo_path}")
            continue

        for item in os.listdir(repo_path):
            if item.startswith("."):
                if item in EXCLUDED_REPO_ITEMS:
                    continue
                item_path = os.path.join(repo_path, item)
                item_type = determine_item_type(item_path)

                item_sources.setdefault(item, set()).add(repo_scope)
                repo_items.append({
                    "item_name_rp": item,
                    "item_type_rp": item_type,
                    "repo_scope_rp": repo_scope,
                    "unique_id_rp": get_next_unique_id(),
                })

    collisions = {
        item_name: sorted(list(scopes))
        for item_name, scopes in item_sources.items()
        if len(scopes) > 1
    }
    if collisions:
        lines = ["Dot item name collision across repos:"]
        for item_name in sorted(collisions):
            lines.append(f"- {item_name}: {', '.join(collisions[item_name])}")
        raise ValueError("\n".join(lines))

    df = pd.DataFrame(
        repo_items,
        columns=["item_name_rp", "item_type_rp", "repo_scope_rp", "unique_id_rp"],
    ).copy()

    # Explicitly set data types.
    df["item_name_rp"] = df["item_name_rp"].astype(f_types_vals["item_name_rp"]['dtype'])
    df["item_type_rp"] = df["item_type_rp"].astype(f_types_vals["item_type_rp"]['dtype'])
    df["repo_scope_rp"] = df["repo_scope_rp"].astype(f_types_vals["repo_scope_rp"]['dtype'])
    df["unique_id_rp"] = df["unique_id_rp"].astype(f_types_vals["unique_id_rp"]['dtype'])

    # Create the git_rp column based on each repo's .gitignore.
    df = create_git_rp_column(df, repo_scope_paths)

    # Input dataframe display toggle
    show_output = False
    show_full_df = False

    return df

def create_git_rp_column(df, repo_scope_paths):
    # Retrieve .gitignore patterns per repo scope.
    gitignore_items_by_scope = {}
    for repo_scope, repo_path in repo_scope_paths.items():
        gitignore_items_by_scope[repo_scope] = read_gitignore_items(repo_path)

    # Iterate through every item in the DataFrame and compare against scope-specific .gitignore items.
    for idx, row in df.iterrows():
        item_name = row['item_name_rp']
        item_type = row['item_type_rp']
        repo_scope = row.get('repo_scope_rp')

        # Initialize the git_rp column with True (assuming it's tracked).
        df.at[idx, 'git_rp'] = True

        # Compare with the corresponding scope's .gitignore patterns.
        gitignore_items = gitignore_items_by_scope.get(repo_scope, {})
        for pattern, pattern_type in gitignore_items.items():
            # Use fnmatch to compare names and types.
            if fnmatch.fnmatch(item_name, pattern) and item_type == pattern_type:
                df.at[idx, 'git_rp'] = False
                break

    df['git_rp'] = df['git_rp'].astype(f_types_vals["git_rp"]['dtype'])

    return df


def read_gitignore_items(repo_path):
    gitignore_path = os.path.join(repo_path, ".gitignore")
    if not os.path.exists(gitignore_path):
        return {}

    gitignore_items = {}

    with open(gitignore_path, 'r') as f:
        for line in f:
            pattern = line.strip()
            if not pattern or pattern.startswith('#'):
                continue

            # Remove leading and trailing slashes for comparison purposes
            pattern_cleaned = pattern.lstrip('/').rstrip('/')

            # Determine type based on whether it had a trailing slash originally
            item_type = 'folder' if pattern.endswith('/') else 'file'

            # Store the cleaned pattern and its type
            gitignore_items[pattern_cleaned] = item_type

    return gitignore_items
