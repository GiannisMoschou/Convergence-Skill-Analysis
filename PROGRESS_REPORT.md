# Thesis Analysis Progress Report
**Date:** December 6, 2025  
**Subject:** Status of Skill Convergence Analysis Pipeline

## 1. Project Objective
The objective of this project is to perform a **Skill Convergence Analysis** on job posting data from January 2024 to November 2025. The analysis tracks how skills co-occur, form clusters, and evolve over time, providing quantitative evidence of how different technical domains are merging or diverging.

## 2. Implementation Status
A modular Python analysis pipeline (`thesis_analysis`) has been implemented and successfully executed.

### 2.1 Data Pipeline
*   **Collection**: Automated script (`take_jobs.py`) retrieves 2,000 job postings per month from the OJA API.
*   **Preprocessing**: Data is aggregated into `thesis_dataset_cleaned_monthly.csv` with temporal markers.

### 2.2 Network Analysis Framework
We utilize a Graph Theory approach where **Nodes=Skills** and **Edges=Co-occurrence**.
*   **Topology Analysis**: Calculation of Network Density, Average Clustering Coefficient.
*   **Centrality Measures**: 
    *   *Degree Centrality*: Identifying most popular skills.
    *   *Betweenness Centrality*: Identifying "bridge" skills connecting different domains.
*   **Community Detection**: Using the Louvain method to detect distinct skill clusters (e.g., AI, Web, DevOps).

### 2.3 Temporal & Convergence Analysis
New modules have been added to track evolution month-over-month:
*   **Trend Analysis**: Plotting the trajectory of network density and edge counts.
*   **Emerging Skills**: algorithmically identifying skills with the highest growth in centrality.
*   **Convergence Metrics**: finding the *Jaccard Similarity* and *Rank Correlation* of top skills between time steps to quantify stability vs. change.

## 3. Current Findings (Preliminary)
Based on the latest run of the pipeline:

### 3.1 Network Overview
*   **Total Unique Skills Analyzed**: 537
*   **Co-occurrence Connections**: 23,309
*   **Network Density**: 0.162 (16.2% of all possible skill pairs are connected)
*   **Clustering Coefficient**: 0.007 (indicating loose, broad connections rather than tight cliques at the global level)

### 3.2 Key Artifacts Generated
The following outputs are available for review in `thesis_analysis/output/`:

#### Visualizations
*   `network_graph.png`: Force-directed layout of the entire skill network.
*   `trajectory_degree.png`: Line charts showing the rise/fall of top emerging skills.
*   `convergence_jaccard.png`: Plot illustrating how much skill demand overlaps between months.
*   `dist_degree_centrality.png`: Distribution of skill popularity.

#### Data Tables
*   `emerging_skills.csv`: List of skills with highest recent growth.
*   `temporal_global_stats.csv`: Month-by-month network statistics.
*   `association_rules.csv`: (Generated but excluded from git due to size) Strong skill implications (e.g., If Skill A -> Then Skill B).

## 4. Next Steps
1.  **Label Refinement**: Map ESCO skill URIs to human-readable names in visualizations.
2.  **Qualitative Review**: Select specific "converging" communities for case study.
3.  **Thesis Writing**: Incorporate these graphs and metrics into the methodology and results sections of the thesis document.
