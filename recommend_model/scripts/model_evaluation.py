"""
model_evaluation.py
---------------------------------------
Evaluate Collaborative Filtering Model (Item-Item Similarity)
Metrics: RMSE, MAE, Precision@K, Recall@K
---------------------------------------
"""

import pandas as pd
import numpy as np
import pickle
from math import sqrt
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split


# -------------------- STEP 1: Load Data --------------------
print(" Loading data and similarity matrix...")

# Load ratings data
ratings = pd.read_csv(r"D:\movie_recommendation_system\recommend_model\data\processed\ratings_final_fixed.csv")   # columns: userId, movieId, rating
print(f" Ratings loaded: {len(ratings)} rows")

# Load similarity matrix
with open(r"D:\movie_recommendation_system\recommend_model\trained_models\item_similarity.pkl", "rb") as f:
    item_similarity = pickle.load(f)
print(f" Similarity matrix loaded with shape: {item_similarity.shape}")


# -------------------- STEP 2: Predict Rating --------------------
def predict_rating(user_id, movie_id, ratings_df, similarity_matrix, k=10):
    """
    Predicts how a user might rate a given movie based on their existing ratings.
    Uses weighted average of item similarities and user ratings.
    """
    user_ratings = ratings_df[ratings_df["userId"] == user_id]

    # If user hasn't rated anything or movie not in matrix
    if user_ratings.empty or movie_id not in similarity_matrix.index:
        return np.nan

    # Get similarities between target movie and user-rated movies
    similarities = similarity_matrix.loc[movie_id, user_ratings["movieId"]].dropna()

    if similarities.empty:
        return np.nan

    # Take top-K similar movies
    top_k = similarities.sort_values(ascending=False)[:k]
    rated_movies = user_ratings[user_ratings["movieId"].isin(top_k.index)]

    if rated_movies.empty:
        return np.nan

    weights = top_k.values
    ratings = rated_movies["rating"].values

    # Weighted average of ratings
    return np.dot(weights, ratings) / np.sum(np.abs(weights))


# -------------------- STEP 3: Split Train/Test --------------------
print(" Splitting data into train and test sets...")
train_df, test_df = train_test_split(ratings, test_size=0.2, random_state=42)
print(f"Train: {len(train_df)} | Test: {len(test_df)}")


# -------------------- STEP 4: Compute RMSE and MAE --------------------
print(" Calculating RMSE and MAE...")

predictions, actuals = [], []

for _, row in test_df.iterrows():
    pred = predict_rating(row["userId"], row["movieId"], train_df, item_similarity)
    if not np.isnan(pred):
        predictions.append(pred)
        actuals.append(row["rating"])

# Compute numeric accuracy
rmse = sqrt(mean_squared_error(actuals, predictions))
mae = mean_absolute_error(actuals, predictions)

print("\n Model Evaluation Results:")
print(f"   RMSE: {rmse:.4f}")
print(f"   MAE : {mae:.4f}")


# -------------------- STEP 5: Precision@K & Recall@K --------------------
def precision_recall_at_k(test_df, train_df, similarity_matrix, k=10):
    """
    Evaluates how well the system recommends relevant movies.
    Returns average Precision@K and Recall@K across users.
    """
    precisions, recalls = [], []

    for user_id in test_df["userId"].unique():
        user_train = train_df[train_df["userId"] == user_id]
        user_test = test_df[test_df["userId"] == user_id]

        if user_train.empty or user_test.empty:
            continue

        # Relevant (liked) movies = ratings >= 4
        liked_movies = user_test[user_test["rating"] >= 4]["movieId"].tolist()
        if not liked_movies:
            continue

        all_movies = similarity_matrix.index.tolist()
        unseen_movies = [m for m in all_movies if m not in user_train["movieId"].values]

        preds = []
        for m in unseen_movies[:100]:  # limit for performance
            p = predict_rating(user_id, m, train_df, similarity_matrix)
            if not np.isnan(p):
                preds.append((m, p))

        preds = sorted(preds, key=lambda x: x[1], reverse=True)[:k]
        recommended = [m for m, _ in preds]

        # Compute precision and recall
        hits = len(set(recommended) & set(liked_movies))
        precisions.append(hits / k)
        recalls.append(hits / len(liked_movies))

    return np.mean(precisions), np.mean(recalls)


print("\n Calculating Precision@K and Recall@K...")
precision, recall = precision_recall_at_k(test_df, train_df, item_similarity, k=10)

print("\nRanking Evaluation:")
print(f"   Precision@10: {precision:.4f}")
print(f"   Recall@10   : {recall:.4f}")


# -------------------- STEP 6: Summary --------------------
print("\nModel Evaluation Complete!")
print("-" * 40)
print(f"RMSE           : {rmse:.4f}")
print(f"MAE            : {mae:.4f}")
print(f"Precision@10   : {precision:.4f}")
print(f"Recall@10      : {recall:.4f}")
print("-" * 40)
