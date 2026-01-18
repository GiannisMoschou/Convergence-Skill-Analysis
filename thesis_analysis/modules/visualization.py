import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
import os

def plot_network(G, output_path, title="Skill Network"):
    """
    Plots the network graph.
    """
    print(f"Plotting network to {output_path}...")
    plt.figure(figsize=(12, 12))
    
    # Use a layout
    pos = nx.spring_layout(G, k=0.15, iterations=20)
    
    # Draw nodes
    # Size by degree (frequency)
    node_sizes = [G.nodes[n].get('frequency', 1) * 0.1 for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='skyblue', alpha=0.7)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    
    # Draw labels (maybe only for high degree nodes to avoid clutter)
    # For now, drawing all
    nx.draw_networkx_labels(G, pos, font_size=8)
    
    plt.title(title)
    plt.axis('off')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_centrality_distribution(centrality_df, output_dir):
    """
    Plots histograms of centrality measures.
    """
    print("Plotting centrality distributions...")
    
    metrics = ['degree_centrality', 'betweenness_centrality', 'closeness_centrality']
    
    for metric in metrics:
        if metric in centrality_df.columns:
            plt.figure(figsize=(10, 6))
            sns.histplot(centrality_df[metric], kde=True)
            plt.title(f'Distribution of {metric}')
            plt.xlabel(metric)
            plt.ylabel('Count')
            plt.savefig(os.path.join(output_dir, f'dist_{metric}.png'), dpi=300)
            plt.close()

def plot_metric_trends(global_df, output_dir):
    """
    Plots global network metrics over time.
    """
    print("Plotting global metric trends...")
    
    metrics = ['density', 'average_clustering', 'nodes', 'edges']
    
    for metric in metrics:
        if metric in global_df.columns:
            plt.figure(figsize=(12, 6))
            sns.lineplot(data=global_df, x='period', y=metric, marker='o')
            plt.title(f'Evolution of {metric} over Time')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'trend_{metric}.png'), dpi=300)
            plt.close()

def plot_skill_trajectories(node_df, top_skills, output_dir):
    """
    Plots the centrality trajectory of specific skills.
    """
    print("Plotting skill trajectories...")
    
    # Filter for top skills
    subset = node_df[node_df['skill'].isin(top_skills)]
    
    plt.figure(figsize=(14, 8))
    sns.lineplot(data=subset, x='period', y='degree_centrality', hue='skill', marker='o')
    plt.title('Degree Centrality Trajectories of Top Skills')
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'trajectory_degree.png'), dpi=300)
    plt.close()

def plot_convergence_metrics(convergence_df, output_dir):
    """
    Plots convergence metrics over time.
    """
    print("Plotting convergence metrics...")
    
    if convergence_df.empty:
        print("No convergence data to plot.")
        return

    # Plot Jaccard Similarity
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=convergence_df, x='period', y='jaccard_similarity', marker='o', color='green')
    plt.title('Skill Set Stability (Jaccard Similarity) over Time')
    plt.ylabel('Jaccard Similarity (0-1)')
    plt.xlabel('Period')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'convergence_jaccard.png'), dpi=300)
    plt.close()

    # Plot Rank Correlation
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=convergence_df, x='period', y='rank_correlation', marker='o', color='purple')
    plt.title('Skill Ranking Stability (Spearman Correlation) over Time')
    plt.ylabel('Rank Correlation (-1 to 1)')
    plt.xlabel('Period')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'convergence_correlation.png'), dpi=300)
    plt.close()
