import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "") # Parent dir where csv is
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
INPUT_FILE = os.path.join(DATA_DIR, "thesis_dataset_cleaned_monthly.csv")

# Analysis Parameters
MIN_COOCCURRENCE = 10  # Minimum times two skills must appear together to form an edge
MIN_SUPPORT = 0.05     # Minimum support for association rules (0.05 = 5%)
MIN_CONFIDENCE = 0.3   # Minimum confidence for association rules

# Date Range (for filtering if needed, though file is already filtered)
START_DATE = "2024-01-01"
END_DATE = "2025-11-27"

# Visualization
PLOT_DPI = 300
