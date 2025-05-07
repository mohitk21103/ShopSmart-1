import os
from flask import Flask, render_template, request

from product_recommender import ProductRecommender
from update_master import ModelUpdater

app = Flask(__name__)

# Directory setup
BASE_DIR = "data"
FETCHED_DIR = os.path.join(BASE_DIR, "fetched-product")
RECOMMENDED_DIR = os.path.join(BASE_DIR, "recommended-data")

os.makedirs(FETCHED_DIR, exist_ok=True)
os.makedirs(RECOMMENDED_DIR, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/results")
def show_results():
    search_term = request.args.get('query', '')

    # Step 1: Update model pipeline with new search
    updater = ModelUpdater(search_term)
    updater.run_pipeline()

    # Step 2: Get path to the latest fetched CSV
    fetched_csv_path = os.path.join(FETCHED_DIR, f"{search_term}.csv")

    # Step 3: Recommend products
    recommender = ProductRecommender(fetched_csv_path)
    top_products = recommender.run_recommendation(top_n=10)

    # Step 4: Save and display recommendations
    recommended_csv_path = os.path.join(RECOMMENDED_DIR, f"{search_term}_recommended.csv")
    top_products.to_csv(recommended_csv_path, index=False)

    top_product_json = top_products.to_dict(orient='records')

    return render_template("show-Result.html", query=search_term, results=top_product_json)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
