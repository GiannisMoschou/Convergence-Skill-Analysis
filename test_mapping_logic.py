import sys
import os
import pandas as pd
from thesis_analysis import config

def test_mapping():
    print("Testing Mapping Logic...")
    
    if not os.path.exists(config.MAPPING_FILE):
        print(f"ERROR: Mapping file not found at {config.MAPPING_FILE}")
        return

    print(f"Mapping file found: {config.MAPPING_FILE}")
    
    # Force latin-1 encoding
    try:
        mapping_df = pd.read_csv(config.MAPPING_FILE, sep=';', usecols=[0, 1], encoding='latin-1')
        print(f"Mapping loaded successfully. Rows: {len(mapping_df)}")
        # Check first row
        uri = mapping_df.iloc[0, 0]
        label = mapping_df.iloc[0, 1]
        print(f"Sample mapping: {uri} -> {label}")
        
        uri_to_name = dict(zip(mapping_df.iloc[:, 0], mapping_df.iloc[:, 1]))
        
        # Test Case
        test_uri = 'http://data.europa.eu/esco/skill/7679b863-4d53-4a44-ab2f-be5618783e00'
        # Note: Depending on file content, stripped strings might be needed?
        # Let's strip potential whitespace from loaded keys just in case, though usually CSV reader handles it.
        # But let's check exact match.
        
        mapped_name = uri_to_name.get(test_uri, "NOT_FOUND")
        print(f"Test Look-up: {test_uri}")
        print(f"Result: {mapped_name}")
        
        if mapped_name != "NOT_FOUND" and mapped_name == label:
             print("\nSUCCESS: Mapping verification passed.")
        else:
             print(f"\nFAILURE: Mapping returned {mapped_name}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mapping()
