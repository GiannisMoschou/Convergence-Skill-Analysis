import os
import pandas as pd
from thesis_analysis import config
from thesis_analysis.modules import network_builder, analysis, visualization, temporal

def static_analysis(df):
    """
    Performs the static network analysis:
    - Builds the Co-occurrence Network
    - Calculates Centrality & Communities
    - Mines Association Rules (Optional/Commented out)
    - Generates Visualizations
    """
    print("\n--- Starting Static Analysis ---")
    
    # Define Static Output Paths
    static_csv_dir = os.path.join(config.OUTPUT_DIR, "static", "csvs")
    static_img_dir = os.path.join(config.OUTPUT_DIR, "static", "pngs")
    os.makedirs(static_csv_dir, exist_ok=True)
    os.makedirs(static_img_dir, exist_ok=True)

    # Build Network and save
    co_occurrence_df, skills_df = network_builder.build_cooccurrence_matrix(df, min_weight=config.MIN_COOCCURRENCE)
    G = network_builder.build_graph(co_occurrence_df, skills_df)

    co_occurrence_df.to_csv(os.path.join(static_csv_dir, "co_occurrence.csv"), index=False)
    skills_df.to_csv(os.path.join(static_csv_dir, "skills_metadata.csv"), index=False)
    
    # 3. Network Analysis
    centrality_df = analysis.calculate_centrality(G)
    community_df, community_stats = analysis.detect_communities(G)
    global_stats = analysis.global_network_stats(G)
    
    # Merge centrality and community info
    full_stats_df = pd.merge(centrality_df, community_df, on='skill', how='left')
    full_stats_df.to_csv(os.path.join(static_csv_dir, "node_metrics.csv"), index=False)
    community_stats.to_csv(os.path.join(static_csv_dir, "community_stats.csv"), index=False)
    
    # Save global stats
    with open(os.path.join(static_csv_dir, "global_stats.txt"), "w") as f:
        f.write(f"Total Job Postings: {len(df)}\n")
        for k, v in global_stats.items():
            f.write(f"{k}: {v}\n")
    
    # Visualization (Static)
    # Only plot if graph is not too huge, or plot a subgraph
    if G.number_of_nodes() < 2000:
        visualization.plot_network(G, os.path.join(static_img_dir, "network_graph.png"))
        
        # Plot a cleaner version (K-Core)
        # k=5 means a node must be connected to at least 5 others in the core
        visualization.plot_filtered_network(G, os.path.join(static_img_dir, "network_graph_clean.png"), k_core=5)
        
    else:
        print("Graph too large for full visualization. Plotting filtered core only.")
        visualization.plot_filtered_network(G, os.path.join(static_img_dir, "network_graph_clean.png"), k_core=10)

    # Plot: Top 50 Skills
    visualization.plot_filtered_network(G, os.path.join(static_img_dir, "network_graph_top50.png"), 
                                        top_n=50, 
                                        title="Top 50 Skills Network")
        
    visualization.plot_centrality_distribution(full_stats_df, static_img_dir)
    
    print("Static analysis complete. Outputs saved to:", config.OUTPUT_DIR)

def temporal_analysis(df):
    """
    Performs the temporal network analysis:
    - Builds networks per time slice (Month)
    - Calculates Convergence Metrics (Jaccard, Rank Correlation)
    - Identifies Emerging Skills
    """
    print("\n--- Starting Temporal Analysis ---")
    
    # Define Temporal Output Paths
    temporal_csv_dir = os.path.join(config.OUTPUT_DIR, "temporal", "csvs")
    temporal_img_dir = os.path.join(config.OUTPUT_DIR, "temporal", "pngs")
    os.makedirs(temporal_csv_dir, exist_ok=True)
    os.makedirs(temporal_img_dir, exist_ok=True)

    # Build monthly networks
    temporal_networks = temporal.build_temporal_networks(df, interval='M')
    
    # Visualization: Job Distribution
    visualization.plot_job_distribution(df, os.path.join(temporal_img_dir, "job_distribution.png"))
    
    # Calculate metrics
    global_stats_df, node_stats_df = temporal.calculate_temporal_metrics(temporal_networks)
    
    # Save temporal data
    global_stats_df.to_csv(os.path.join(temporal_csv_dir, "temporal_global_stats.csv"), index=False)
    node_stats_df.to_csv(os.path.join(temporal_csv_dir, "temporal_node_stats.csv"), index=False)
    
    # Identify emerging skills
    emerging_skills = temporal.detect_emerging_skills(node_stats_df, top_n=10)
    print("\nTop Emerging Skills (by Centrality Growth):")
    print(emerging_skills)
    emerging_skills.to_csv(os.path.join(temporal_csv_dir, "emerging_skills.csv"), index=False)
    
    # Visualization (Temporal)
    visualization.plot_metric_trends(global_stats_df, temporal_img_dir)
    
    # Plot trajectories for top emerging skills
    if not emerging_skills.empty:
        top_skills = emerging_skills['skill'].tolist()
        visualization.plot_skill_trajectories(node_stats_df, top_skills, temporal_img_dir)

    # Convergence Analysis
    print("\n--- Calculating Convergence Metrics ---")
    convergence_df = temporal.calculate_convergence_metrics(temporal_networks)
    print(convergence_df.head())
    
    print(convergence_df.head())
    
    convergence_df.to_csv(os.path.join(temporal_csv_dir, "convergence_stats.csv"), index=False)
    visualization.plot_convergence_metrics(convergence_df, temporal_img_dir)
    visualization.plot_common_skills_trend(convergence_df, temporal_img_dir)

    print("Temporal analysis complete.")
