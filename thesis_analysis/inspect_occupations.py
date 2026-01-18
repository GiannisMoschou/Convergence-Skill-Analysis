
import pandas as pd
import sys

# File path from config
file_path = r"c:/Users/giann/OneDrive/Υπολογιστής/thesis/jobs_monthly_2024_2025.csv"

try:
    # Read only header first to see columns
    df_head = pd.read_csv(file_path, nrows=0)
    print("Columns found:", df_head.columns.tolist())
    
    # Try to guess occupation column
    target_col = 'occupations'
    if target_col in df_head.columns:
        print(f"Targeting column: {target_col}")
        # Read the file
        df = pd.read_csv(file_path, usecols=[target_col])
        counts = df[target_col].value_counts()
        print(f"\nTotal Records: {len(df)}")
        print(f"Unique Occupations: {len(counts)}")
        print("\nBreakdown:")
        print(counts.to_string())
        
    else:
        print("Could not identify occupation column automatically.")
        
except Exception as e:
    print(f"Error: {e}")
