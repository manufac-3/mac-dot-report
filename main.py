import logging
from db1_main_df.db10_make_df_dict import build_full_output_dict
from report_gen import save_outputs

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    # Configuration options
    config = {
        'verbose_output': False,  # Set to True to enable DataFrame debug output
        'save_markdown': True,
        'save_report_csv': True,
        'save_full_csv': False
    }
    
    # Diagnostic: Show resolved output path
    from pathlib import Path
    import os
    reports_dir = os.getenv("SRB_REPORTS_DIR", "./_output")
    print(f"Output directory: {Path(reports_dir).resolve()}")
    
    main_df_dict = build_full_output_dict(verbose=config['verbose_output'])

    # Configuration to control which outputs to save
    save_config = {
        'save_markdown': config['save_markdown'],
        'save_report_csv': config['save_report_csv'],
        'save_full_csv': config['save_full_csv']
    }

    save_outputs(main_df_dict, save_config)

if __name__ == "__main__":
    main()