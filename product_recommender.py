import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler


class ProductRecommender:
    def __init__(self, csv_file, model_path="model/random_forest_model.pkl"):
        self.csv_file = csv_file
        self.model_path = model_path
        self.df = None
        self.model = None

    def load_and_clean_data(self):
        self.df = pd.read_csv(self.csv_file)

        # Clean and convert fields
        self.df["price"] = pd.to_numeric(self.df["price"].astype(str).str.replace(",", ""), errors="coerce")
        self.df["rating"] = pd.to_numeric(self.df["rating"], errors="coerce")
        self.df["review_count"] = self.df["review_count"].astype(str).str.extract(r'(\d+)').astype(float)

        self.df.dropna(subset=["price", "rating", "review_count"], inplace=True)

    def load_model(self):
        if not self.model:
            self.model = joblib.load(self.model_path)

    def predict_scores(self):
        self.load_model()
        X = self.df[["rating", "review_count"]]
        self.df["score"] = self.model.predict_proba(X)[:, 1]  # Probability of label=1 (good product)

    def get_top_products(self, top_n=5):
        top_df = self.df.sort_values("score", ascending=False).head(top_n)
        return top_df[["title", "price", "rating", "review_count", "score", "product_url", "image_url"]]

    def run_recommendation(self, top_n=5):
        self.load_and_clean_data()
        self.predict_scores()
        return self.get_top_products(top_n)
