import os
import sys
import pandas as pd
from thesis_analysis import config
from thesis_analysis.modules import data_loader, network_builder, analysis, association_rules, visualization

def main():
    print("Starting Skill Network Analysis Pipeline...")
    
    # Ensure output directory exists
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    # 1. Load Data
    df = data_loader.load_and_clean_data(config.INPUT_FILE)
    if df.empty:
        print("No data loaded. Exiting.")
        return

    # 2. Build Network
    co_occurrence_df, skills_df = network_builder.build_cooccurrence_matrix(df, min_weight=config.MIN_COOCCURRENCE)
    G = network_builder.build_graph(co_occurrence_df, skills_df)
    
    # Save intermediate data
    co_occurrence_df.to_csv(os.path.join(config.OUTPUT_DIR, "co_occurrence.csv"), index=False)
    skills_df.to_csv(os.path.join(config.OUTPUT_DIR, "skills_metadata.csv"), index=False)
    
    # 3. Network Analysis
    centrality_df = analysis.calculate_centrality(G)
    community_df, community_stats = analysis.detect_communities(G)
    global_stats = analysis.global_network_stats(G)
    
    # Merge centrality and community info
    full_stats_df = pd.merge(centrality_df, community_df, on='skill', how='left')
    full_stats_df.to_csv(os.path.join(config.OUTPUT_DIR, "node_metrics.csv"), index=False)
    community_stats.to_csv(os.path.join(config.OUTPUT_DIR, "community_stats.csv"), index=False)
    
    # Save global stats
    with open(os.path.join(config.OUTPUT_DIR, "global_stats.txt"), "w") as f:
        for k, v in global_stats.items():
            f.write(f"{k}: {v}\n")

    # 4. Association Rules
    # frequent_itemsets, rules = association_rules.mine_association_rules(
    #     df, 
    #     min_support=config.MIN_SUPPORT, 
    #     min_confidence=config.MIN_CONFIDENCE
    # )
    # if not rules.empty:
    #     rules.to_csv(os.path.join(config.OUTPUT_DIR, "association_rules.csv"), index=False)
    
    # 5. Visualization
    # Only plot if graph is not too huge, or plot a subgraph
    if G.number_of_nodes() < 2000:
        visualization.plot_network(G, os.path.join(config.OUTPUT_DIR, "network_graph.png"))
    else:
        print("Graph too large for full visualization. Skipping full plot.")
        
    visualization.plot_centrality_distribution(full_stats_df, config.OUTPUT_DIR)
    
    print("Analysis complete. Outputs saved to:", config.OUTPUT_DIR)

    # 6. Temporal Analysis (New)
    print("\n--- Starting Temporal Analysis ---")
    from thesis_analysis.modules import temporal
    
    # Build monthly networks
    temporal_networks = temporal.build_temporal_networks(df, interval='M')
    
    # Calculate metrics
    global_stats_df, node_stats_df = temporal.calculate_temporal_metrics(temporal_networks)
    
    # Save temporal data
    global_stats_df.to_csv(os.path.join(config.OUTPUT_DIR, "temporal_global_stats.csv"), index=False)
    node_stats_df.to_csv(os.path.join(config.OUTPUT_DIR, "temporal_node_stats.csv"), index=False)
    
    # Identify emerging skills
    emerging_skills = temporal.detect_emerging_skills(node_stats_df, top_n=10)
    print("\nTop Emerging Skills (by Centrality Growth):")
    print(emerging_skills)
    emerging_skills.to_csv(os.path.join(config.OUTPUT_DIR, "emerging_skills.csv"), index=False)
    
    # Visualization
    visualization.plot_metric_trends(global_stats_df, config.OUTPUT_DIR)
    
    # Plot trajectories for top emerging skills
    # Plot trajectories for top emerging skills
    if not emerging_skills.empty:
        top_skills = emerging_skills['skill'].tolist()
        visualization.plot_skill_trajectories(node_stats_df, top_skills, config.OUTPUT_DIR)

    # 7. Convergence Analysis (New)
    print("\n--- Calculating Convergence Metrics ---")
    convergence_df = temporal.calculate_convergence_metrics(temporal_networks)
    print(convergence_df.head())
    
    convergence_df.to_csv(os.path.join(config.OUTPUT_DIR, "convergence_stats.csv"), index=False)
    visualization.plot_convergence_metrics(convergence_df, config.OUTPUT_DIR)

    print("Temporal analysis complete.")

if __name__ == "__main__":
    main()
