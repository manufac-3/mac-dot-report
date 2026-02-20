# mac-dot-report

## Overview
`mac-dot-report` generates a categorized inventory of root-level dot items in `$HOME` and compares four sources of truth:

1. Repo scan (`rp`): dot items in dotfiles repositories.
2. Home scan (`hm`): dot items currently present in `$HOME`.
3. Dotbot YAML (`db`): expected symlink mappings from `install.conf.yaml`.
4. Config CSV (`cf`): user-maintained metadata and ordering in `data/dotrep_config.csv`.

The output is a timestamped markdown report plus a timestamped CSV report.

## Current Model
This project currently supports a two-repo dotfiles model:

- Public repo scope: `~/._dotfiles/dotfiles_srb_repo`
- Private repo scope: `~/._dotfiles/dotfiles_srb_repo_private`

At runtime, scope is represented as:

- `public`
- `private`
- `local`

If the same dot item name exists in both repos, report generation fails with an explicit collision error.

## Config File
Primary config file:

- `data/dotrep_config.csv`
- `data/test_fixtures.csv` (intentional test artifacts + suppression toggles)

The row order in `data/dotrep_config.csv` is intentional and remains the baseline ordering signal.

Key fields:

- `item_name_rp_cf`, `item_name_hm_cf`
- `dot_struc_cf`
- `item_type_rp_cf`, `item_type_hm_cf`
- `cat_1_cf`, `cat_1_name_cf`, `cat_2_cf`
- `comment_cf`
- `repo_scope_cf`
- `no_show_cf`

Test fixture fields (`data/test_fixtures.csv`):

- `fixture_id`, `item_name`, `scope`, `fixture_type`
- `enabled`
- `suppress_unmatched`
- `suppress_alert`
- `expected_state`, `notes`

Fixture visibility behavior:

- Enabled fixture items are hidden from user-facing report output by default.
- This includes managed list rows, unmatched sections, and fixture inventory section.
- To temporarily show fixture inventory in markdown while debugging, run with:
  - `DOTREP_SHOW_TEST_FIXTURES=1 python main.py`

## Output Files
Output directory:

- Uses `$SRB_REPORTS_DIR` if set.
- Falls back to `./_output`.

Generated files:

- `YYMMDD-HHMMSS_mac-dot-report.md`
- `YYMMDD-HHMMSS_mac-dot-report.csv`

Markdown behavior:

- Top line reports unmanaged home-item status explicitly.
- Grouping follows configured categories.
- `NoSym` items are visually distinguished and placed below symlinked items within each subgroup.
- `Test Fixtures` section is shown only when fixture display is explicitly enabled.

CSV behavior:

- Includes operational/report fields in addition to config fields.
- Includes derived fields such as `dot_state` and `nosym_sort` for report presentation logic.
- Uses source-side filesystem fields (`item_name_rp`, `item_type_rp`, `item_name_hm`, `item_type_hm`) as the canonical repo/home representations in output.

## Running
From repo root:

```bash
python main.py
```

If using the project virtual environment:

```bash
.venv/bin/python main.py
```

## Maintenance Workflow
Recommended loop:

1. Run report.
2. Review unmanaged/unmatched sections.
3. Update `data/dotrep_config.csv` for newly accepted items.
4. Update `data/test_fixtures.csv` for intentional test artifacts and suppression policy.
5. Re-run report to confirm grouping, comments, and fixture behavior.

## Scope and Limits
- Scans only root-level dot items in `$HOME`.
- Does not recurse nested dot items for inventory classification.
- Assumes Dotbot-style symlink management for YAML-derived comparisons.
