# Skill Convergence Analysis

This project aims to analyze the convergence of skills in job postings over time (2024-2025). It includes a data collection pipeline and a modular analysis framework.

## Project Structure

- **`take_jobs.py`**: The main data collection script. It fetches job postings from the API month-by-month.
- **`thesis_analysis/`**: A Python package containing the analysis modules.
    - `main.py`: The entry point for running the analysis pipeline.
    - `config.py`: Configuration settings (paths, parameters).
    - `modules/`:
        - `network_builder.py`: Builds skill co-occurrence networks.
        - `analysis.py`: Calculates network metrics (centrality, communities).
        - `association_rules.py`: Mines association rules (Apriori).
        - `visualization.py`: Generates plots.
- **Data Files**:
    - `jobs_monthly_2024_2025.csv`: Raw collected job data.
    - `thesis_dataset_cleaned_monthly.csv`: Cleaned dataset used for analysis.

## Setup

1.  Ensure you have Python installed.
2.  Install dependencies:
    ```bash
    pip install pandas requests networkx matplotlib seaborn mlxtend python-louvain
    ```

## Usage

### 1. Data Collection
To collect new data or update the dataset:
```bash
python take_jobs.py
```
This script will fetch 2000 jobs for each month from Jan 2024 to Nov 2025 and save them to `jobs_monthly_2024_2025.csv` and `thesis_dataset_cleaned_monthly.csv`.

### 2. Analysis
To run the analysis pipeline:
```bash
python -m thesis_analysis.main
```
This will:
1.  Load the cleaned dataset.
2.  Build the skill network.
3.  Calculate centrality and community metrics.
4.  Mine association rules.
5.  Generate visualizations in the `thesis_analysis/output/` directory.

## Analysis Modules

- **Network Analysis**: Nodes represent skills, and edges represent co-occurrence in job postings.
- **Centrality**: Identifies the most important skills (Degree, Betweenness, etc.).
- **Communities**: Groups skills into clusters (e.g., "Data Science", "Web Development").
- **Association Rules**: Finds strong relationships between skills (e.g., "SQL -> Python").

## Future Work (Planned)
- Temporal Analysis: Tracking network evolution month-over-month.
- Convergence Metrics: Measuring how skill sets are converging or diverging over time.
