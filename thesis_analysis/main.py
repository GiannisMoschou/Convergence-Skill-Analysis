import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from thesis_analysis import config
from thesis_analysis.modules import data_loader, pipeline

def main():
    print("Starting Skill Network Analysis Pipeline...")
    
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    # Load Data
    df = data_loader.load_and_clean_data(config.INPUT_FILE)
    if df.empty:
        print("No data loaded. Exiting.")
        return

    # Static Analysis
    pipeline.static_analysis(df)
    
    # Temporal Analysis
    pipeline.temporal_analysis(df)

    print("Pipeline completed. Outputs saved to:", config.OUTPUT_DIR)

if __name__ == "__main__":
    main()
