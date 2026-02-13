import pandas as pd
import os
from thesis_analysis import config


def analyze_results():
    static_csv_dir = os.path.join(config.OUTPUT_DIR, "static", "csvs")
    temporal_csv_dir = os.path.join(config.OUTPUT_DIR, "temporal", "csvs")
    results_dir = os.path.join(config.OUTPUT_DIR, "key_skills")
    os.makedirs(results_dir, exist_ok=True)

    # BRIDGES (High Betweenness Centrality) 
    node_metrics_file = os.path.join(static_csv_dir, "node_metrics.csv")
    if os.path.exists(node_metrics_file):
        df_static = pd.read_csv(node_metrics_file)

        bridges = df_static.sort_values(
            by='betweenness_centrality', ascending=False
        ).head(20)
        print("\n=== Top 20 Bridge Skills (High Betweenness Centrality) ===")
        print("These skills connect different clusters in the network:\n")
        for i, row in bridges.iterrows():
            print(f"  {row['skill']:<45} betweenness={row['betweenness_centrality']:.4f}")
        bridges.to_csv(os.path.join(results_dir, "top_bridges.csv"), index=False)

        # B. Skill Ranks (by weighted degree)
        ranks = df_static.sort_values(
            by='weighted_degree', ascending=False
        ).head(20)
        print("\n=== Top 20 Skill Ranks (Highest Weighted Degree) ===")
        print("These are the most popular/connected skills overall:\n")
        for i, row in ranks.iterrows():
            print(f"  {row['skill']:<45} weighted_degree={row['weighted_degree']:,.0f}")
        ranks.to_csv(os.path.join(results_dir, "top_skill_ranks.csv"), index=False)
    else:
        print(f"Warning: {node_metrics_file} not found. Skipping bridges & ranks.")

    # STABLE SKILLS (Consistent presence over time)
    temporal_file = os.path.join(temporal_csv_dir, "temporal_node_stats.csv")
    if os.path.exists(temporal_file):
        df_temp = pd.read_csv(temporal_file)
        total_months = df_temp['period'].nunique()

        skill_stability = df_temp.groupby('skill').agg(
            months_present=('period', 'count'),
            avg_degree_centrality=('degree_centrality', 'mean'),
            std_degree_centrality=('degree_centrality', 'std'),
            avg_betweenness=('betweenness_centrality', 'mean'),
            avg_frequency=('frequency', 'mean')
        ).reset_index()

        # Fill NaN std (skills with only 1 month get NaN)
        skill_stability['std_degree_centrality'] = skill_stability['std_degree_centrality'].fillna(0)

        # Filter: present in at least 80% of months
        threshold = total_months * 0.8
        stable = skill_stability[skill_stability['months_present'] >= threshold]

        # Sort by lowest volatility (std) while being reasonably important
        # Use coefficient of variation (std/mean) to normalize
        stable = stable.copy()
        stable['cv'] = stable['std_degree_centrality'] / stable['avg_degree_centrality'].replace(0, float('inf'))
        stable = stable.sort_values(by='cv', ascending=True).head(20)

        print(f"\n=== Top 20 Stable Skills (Present in >={threshold:.0f}/{total_months} months, lowest volatility) ===")
        print("These skills maintain consistent importance over time:\n")
        for i, row in stable.iterrows():
            print(f"  {row['skill']:<45} months={row['months_present']:>3}  avg_centrality={row['avg_degree_centrality']:.4f}  CV={row['cv']:.4f}")
        stable.to_csv(os.path.join(results_dir, "top_stable_skills.csv"), index=False)
    else:
        print(f"Warning: {temporal_file} not found. Skipping stable skills.")

    # EMERGING SKILLS (Highest Centrality Growth)
    emerging_file = os.path.join(temporal_csv_dir, "emerging_skills.csv")
    if os.path.exists(emerging_file):
        emerging = pd.read_csv(emerging_file)
        print("\n=== Top Emerging Skills (Highest Centrality Growth) ===")
        print("These skills grew the most in importance over the observation period:\n")
        for i, row in emerging.iterrows():
            print(f"  {row['skill']:<45} growth={row['growth']:.4f}")
        # Copy to results dir for easy access
        emerging.to_csv(os.path.join(results_dir, "top_emerging_skills.csv"), index=False)
    else:
        print(f"Warning: {emerging_file} not found. Skipping emerging skills.")

    print(f"\n[OK] All results saved to: {results_dir}")


if __name__ == "__main__":
    analyze_results()
