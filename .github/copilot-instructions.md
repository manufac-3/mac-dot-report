# mac-dot-report AI Assistant Instructions

## Project Overview
This is a Python data processing pipeline that generates categorized reports about macOS dotfiles and folders in a user's home directory. It scans `~/.`, merges with configuration data, and produces timestamped markdown/CSV reports.

## Architecture & Data Flow
- **Entry Point**: `main.py` → `build_full_output_dict()` → `save_outputs()`
- **Core Pipeline**: Load data sources → Merge into main dataframe → Build report dataframe → Generate outputs
- **Key Modules**:
  - `db0_load/`: Data ingestion (home dir, config CSV, repo files, dotbot YAML)
  - `db1_main_df/`: Dataframe merging and consolidation
  - `db2_rep_df/`: Report formatting and filtering
  - `db5_global/`: Shared utilities and type definitions

## Critical Patterns & Conventions

### Data Types & Validation
- Use explicit pandas dtypes from `db5_global/db52_dtype_dict.py`
- String fields: `'string'` dtype (nullable)
- Integer IDs: `'Int64'` dtype (nullable)
- Boolean flags: `'bool'` dtype
- Always handle NaN values explicitly with `.fillna()`

### DataFrame Merging
```python
# Example pattern from db13_merge.py
main_df = pd.merge(main_df, other_df, 
                   left_on='item_name_rp', 
                   right_on='item_name_hm',
                   how='outer',
                   suffixes=('_rp', '_hm'))
```

### Output Generation
- Reports saved to hardcoded iCloud paths (modify `report_gen.py` USER_PATH_* variables)
- Timestamped filenames: `YYMMDD-HHMMSS_mac-dot-report.{md,csv}`
- Jinja2 templating in `data/report_md.jinja2`
- Folders denoted with `**bold**` and `(ƒ)` in markdown

### Configuration Management
- `data/dotrep_config.csv`: Primary config with columns:
  - `item_name_rp_cf`/`item_name_hm_cf`: Repo/home item names
  - `cat_1_cf`/`cat_1_name_cf`: Primary categorization
  - `cat_2_cf`: Secondary categorization
  - `comment_cf`: Descriptive comments
  - `no_show_cf`: Hide from reports

## Developer Workflows

### Running the Project
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py

# Or install as package and use console script
pip install -e .
dotreport
```

### Adding New Dotfile Categories
1. Edit `data/dotrep_config.csv`
2. Add row with appropriate `cat_1_cf`, `cat_1_name_cf`, `cat_2_cf`
3. Set `item_name_hm_cf` for home directory items
4. Run report to see new categorization

### Debugging Data Issues
- Enable debug prints in loaders: Set `show_output = True` in `db0_load/db*.py`
- Check merge results: Uncomment prints in `db1_main_df/db13_merge.py`
- Validate dtypes: Use `df.dtypes` and compare with `f_types_vals`

### Testing Data Changes
- No automated tests currently - validate manually by running reports
- Check "Unmatched Items" sections in output for new/removed dotfiles
- Verify categorization in generated markdown

## Key Files to Reference
- `data/dotrep_config.csv`: Configuration schema and examples
- `data/report_md.jinja2`: Report template structure
- `db5_global/db52_dtype_dict.py`: All pandas dtypes used
- `db1_main_df/db13_merge.py`: Complex merge logic patterns
- `report_gen.py`: Output path configuration

## Common Gotchas
- Output paths hardcoded to iCloud - modify for local development
- Pandas nullable dtypes (`Int64`, `string`) require explicit NaN handling
- Merge suffixes (`_rp`, `_hm`, `_cf`) used throughout for column disambiguation
- Symlinks treated as regular files by `os` library (intended behavior)</content>
<parameter name="filePath">/Users/stevenbrown/swd_storage/VCS_loc_gh/gh_loc_5_tech/macos_scripts_pub/macOS_util_py_rep_mac-dot-report/.github/copilot-instructions.md