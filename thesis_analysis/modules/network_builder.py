import pandas as pd
import networkx as nx
from itertools import combinations
from collections import Counter

def build_cooccurrence_matrix(df, min_weight=1):
    """
    Generates a co-occurrence DataFrame from the 'skills_list' column.
    """
    print("Building co-occurrence matrix...")
    pair_counts = Counter()
    
    skill_counts = Counter()

    for skills in df['skills_list']:
        # Sort skills to ensure (A, B) is same as (B, A)
        sorted_skills = sorted(skills)
        
        skill_counts.update(sorted_skills)
        
        for pair in combinations(sorted_skills, 2):
            pair_counts[pair] += 1

    co_occurrence_data = []
    for (skill_i, skill_j), weight in pair_counts.items():
        if weight >= min_weight:
            co_occurrence_data.append({
                'skill_i': skill_i,
                'skill_j': skill_j,
                'weight': weight
            })
            
    co_occurrence_df = pd.DataFrame(co_occurrence_data)
    
    skills_df = pd.DataFrame.from_dict(skill_counts, orient='index', columns=['frequency']).reset_index()
    skills_df.rename(columns={'index': 'skill'}, inplace=True)
    
    print(f"Generated {len(co_occurrence_df)} edges and {len(skills_df)} nodes.")
    return co_occurrence_df, skills_df

def build_graph(co_occurrence_df, skills_df):
    """
    Builds a NetworkX graph from the co-occurrence DataFrame.
    """
    print("Building NetworkX graph...")
    G = nx.Graph()
    
    for _, row in skills_df.iterrows():
        G.add_node(row['skill'], frequency=row['frequency'])
        
    for _, row in co_occurrence_df.iterrows():
        G.add_edge(row['skill_i'], row['skill_j'], weight=row['weight'])
        
    print(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    return G

