import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "") # Parent dir where csv is
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
OUTPUT_DIR_CSV = os.path.join(OUTPUT_DIR, "csvs")
OUTPUT_DIR_IMG = os.path.join(OUTPUT_DIR, "pngs")
INPUT_FILE = os.path.join(DATA_DIR, "jobs_monthly_2020_2025.csv")
MAPPING_FILE = os.path.join(DATA_DIR, "ESCO_skiils_mapping.csv")

# Analysis Parameters
MIN_COOCCURRENCE = 10  # Minimum times two skills must appear together to form an edge
MIN_SUPPORT = 0.1      # Minimum support for association rules (0.1 = 10%)
MIN_CONFIDENCE = 0.3   # Minimum confidence for association rules
MIN_LIFT = 1.2         # Minimum lift for association rules ( > 1 implies positive correlation)

# Date Range (for filtering if needed, though file is already filtered)
START_DATE = "2024-01-01"
END_DATE = "2025-11-27"

# Visualization
PLOT_DPI = 300
