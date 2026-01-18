import pandas as pd
import ast
import os
from datetime import datetime
from thesis_analysis import config


def load_and_clean_data(filepath):
    """
    Loads the jobs CSV, parses skills, and performs basic cleaning.
    """
    print(f"Loading data from {filepath}...")
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return pd.DataFrame()

    df = df.dropna(subset=['skills'])

    # Parse 'skills' column from string representation of list to actual list
    # Example format: "['http://data.europa.eu/esco/skill/123', ...]"
    def parse_skills(skill_str):
        try:
            if isinstance(skill_str, list):
                return skill_str
            return ast.literal_eval(skill_str)
        except (ValueError, SyntaxError):
            return []

    df['skills_list'] = df['skills'].apply(parse_skills)

    df = df[df['skills_list'].map(len) > 0]

    # Load Mapping `ESCO_skiils_mapping.csv` 
    if os.path.exists(config.MAPPING_FILE):
        print(f"Loading skill mapping from {config.MAPPING_FILE}...")
        try:
            # Load only first two columns: conceptUri, preferredLabel
            # Try utf-8 first, then fallback to latin-1/cp1252 if needed.
            # Given the error 0xa0, it's likely latin-1 or similar.
            try:
                mapping_df = pd.read_csv(config.MAPPING_FILE, sep=';', usecols=[0, 1])
            except UnicodeDecodeError:
                print("Utf-8 decode failed, trying latin-1...")
                mapping_df = pd.read_csv(config.MAPPING_FILE, sep=';', usecols=[0, 1], encoding='latin-1')
            
            # Create dictionary: URI -> Label
            uri_to_name = dict(zip(mapping_df.iloc[:, 0], mapping_df.iloc[:, 1]))
            
            def map_skills(skill_list):
                # Replace URI with Name if exists, otherwise keep URI (or stringify it)
                return [uri_to_name.get(s, s) for s in skill_list]

            df['skills_list'] = df['skills_list'].apply(map_skills)
            print("Applied skill mapping (URIs -> Names).")

        except Exception as e:
            print(f"Warning: Failed to load mapping file: {e}")
    else:
        print(f"Warning: Mapping file not found at {config.MAPPING_FILE}")

    if 'upload_date' in df.columns:
        df['upload_date'] = pd.to_datetime(df['upload_date'], errors='coerce')

    print(f"Loaded {len(df)} jobs with valid skills.")
    
    # Filter to keep only relevant columns
    cols_to_keep = ['skills_list', 'upload_date']
    # Ensure columns exist before selecting to avoid KeyErrors if something went wrong upstream
    cols_to_keep = [c for c in cols_to_keep if c in df.columns]
    df = df[cols_to_keep]
    
    return df
