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

def plot_filtered_network(G, output_path, title="Core Skill Network", k_core=None, min_weight=None, top_n=None):
    """
    Plots a filtered version of the network to reduce clutter (The 'Hairball' problem).
    Supports K-Core, Min Weight, and Top-N filtering.
    """
    print(f"Plotting filtered network to {output_path}...")
    
    H = G.copy()
    
    # Filter 1: K-Core (Keep only nodes connected to k other nodes)
    if k_core:
        print(f"  Applying k-core decomposition (k={k_core})...")
        H = nx.k_core(H, k=k_core)
        
    # Filter 2: Min Weight (Keep only strong edges)
    if min_weight:
        print(f"  Filtering edges with weight < {min_weight}...")
        edges_to_remove = [(u, v) for u, v, d in H.edges(data=True) if d.get('weight', 0) < min_weight]
        H.remove_edges_from(edges_to_remove)
        
    # Filter 3: Top N Nodes (by weighted degree)
    if top_n:
        print(f"  Keeping top {top_n} nodes by centrality...")
        # Sort by weighted degree
        node_degrees = dict(H.degree(weight='weight'))
        top_nodes = sorted(node_degrees, key=node_degrees.get, reverse=True)[:top_n]
        H = H.subgraph(top_nodes).copy()
        
    # Remove isolated nodes after filtering
    H.remove_nodes_from(list(nx.isolates(H)))
        
    if H.number_of_nodes() == 0:
        print("  Warning: Filtering removed all nodes. Skipping plot.")
        return

    if H.number_of_nodes() == 0:
        print("  Warning: Filtering removed all nodes. Skipping plot.")
        return

    # Increase canvas size for better readability
    plt.figure(figsize=(20, 20))
    # Increase k (optimal distance) to spread nodes apart
    pos = nx.spring_layout(H, k=0.5, iterations=50, seed=42)
    
    # Scale node size: normalization to avoid huge blobs
    # Base size 100, plus scaled frequency
    degrees = [H.degree(n, weight='weight') for n in H.nodes()]
    max_deg = max(degrees) if degrees else 1
    node_sizes = [300 + (d / max_deg) * 2000 for d in degrees]
    
    nx.draw_networkx_nodes(H, pos, node_size=node_sizes, node_color='#66b3ff', alpha=0.9, edgecolors='white')
    nx.draw_networkx_edges(H, pos, alpha=0.15, edge_color='#555555')
    
    # Add labels with white background for readability
    bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.8)
    nx.draw_networkx_labels(H, pos, font_size=10, font_family='sans-serif', bbox=bbox_props)
    
    
    plt.title(f"{title}\n(Nodes: {H.number_of_nodes()}, Edges: {H.number_of_edges()})")
    plt.axis('off')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_mst_network(G, output_path, title="Maximum Spanning Tree (Backbone)", top_n=None):
    """
    Plots the Maximum Spanning Tree of the graph.
    This reveals the 'skeleton' or strongest paths between skills, ensuring no cycles.
    """
    print(f"Plotting MST to {output_path}...")
    
    H = G.copy()
    
    # Filter if top_n is requested
    if top_n:
        print(f"  Filtering MST input to Top {top_n} skills...")
        node_degrees = dict(H.degree(weight='weight'))
        top_nodes = sorted(node_degrees, key=node_degrees.get, reverse=True)[:top_n]
        H = H.subgraph(top_nodes).copy()
        title = f"{title} (Top {top_n} Skills)"

    # Calculate Maximum Spanning Tree (keeps strongest edges)
    T = nx.maximum_spanning_tree(H, weight='weight')
    
    plt.figure(figsize=(14, 14))
    
    # MST looks usually better with Kamada Kawai or just Spring
    pos = nx.spring_layout(T, k=0.5, iterations=50)
    
    # Node Size
    node_degrees = dict(G.degree(weight='weight')) # Use original graph degree for sizing to show importance
    node_sizes = [node_degrees.get(n, 1) * 0.5 for n in T.nodes()]
    
    # Edge Width by weight
    edge_weights = [T[u][v]['weight'] for u, v in T.edges()]
    # Normalize roughly
    max_w = max(edge_weights) if edge_weights else 1
    width = [ (w / max_w) * 3 for w in edge_weights]
    
    nx.draw_networkx_nodes(T, pos, node_size=node_sizes, node_color='#ffcc99', alpha=0.9)
    nx.draw_networkx_edges(T, pos, width=width, alpha=0.5, edge_color='#666666')
    nx.draw_networkx_labels(T, pos, font_size=9)
    
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
    sns.lineplot(data=convergence_df, x='period', y='rank_correlation_degree', marker='o', label='Degree Centrality', color='purple')
    if 'rank_correlation_betweenness' in convergence_df.columns:
        sns.lineplot(data=convergence_df, x='period', y='rank_correlation_betweenness', marker='s', label='Betweenness Centrality', color='orange')
    
    plt.title('Skill Ranking Stability (Spearman Correlation) over Time')
    plt.ylabel('Rank Correlation (-1 to 1)')
    plt.xlabel('Period')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'convergence_correlation.png'), dpi=300)
    plt.close()
