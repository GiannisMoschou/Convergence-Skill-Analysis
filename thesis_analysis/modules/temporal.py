import pandas as pd
import networkx as nx
from thesis_analysis.modules import network_builder, analysis

def build_temporal_networks(df, date_col='upload_date', interval='M'):
    """
    Splits the dataframe by the specified time interval and builds a network for each slice.
    
    Args:
        df (pd.DataFrame): The input dataframe containing job data.
        date_col (str): The name of the date column.
        interval (str): The frequency for slicing (default 'M' for month).
        
    Returns:
        dict: A dictionary where keys are time periods (str) and values are (G, skills_df) tuples.
    """
    print(f"Building temporal networks (interval={interval})...")
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col])
        
    temporal_networks = {}
    
    grouped = df.groupby(pd.Grouper(key=date_col, freq=interval))
    
    # 1. First pass: Determine minimum count across all valid intervals
    counts = []
    valid_groups = []
    
    for time_period, group in grouped:
        if not group.empty:
            counts.append(len(group))
            valid_groups.append((time_period, group))
            
    if not counts:
        print("No valid data found for any interval.")
        return {}
        
    min_count = min(counts)
    print(f"Equalizing job counts per interval. Minimum count found: {min_count}")
    
    # 2. Second pass: Build networks with sampled data
    for time_period, group in valid_groups:
        period_str = time_period.strftime('%Y-%m')
        
        # Sample down to min_count
        if len(group) > min_count:
            sampled_group = group.sample(n=min_count, random_state=42)
        else:
            sampled_group = group
            
        print(f"Processing period: {period_str} (Jobs: {len(sampled_group)} - original: {len(group)})")
        
        # Build network for this slice
        co_occurrence_df, skills_df = network_builder.build_cooccurrence_matrix(sampled_group, min_weight=1)
        
        if co_occurrence_df.empty:
            print(f"  No co-occurrences found for {period_str}")
            continue
            
        G = network_builder.build_graph(co_occurrence_df, skills_df)
        temporal_networks[period_str] = G
        
    return temporal_networks

def calculate_temporal_metrics(temporal_networks):
    """
    Calculates network metrics for each time step.
    
    Args:
        temporal_networks (dict): Dictionary of {period: Graph}.
        
    Returns:
        pd.DataFrame: Global metrics over time.
        pd.DataFrame: Node-level metrics over time (long format).
    """
    print("Calculating temporal metrics...")
    
    global_metrics_list = []
    node_metrics_list = []
    
    for period, G in temporal_networks.items():
        # Global Stats
        stats = analysis.global_network_stats(G)
        stats['period'] = period
        global_metrics_list.append(stats)
        
        # Node Stats (Centrality)
        # We focus on Degree and Betweenness as per papers
        degree = nx.degree_centrality(G)
        betweenness = nx.betweenness_centrality(G, weight='weight')
        
        for node in G.nodes():
            node_metrics_list.append({
                'period': period,
                'skill': node,
                'degree_centrality': degree.get(node, 0),
                'betweenness_centrality': betweenness.get(node, 0),
                'frequency': G.nodes[node].get('frequency', 0)
            })
            
    global_df = pd.DataFrame(global_metrics_list)
    node_df = pd.DataFrame(node_metrics_list)
    
    return global_df, node_df

def detect_emerging_skills(node_df, top_n=10):
    """
    Identifies skills with the highest growth in centrality.
    """
    # Pivot to get skills as columns
    pivot_df = node_df.pivot(index='period', columns='skill', values='degree_centrality').fillna(0)
    
    # Calculate difference between last and first period (or trend slope)
    # Simple approach: Last - First
    if len(pivot_df) < 2:
        return pd.DataFrame()
        
    growth = pivot_df.iloc[-1] - pivot_df.iloc[0]
    emerging = growth.sort_values(ascending=False).head(top_n)
    
    return emerging.reset_index(name='growth')

def calculate_convergence_metrics(temporal_networks):
    """
    Calculates convergence metrics (Jaccard Similarity, Rank Correlation) between consecutive time periods.
    
    Args:
        temporal_networks (dict): Dictionary of {period: Graph}.
        
    Returns:
        pd.DataFrame: Convergence metrics over time.
    """
    print("Calculating convergence metrics...")
    
    periods = sorted(temporal_networks.keys())
    convergence_data = []
    
    for i in range(len(periods) - 1):
        t1 = periods[i]
        t2 = periods[i+1]
        
        G1 = temporal_networks[t1]
        G2 = temporal_networks[t2]
        
        # 1. Jaccard Similarity (Nodes)
        nodes1 = set(G1.nodes())
        nodes2 = set(G2.nodes())
        
        if not nodes1 or not nodes2:
            jaccard = 0
        else:
            intersection = len(nodes1.intersection(nodes2))
            union = len(nodes1.union(nodes2))
            jaccard = intersection / union if union > 0 else 0
            
        # 2. Rank Correlation (Degree Centrality)
        # We only correlate nodes present in BOTH periods to see stability of common skills
        common_nodes = list(nodes1.intersection(nodes2))
        
        if len(common_nodes) > 5: # Need enough points for correlation
            deg1 = nx.degree_centrality(G1)
            deg2 = nx.degree_centrality(G2)
            
            bet1 = nx.betweenness_centrality(G1, weight='weight')
            bet2 = nx.betweenness_centrality(G2, weight='weight')
            
            vec_deg1 = [deg1[n] for n in common_nodes]
            vec_deg2 = [deg2[n] for n in common_nodes]
            
            vec_bet1 = [bet1[n] for n in common_nodes]
            vec_bet2 = [bet2[n] for n in common_nodes]
            
            # Spearman correlation
            from scipy.stats import spearmanr
            corr_deg, _ = spearmanr(vec_deg1, vec_deg2)
            corr_bet, _ = spearmanr(vec_bet1, vec_bet2)
            
            # Handle NaN if constant input
            if pd.isna(corr_deg): corr_deg = 0
            if pd.isna(corr_bet): corr_bet = 0
            
        else:
            corr_deg = 0
            corr_bet = 0
            
        convergence_data.append({
            'period': t2, # Plot against the "next" period
            'jaccard_similarity': jaccard,
            'rank_correlation_degree': corr_deg,
            'rank_correlation_betweenness': corr_bet,
            'common_skills_count': len(common_nodes)
        })
        
    return pd.DataFrame(convergence_data)
