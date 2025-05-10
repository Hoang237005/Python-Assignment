import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA


def prepare_data(filepath, excluded_columns):
    """Load and preprocess the dataset"""
    dataset = pd.read_csv(filepath, na_values=['N/a'])
    processed_data = dataset.drop(columns=excluded_columns)
    return processed_data.fillna(processed_data.mean(numeric_only=True))


def determine_optimal_clusters(data, max_clusters=10):
    """Calculate WCSS for different cluster counts"""
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(data)

    cluster_errors = []
    for n in range(1, max_clusters + 1):
        cluster_model = KMeans(
            n_clusters=n,
            init='k-means++',
            max_iter=400,
            n_init=20,
            random_state=42
        )
        cluster_model.fit(normalized_data)
        cluster_errors.append(cluster_model.inertia_)

    return normalized_data, cluster_errors


def visualize_elbow_method(cluster_range, wcss_values):
    """Plot the elbow method graph"""
    plt.figure()
    plt.plot(cluster_range, wcss_values, marker='o')
    plt.title("Optimal Cluster Count Determination")
    plt.xlabel("Number of Clusters")
    plt.ylabel("Within-Cluster Sum of Squares")
    plt.grid(True)
    plt.savefig('Exercise 3/elbow_analysis.png')
    plt.close()


def perform_clustering(data, n_clusters=3):
    """Execute K-means clustering and return results"""
    clustering_model = KMeans(
        n_clusters=n_clusters,
        init='k-means++',
        max_iter=400,
        n_init=20,
        random_state=42
    )
    cluster_labels = clustering_model.fit_predict(data)
    return cluster_labels, clustering_model


def visualize_clusters(features_2d, cluster_labels):
    """Create 2D visualization of clusters"""
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        features_2d[:, 0],
        features_2d[:, 1],
        c=cluster_labels,
        cmap='plasma',
        s=60,
        alpha=0.8
    )
    plt.title("Player Clusters in 2D Space")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.colorbar(scatter, label='Cluster Group')
    plt.savefig('Exercise 3/cluster_visualization_2d.png')
    plt.close()


def main():
    # Configuration
    INPUT_FILE = 'Exercise 1/result.csv'
    COLUMNS_TO_REMOVE = [
        'Player', 'Nation', 'Position', 'Team',
        'GA90', 'Save%', 'CS%', 'Penalty_Save%'
    ]

    # Data preparation
    analysis_data = prepare_data(INPUT_FILE, COLUMNS_TO_REMOVE)

    # Cluster optimization
    scaled_data, wcss_values = determine_optimal_clusters(analysis_data)
    visualize_elbow_method(range(1, 11), wcss_values)
    print("Elbow analysis plot saved to elbow_analysis.png")

    # Clustering execution
    cluster_assignments, model = perform_clustering(scaled_data)
    clustering_score = silhouette_score(scaled_data, cluster_assignments)
    print(f"Clustering Quality Score: {clustering_score:.3f}")

    # Dimensionality reduction and visualization
    reducer = PCA(n_components=2)
    reduced_features = reducer.fit_transform(scaled_data)
    visualize_clusters(reduced_features, cluster_assignments)
    print("Cluster visualization saved to cluster_visualization_2d.png")


if __name__ == "__main__":
    main()