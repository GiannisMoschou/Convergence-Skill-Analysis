import pandas as pd
import networkx as nx
import community.community_louvain as community_louvain

def calculate_centrality(G):
    """
    Calculates various centrality measures for the graph.
    """
    print("Calculating centrality metrics...")
    
    degree = nx.degree_centrality(G)
    
    strength = dict(G.degree(weight='weight'))
    

    betweenness = nx.betweenness_centrality(G, weight='weight')
    
    closeness = nx.closeness_centrality(G)
    
    try:
        eigenvector = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
    except nx.PowerIterationFailedConvergence:
        print("Eigenvector centrality failed to converge.")
        eigenvector = {node: 0 for node in G.nodes()}

    centrality_df = pd.DataFrame({
        'skill': list(G.nodes()),
        'degree_centrality': [degree.get(n, 0) for n in G.nodes()],
        'weighted_degree': [strength.get(n, 0) for n in G.nodes()],
        'betweenness_centrality': [betweenness.get(n, 0) for n in G.nodes()],
        'closeness_centrality': [closeness.get(n, 0) for n in G.nodes()],
        'eigenvector_centrality': [eigenvector.get(n, 0) for n in G.nodes()]
    })
    
    return centrality_df

def detect_communities(G):
    """
    Detects communities using the Louvain method.
    """
    print("Detecting communities (Louvain)...")
    partition = community_louvain.best_partition(G, weight='weight')
    
    community_df = pd.DataFrame(list(partition.items()), columns=['skill', 'community_id'])
    
    # Calculate community stats
    community_stats = community_df.groupby('community_id').size().reset_index(name='size')
    
    return community_df, community_stats

def global_network_stats(G):
    """
    Calculates global network statistics.
    """
    print("Calculating global network stats...")
    stats = {
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'average_clustering': nx.average_clustering(G, weight='weight'),
        'connected_components': nx.number_connected_components(G)
    }
    return stats
