import pandas as pd
import ast
from datetime import datetime

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

    # Drop rows with missing skills
    df = df.dropna(subset=['skills'])

    # Parse 'skills' column from string representation of list to actual list
    # Example format: "['http://data.europa.eu/esco/skill/123', ...]"
    def parse_skills(skill_str):
        try:
            # If it's already a list (rare in CSV read), return it
            if isinstance(skill_str, list):
                return skill_str
            # Safely evaluate the string literal
            return ast.literal_eval(skill_str)
        except (ValueError, SyntaxError):
            return []

    df['skills_list'] = df['skills'].apply(parse_skills)

    # Filter out jobs with empty skills list
    df = df[df['skills_list'].map(len) > 0]

    # Parse dates
    if 'upload_date' in df.columns:
        df['upload_date'] = pd.to_datetime(df['upload_date'], errors='coerce')

    print(f"Loaded {len(df)} jobs with valid skills.")
    return df
