# mac-dot-report AI Assistant Instructions

## Project Purpose
This project builds a report about root-level dot items in `$HOME` by combining:

- filesystem home scan (`hm`)
- dotfiles repo scan (`rp`)
- Dotbot YAML mapping scan (`db`)
- user config scan (`cf`)

Output is markdown + CSV with timestamped filenames.

## Architecture
Entry path:

- `main.py` -> `build_full_output_dict()` -> `save_outputs()`

Core packages:

- `db0_load/`: loaders for repo/home/yaml/config
- `db1_main_df/`: merge + consolidated main dataframe
- `db2_rep_df/`: report fields, matching, sorting, final display dataframe
- `db5_global/`: dtype dictionary and shared helpers
- `data/report_md.jinja2`: markdown template

## Current Dotfiles Model Assumptions
Repo loader currently expects:

- public repo: `~/._dotfiles/dotfiles_srb_repo`
- private repo: `~/._dotfiles/dotfiles_srb_repo_private`

Note:

- Dot item name collisions across public/private repos are treated as errors.

## Dtype and Null Rules
- Keep all dataframe dtypes aligned with `db5_global/db52_dtype_dict.py`.
- Use pandas nullable types where defined (`string`, `Int64`, etc.).
- Handle missing values explicitly (`fillna`) before comparisons/sorting.

## Sorting and Presentation Rules
- Baseline ordering comes from config row order (`sort_orig` from `data/dotrep_config.csv`).
- Report-level sorting can add presentation keys (for example `nosym_sort`) but should preserve user-configured order within buckets.
- Markdown rendering must prioritize readability over exhaustive inline metadata.

## Output Paths
- Output directory is controlled by `SRB_REPORTS_DIR` with fallback to `./_output` (see `report_gen.py`).
- Do not reintroduce hardcoded absolute output paths.

## Editing Guidance
- Prefer focused changes in the smallest relevant module.
- When changing report semantics, update `README.md` accordingly.
- For behavioral changes, run `python main.py` and validate:
  - generated markdown
  - generated report CSV
  - unmatched sections
  - expected state/sort behavior

## Typical Local Run
```bash
python main.py
```

Or:

```bash
.venv/bin/python main.py
```
