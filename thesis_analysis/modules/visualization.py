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
    pos = nx.spring_layout(G, k=0.15, iterations=20)
    node_sizes = [G.nodes[n].get('frequency', 1) * 0.1 for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='skyblue', alpha=0.7)
    
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    
    nx.draw_networkx_labels(G, pos, font_size=8)
    
    plt.title(title)
    plt.axis('off')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_filtered_network(G, output_path, title="Core Skill Network", k_core=None, min_weight=None, top_n=None):
    """
    Plots a filtered version of the network to reduce clutter (The 'Hairball' problem).
    Supports K-Core, Min Weight, and Top-N filtering.
    """
    print(f"Plotting filtered network to {output_path}...")
    
    H = G.copy()
    
    if k_core:
        print(f"  Applying k-core decomposition (k={k_core})...")
        H = nx.k_core(H, k=k_core)
        
    if min_weight:
        print(f"  Filtering edges with weight < {min_weight}...")
        edges_to_remove = [(u, v) for u, v, d in H.edges(data=True) if d.get('weight', 0) < min_weight]
        H.remove_edges_from(edges_to_remove)
        
    if top_n:
        print(f"  Keeping top {top_n} nodes by centrality...")
        node_degrees = dict(H.degree(weight='weight'))
        top_nodes = sorted(node_degrees, key=node_degrees.get, reverse=True)[:top_n]
        H = H.subgraph(top_nodes).copy()
        
    H.remove_nodes_from(list(nx.isolates(H)))
        
    if H.number_of_nodes() == 0:
        print("  Warning: Filtering removed all nodes. Skipping plot.")
        return

    if H.number_of_nodes() == 0:
        print("  Warning: Filtering removed all nodes. Skipping plot.")
        return

    plt.figure(figsize=(20, 20))
    pos = nx.spring_layout(H, k=0.5, iterations=50, seed=42)
    
    degrees = [H.degree(n, weight='weight') for n in H.nodes()]
    max_deg = max(degrees) if degrees else 1
    node_sizes = [300 + (d / max_deg) * 2000 for d in degrees]
    
    nx.draw_networkx_nodes(H, pos, node_size=node_sizes, node_color='#66b3ff', alpha=0.9, edgecolors='white')
    nx.draw_networkx_edges(H, pos, alpha=0.15, edge_color='#555555')
    
    bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.8)
    nx.draw_networkx_labels(H, pos, font_size=10, font_family='sans-serif', bbox=bbox_props)
    
    
    plt.title(f"{title}\n(Nodes: {H.number_of_nodes()}, Edges: {H.number_of_edges()})")
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
            
            sns.lineplot(data=global_df, x='period', y=metric, marker='o', alpha=0.4, label=f'Monthly {metric}')
            
            global_df[f'{metric}_rolling'] = global_df[metric].rolling(window=3, center=True).mean()
            sns.lineplot(data=global_df, x='period', y=f'{metric}_rolling', linewidth=3, label=f'3-Month Avg {metric}')
            
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
    
    sns.lineplot(data=convergence_df, x='period', y='jaccard_similarity', marker='o', color='green', alpha=0.4, label='Monthly Jaccard')
    
    convergence_df['jaccard_rolling'] = convergence_df['jaccard_similarity'].rolling(window=3, center=True).mean()
    sns.lineplot(data=convergence_df, x='period', y='jaccard_rolling', linewidth=3, color='darkgreen', label='3-Month Moving Average')
    
    plt.title('Skill Set Stability (Jaccard Similarity) over Time')
    plt.ylabel('Jaccard Similarity (0-1)')
    plt.xlabel('Period')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'convergence_jaccard.png'), dpi=300)
    plt.close()

    # Plot Rank Correlation
    plt.figure(figsize=(12, 6))
    
    sns.lineplot(data=convergence_df, x='period', y='rank_correlation_degree', marker='o', color='purple', alpha=0.4, label='Degree (Monthly)')
    convergence_df['rank_degree_rolling'] = convergence_df['rank_correlation_degree'].rolling(window=3, center=True).mean()
    sns.lineplot(data=convergence_df, x='period', y='rank_degree_rolling', linewidth=3, color='purple', label='Degree (3-Month Avg)')

    if 'rank_correlation_betweenness' in convergence_df.columns:
        sns.lineplot(data=convergence_df, x='period', y='rank_correlation_betweenness', marker='s', color='orange', alpha=0.4, label='Betweenness (Monthly)')
        convergence_df['rank_bet_rolling'] = convergence_df['rank_correlation_betweenness'].rolling(window=3, center=True).mean()
        sns.lineplot(data=convergence_df, x='period', y='rank_bet_rolling', linewidth=3, color='orange', label='Betweenness (3-Month Avg)')
    
    plt.title('Skill Ranking Stability (Spearman Correlation) over Time')
    plt.ylabel('Rank Correlation (-1 to 1)')
    plt.xlabel('Period')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'convergence_correlation.png'), dpi=300)
    plt.close()

def plot_job_distribution(df, output_path):
    """
    Plots the number of job postings per month.
    """
    print(f"Plotting job distribution to {output_path}...")
    
    if 'upload_date' not in df.columns:
        print("Error: 'upload_date' not in DataFrame.")
        return

    temp_df = df.copy()
    temp_df['period'] = temp_df['upload_date'].dt.to_period('M').astype(str)
    
    counts = temp_df.groupby('period').size().reset_index(name='count')
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=counts, x='period', y='count', color='steelblue')
    
    plt.title('Number of Job Postings per Month')
    plt.xlabel('Period')
    plt.ylabel('Number of Jobs')
    plt.xticks(rotation=45)
    plt.axhline(y=counts['count'].mean(), color='r', linestyle='--', label=f'Average ({int(counts["count"].mean())})')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_common_skills_trend(convergence_df, output_dir):
    """
    Plots the raw count of common skills between consecutive time periods.
    """
    print("Plotting common skills trend...")
    
    if 'common_skills_count' not in convergence_df.columns:
        print("Error: 'common_skills_count' not in DataFrame.")
        return

    plt.figure(figsize=(12, 6))
    
    sns.lineplot(data=convergence_df, x='period', y='common_skills_count', marker='o', color='teal', alpha=0.6, label='Common Skills Count')
    
    if len(convergence_df) > 4:
        convergence_df['common_rolling'] = convergence_df['common_skills_count'].rolling(window=3, center=True).mean()
        sns.lineplot(data=convergence_df, x='period', y='common_rolling', linewidth=3, color='darkslategrey', label='3-Month Moving Average')
    
    plt.title('Number of Common Skills (Overlapping Nodes) between Consecutive Months')
    plt.xlabel('Period')
    plt.ylabel('Count of Common Skills')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'convergence_common_nodes_count.png'), dpi=300)
    plt.close()
