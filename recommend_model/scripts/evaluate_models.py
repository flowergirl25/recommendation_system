import numpy as np
import pandas as pd
import pickle
import scipy.sparse as sp
from math import sqrt

# ===============================
# Load Data & Models
# ===============================
ratings = pd.read_csv(
    r"D:\movie_recommendation_system\recommend_model\data\processed\ratings_final_fixed.csv"
)

# Collaborative filtering model (item-item similarity)
with open(r"D:\movie_recommendation_system\recommend_model\trained_models\item_similarity.pkl", "rb") as f:
    item_similarity = pickle.load(f)

# Content-based features (auto-detect dense, COO, or CSR)
loader = np.load(r"D:\movie_recommendation_system\recommend_model\trained_models\X_content_improved.npz")
print("Available keys in X_content_improved.npz:", loader.files)

if {"row", "col", "data", "shape"}.issubset(loader.files):
    X_content = sp.coo_matrix(
        (loader["data"], (loader["row"], loader["col"])),
        shape=loader["shape"]
    ).tocsr()
elif {"indices", "indptr", "data", "shape"}.issubset(loader.files):
    X_content = sp.csr_matrix(
        (loader["data"], loader["indices"], loader["indptr"]),
        shape=loader["shape"]
    )
else:
    X_content = loader[loader.files[0]]

# Precomputed cosine similarity matrix
with open(r"D:\movie_recommendation_system\recommend_model\trained_models\cosine_sim_improved.pkl", "rb") as f:
    cosine_sim = pickle.load(f)

# Load movieId ↔ index mappings
with open(r"D:\movie_recommendation_system\recommend_model\trained_models\movie_index.pkl", "rb") as f:
    movie_index = pickle.load(f)

with open(r"D:\movie_recommendation_system\recommend_model\trained_models\reverse_index.pkl", "rb") as f:
    reverse_index = pickle.load(f)

# ===============================
# Metrics
# ===============================
def precision_at_k(recommended, relevant, k=10):
    recommended_k = recommended[:k]
    return len(set(recommended_k) & set(relevant)) / k if k > 0 else 0

def recall_at_k(recommended, relevant, k=10):
    recommended_k = recommended[:k]
    return len(set(recommended_k) & set(relevant)) / len(relevant) if relevant else 0

def rmse(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.sqrt(np.mean((y_true - y_pred) ** 2))

def mae(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs(y_true - y_pred))

# ===============================
# Evaluation Functions
# ===============================
def evaluate_content_from_features(user_id, k=10):
    """Content-based recommendations using X_content (dense or sparse)."""
    user_movies = ratings[ratings["userId"] == user_id]["movieId"].tolist()
    if not user_movies:
        return [], 0, 0

    target_movie_id = user_movies[-1]
    if target_movie_id not in movie_index:
        return [], 0, 0

    target_idx = movie_index[target_movie_id]

    if sp.issparse(X_content):
        sim_scores = list(enumerate(X_content[target_idx].toarray().ravel()))
    else:
        sim_scores = list(enumerate(X_content[target_idx]))

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    recommended_idxs = [i for i, _ in sim_scores if i != target_idx][:k]

    # Safe mapping
    recommended = [reverse_index[i] for i in recommended_idxs if i in reverse_index]

    relevant = user_movies
    return recommended, precision_at_k(recommended, relevant, k), recall_at_k(recommended, relevant, k)


def evaluate_content_from_cosine(user_id, k=10):
    """Content-based recommendations using precomputed cosine_sim.pkl."""
    user_movies = ratings[ratings["userId"] == user_id]["movieId"].tolist()
    if not user_movies:
        return [], 0, 0

    target_movie_id = user_movies[-1]
    if target_movie_id not in movie_index:
        return [], 0, 0

    target_idx = movie_index[target_movie_id]

    sim_scores = list(enumerate(cosine_sim[target_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    recommended_idxs = [i for i, _ in sim_scores if i != target_idx][:k]

    # Safe mapping
    recommended = [reverse_index[i] for i in recommended_idxs if i in reverse_index]

    relevant = user_movies
    return recommended, precision_at_k(recommended, relevant, k), recall_at_k(recommended, relevant, k)


def evaluate_collaborative(user_id, k=10):
    """Collaborative filtering recommendations using item similarity matrix."""
    user_data = ratings[ratings["userId"] == user_id]
    user_movies = user_data["movieId"].tolist()
    if not user_movies:
        return [], 0, 0, [], []

    scores = {}
    for movie in user_movies:
        if movie in item_similarity:
            similar = item_similarity[movie]
            for sim_movie, score in similar.items():
                scores[sim_movie] = scores.get(sim_movie, 0) + score

    recommended = sorted(scores, key=scores.get, reverse=True)[:k]
    relevant = user_movies

    # Precision/Recall
    prec = precision_at_k(recommended, relevant, k)
    rec = recall_at_k(recommended, relevant, k)

    # Rating prediction (for RMSE/MAE)
    true_ratings = user_data["rating"].tolist()
    pred_ratings = []
    for m in user_movies:
        if m in scores:
            pred_ratings.append(scores[m] / max(scores.values()))  # normalized
        else:
            pred_ratings.append(2.5)  # neutral fallback

    return recommended, prec, rec, true_ratings, pred_ratings

# ===============================
# Run Evaluation
# ===============================
def run_evaluation(n_users=50, k=10):
    sampled_users = ratings["userId"].drop_duplicates().sample(n=n_users, random_state=42)

    feat_precisions, feat_recalls = [], []
    cos_precisions, cos_recalls = [], []
    collab_precisions, collab_recalls = [], []
    all_true, all_pred = [], []

    for uid in sampled_users:
        _, fp, fr = evaluate_content_from_features(uid, k)
        _, cp, cr = evaluate_content_from_cosine(uid, k)
        _, pp, pr, true_ratings, pred_ratings = evaluate_collaborative(uid, k)

        feat_precisions.append(fp)
        feat_recalls.append(fr)
        cos_precisions.append(cp)
        cos_recalls.append(cr)
        collab_precisions.append(pp)
        collab_recalls.append(pr)
        all_true.extend(true_ratings)
        all_pred.extend(pred_ratings)

    print(" Content-Based (Feature Similarity)")
    print(f"Precision@{k}: {np.mean(feat_precisions):.4f}")
    print(f"Recall@{k}: {np.mean(feat_recalls):.4f}")

    print("\n Content-Based (Cosine Sim Precomputed)")
    print(f"Precision@{k}: {np.mean(cos_precisions):.4f}")
    print(f"Recall@{k}: {np.mean(cos_recalls):.4f}")

    print("\n Collaborative Filtering")
    print(f"Precision@{k}: {np.mean(collab_precisions):.4f}")
    print(f"Recall@{k}: {np.mean(collab_recalls):.4f}")
    print(f"RMSE: {rmse(all_true, all_pred):.4f}")
    print(f"MAE:  {mae(all_true, all_pred):.4f}")


if __name__ == "__main__":
    run_evaluation(n_users=50, k=10)

