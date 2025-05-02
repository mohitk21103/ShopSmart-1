import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class ProductRecommender:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.df = None

    def load_and_clean_data(self):
        self.df = pd.read_csv(self.csv_file)

        # Clean and convert fields
        self.df["price"] = pd.to_numeric(self.df["price"].astype(str).str.replace(",", ""), errors="coerce")
        self.df["rating"] = pd.to_numeric(self.df["rating"], errors="coerce")
        self.df["review_count"] = self.df["review_count"].astype(str).str.extract(r'(\d+)').astype(float)

        # Drop rows with missing values
        self.df.dropna(subset=["price", "rating", "review_count"], inplace=True)

    def normalize_data(self):
        scaler = MinMaxScaler()
        self.df[["price_norm", "rating_norm", "review_norm"]] = scaler.fit_transform(
            self.df[["price", "rating", "review_count"]]
        )

    def calculate_scores(self, weight_rating=0.5, weight_review=0.3, weight_price=0.2):
        self.df["score"] = (
                self.df["rating_norm"] * weight_rating +
                self.df["review_norm"] * weight_review +
                (1 - self.df["price_norm"]) * weight_price
        )

    def get_top_products(self, top_n=5):
        top_df = self.df.sort_values("score", ascending=False).head(top_n)
        return top_df[["title", "price", "rating", "review_count", "score", "product_url", "image_url"]]

    def run_recommendation(self, top_n=5):
        self.load_and_clean_data()
        self.normalize_data()
        self.calculate_scores()
        return self.get_top_products(top_n)


# using below code For unit testing
# if __name__ == "__main__":
#     recommender = ProductRecommender("pen drive under 500.csv")
#     top_products = recommender.run_recommendation(top_n=5)
#     top_products.to_csv("top_5_recommended_products.csv", index=False)  # kept this just for dubug
#
#     json_data = top_products.to_json(orient='records')
#     print(json_data)
