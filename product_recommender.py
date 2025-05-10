import pandas as pd
import joblib


class ProductRecommender:
    def __init__(self, csv_file, model_path="model/random_forest_model.pkl"):
        self.csv_file = csv_file
        self.model_path = model_path
        self.df = None
        self.model = None

    def load_and_clean_data(self):
        self.df = pd.read_csv(self.csv_file)

        # Clean 'price' by removing commas and converting to float
        self.df["price"] = pd.to_numeric(
            self.df["price"].astype(str).str.replace(",", ""), errors="coerce"
        )

        # Clean 'review_count' to extract numeric part
        self.df["review_count"] = (
            self.df["review_count"]
            .astype(str)
            .str.extract(r"(\d+)")
            .fillna(0)
            .astype(int)
        )

        # Drop rows with missing values in required columns
        self.df.dropna(subset=["price", "review_count"], inplace=True)

    def load_model(self):
        if self.model is None:
            self.model = joblib.load(self.model_path)

    def predict_scores(self):
        self.load_model()
        X = self.df[["review_count", "price"]]
        self.df["score"] = self.model.predict_proba(X)[:, 1]  # Probability of label = 1

    def get_top_products(self, top_n=5):
        sorted_df = self.df.sort_values(
            by=["score", "review_count", "price"], ascending=[False, False, True]
        )
        top_df = sorted_df.head(top_n)
        return top_df[
            ["title", "price", "rating", "review_count", "score", "product_url", "image_url"]
        ]

    def run_recommendation(self, top_n=5):
        self.load_and_clean_data()
        self.predict_scores()
        return self.get_top_products(top_n)

# if __name__ == "__main__":
#     product = ProductRecommender('data/fetched-product/motorola phone under 20,000.csv')
#     top_products = product.run_recommendation(top_n=10)
#     top_products.to_csv("top_products.csv", index=False)
#     print(top_products)
