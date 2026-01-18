import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

def mine_association_rules(df, min_support=0.01, min_confidence=0.3):
    """
    Mines frequent itemsets and association rules using Apriori.
    """
    print(f"Mining association rules (min_support={min_support})...")
    
    skills_list = df['skills_list'].tolist()
    
    te = TransactionEncoder()
    te_ary = te.fit(skills_list).transform(skills_list)
    df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
    
    # Frequent Itemsets
    frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
    
    if frequent_itemsets.empty:
        print("No frequent itemsets found with current support threshold.")
        return pd.DataFrame(), pd.DataFrame()
        
    # Association Rules
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    
    # Add lift
    # (Lift is calculated by default in recent mlxtend versions, but ensuring it's there)
    
    print(f"Found {len(frequent_itemsets)} frequent itemsets and {len(rules)} rules.")
    return frequent_itemsets, rules
