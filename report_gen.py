import os
import logging
import pandas as pd

from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# Retrieve preferred reports directory (set in ~/.zshrc)
REPORTS_DIR = os.getenv("SRB_REPORTS_DIR", "./_output")

# Ensure the directory exists
Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)

def format_output_path_display(path):
    """Format path for display: show env var name and abbreviated path"""
    env_var = "SRB_REPORTS_DIR" if os.getenv("SRB_REPORTS_DIR") else "./_output"
    path_obj = Path(path)
    return f"{env_var} (.../{path_obj.name})"

# Define input and output paths
USER_CONFIG_CSV_PATH = 'data'
REPORT_TEMPLATE_J2 = 'report_md.jinja2'
OUTPUT_BASE_NAME = "mac-dot-report"

def generate_timestamped_output_paths(base_name):
    timestamp = datetime.now().strftime('%y%m%d-%H%M%S')
    
    markdown_output_path = os.path.join(REPORTS_DIR, f"{timestamp}_{base_name}.md")
    csv_output_path = os.path.join(REPORTS_DIR, f"{timestamp}_{base_name}.csv")
    full_csv_output_path = os.path.join(REPORTS_DIR, f"{timestamp}_{base_name}_FULL_DF.csv")
    
    return csv_output_path, full_csv_output_path, markdown_output_path

# CONVERT DATAFRAMES TO OUTPUT FORMATS
def export_to_markdown(output_file, df=None, fs_not_in_di=None, di_not_in_fs=None):
    try:
        if df is None:
            raise ValueError("DataFrame 'df' must be provided")

        env = Environment(
            loader=FileSystemLoader(USER_CONFIG_CSV_PATH),
            trim_blocks=True,
            lstrip_blocks=True
        )
        env.globals['pd'] = pd

        template = env.get_template(REPORT_TEMPLATE_J2)
        rendered_markdown = template.render(
            csv_data=df.to_dict(orient='records'),
            fs_not_in_di=fs_not_in_di if fs_not_in_di else [],
            di_not_in_fs=di_not_in_fs if di_not_in_fs else []
        )

        with open(output_file, 'w') as file:
            file.write(rendered_markdown)

        logging.info("Markdown report generated")
    except Exception as e:
        logging.error(f"Failed to export DataFrame to Markdown: {e}")

def export_dataframe_to_csv(df, filename, columns=None):
    try:
        df.to_csv(filename, index=False, columns=columns)
        logging.info("DataFrame exported to CSV")
    except Exception as e:
        logging.error(f"Failed to export DataFrame to CSV: {e}")

# SAVE OUTPUTS TO DISK
def save_outputs(main_df_dict, config):
    csv_output_path, full_csv_output_path, markdown_output_path = generate_timestamped_output_paths(OUTPUT_BASE_NAME)

    # Log output directory once instead of spamming with full paths
    logging.info(f"Output directory: {format_output_path_display(REPORTS_DIR)}")

    if config.get('save_markdown', True):
        save_markdown(main_df_dict, markdown_output_path)
    if config.get('save_report_csv', True):
        save_report_csv(main_df_dict, csv_output_path)
    if config.get('save_full_csv', True):
        save_full_csv(main_df_dict, full_csv_output_path)

def save_markdown(main_df_dict, markdown_output_path):
    export_to_markdown(
        output_file=markdown_output_path,
        df=main_df_dict['report_dataframe'],
        fs_not_in_di=main_df_dict.get('fs_not_in_di', []),
        di_not_in_fs=main_df_dict.get('di_not_in_fs', [])
    )

def save_report_csv(main_df_dict, csv_output_path):
    export_dataframe_to_csv(main_df_dict['report_dataframe'], filename=csv_output_path)
    logging.info("Report CSV saved")

def save_full_csv(main_df_dict, full_csv_output_path):
    if 'full_main_dataframe' in main_df_dict:
        export_dataframe_to_csv(main_df_dict['full_main_dataframe'], filename=full_csv_output_path)
        logging.info("Full DataFrame CSV saved")
    else:
        logging.warning("Warning: 'full_main_dataframe' key not found in main_df_dict. Full DataFrame not saved.")