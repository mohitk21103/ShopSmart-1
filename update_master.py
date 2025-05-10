import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from scrap_product import AmazonScraper  # ensure scraper.py contains your AmazonScraper class
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
from datetime import datetime


class ModelUpdater:
    def __init__(self, search_term):
        self.search_term = search_term
        self.fetched_dir = "data/fetched-product"
        self.training_dir = "data/training-data"
        self.model_path = "model/random_forest_model.pkl"
        self.fetched_csv_path = os.path.join(self.fetched_dir, f"{self.search_term}.csv")
        self.master_csv_path = os.path.join(self.training_dir, "master.csv")

        os.makedirs(self.fetched_dir, exist_ok=True)
        os.makedirs(self.training_dir, exist_ok=True)
        os.makedirs("model", exist_ok=True)

    def run_pipeline(self):
        print(f"\n🔄 Starting pipeline for '{self.search_term}' at {datetime.now()}")
        self.scrape_data()
        self.update_master_csv()
        self.train_model()

    def scrape_data(self):
        if os.path.exists(self.fetched_csv_path):
            os.remove(self.fetched_csv_path)
        scraper = AmazonScraper(self.search_term)
        scraper.scrape_all()
        scraper.save_to_csv(self.fetched_csv_path)

    def update_master_csv(self):
        new_data = pd.read_csv(self.fetched_csv_path)
        if os.path.exists(self.master_csv_path):
            master_data = pd.read_csv(self.master_csv_path)
            combined = pd.concat([master_data, new_data], ignore_index=True)
            combined.drop_duplicates(subset=["title"], inplace=True)
        else:
            combined = new_data

        combined.to_csv(self.master_csv_path, index=False)
        print("✅ Master CSV updated.")

    def train_model(self):
        if not os.path.exists(self.master_csv_path):
            print("⚠️ master.csv not found. Cannot train model.")
            return
        df = pd.read_csv(self.master_csv_path)

        # Preprocessing:
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)

        # Now perform the transformation
        df['review_count'] = (
            df['review_count']
            .astype(str)
            .str.replace(",", "", regex=False)
            .apply(lambda x: ''.join(filter(str.isdigit, x)))  # Keep only digits
            .replace('', '0')
            .astype(int)
        )

        # 'score' column based on 'rating' and 'review_count'
        # Normalize rating and review_count to the same scale
        scaler = MinMaxScaler()
        df[['rating_normalized', 'review_count_normalized']] = scaler.fit_transform(
            df[['rating', 'review_count']])

        # Combining rating and review count into a final 'score'
        df['score'] = df['rating_normalized'] * 0.7 + df['review_count_normalized'] * 0.3

        # Create a realistic label based on the score (top 25% products)
        threshold = df['score'].quantile(0.75)  # Top 25% products based on score
        df['label'] = (df['score'] >= threshold).astype(int)  # 1 = top 25% products

        # Clean the 'price' column
        df['price'] = (
            df['price']
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True)  # Remove ₹, commas, words
            .replace("", "0")  # Replace empty strings with 0
            .astype(float)  # Convert to float
        )

        X = df[['review_count', 'price']]
        y = df['label']

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Model training
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Saving the trained model
        joblib.dump(model, self.model_path)
        print(f"✅ Model saved to {self.model_path}")

        # Predictions and evaluation
        y_pred = model.predict(X_test)
        print("\n📊 Classification Report:")
        print(classification_report(y_test, y_pred))

        acc = model.score(X_test, y_test)
        print(f"✅ Model accuracy: {acc:.2%}")

    def append_new_data(self, new_csv_path):
        if os.path.exists(new_csv_path):
            new_df = pd.read_csv(new_csv_path)
            if os.path.exists(self.master_csv_path):
                master_df = pd.read_csv(self.master_csv_path)
                combined_df = pd.concat([master_df, new_df], ignore_index=True).drop_duplicates()
            else:
                combined_df = new_df
            combined_df.to_csv(self.master_csv_path, index=False)
            print(f"✅ Appended data from '{new_csv_path}' to master.csv.")
        else:
            print(f"⚠️ New CSV path '{new_csv_path}' does not exist.")


# Using Below for Unit Testing
# if __name__ == "__main__":
#     check = ModelUpdater("ABC")
#     check.train_model()
