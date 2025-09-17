"""User behaviour clustering.

This module groups users based on their trading patterns, sizes and
frequencies.  Clusters can then be used to personalise pricing or LP
recommendations.
"""

import pandas as pd
from sklearn.cluster import KMeans


def cluster_user_behaviour(
    user_features: pd.DataFrame, n_clusters: int = 5, random_state: int = 42
) -> pd.DataFrame:
    """Cluster users based on numerical behavioural features.

    Parameters
    ----------
    user_features: pd.DataFrame
        DataFrame where each row corresponds to a user and columns represent
        behavioural metrics (e.g. trade_count, avg_trade_size, total_volume).
    n_clusters: int
        Number of clusters to form.
    random_state: int
        Seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        The input DataFrame with an additional column ``cluster`` indicating the
        assigned cluster label.
    """
    # Perform standardisation to equalise scale
    from sklearn.preprocessing import StandardScaler

    features = user_features.drop(columns=["user"])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features.values)
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    clusters = kmeans.fit_predict(X_scaled)
    user_features = user_features.copy()
    user_features["cluster"] = clusters
    return user_features