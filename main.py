from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
from threading import Thread
from product_recommender import ProductRecommender
from update_master import ModelUpdater
from top_recommendation_db_setup import Product, db

app = Flask(__name__)

# -----------dataBase Creation--------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///recommended_products.db"
db.init_app(app)

with app.app_context():
    db.create_all()

BASE_DIR = "data"
FETCHED_DIR = os.path.join(BASE_DIR, "fetched-product")
RECOMMENDED_DIR = os.path.join(BASE_DIR, "recommended-data")

os.makedirs(FETCHED_DIR, exist_ok=True)
os.makedirs(RECOMMENDED_DIR, exist_ok=True)

# Keep status in memory
processing_status = {}


@app.route("/")
def home():
    products = Product.query.order_by(Product.review_count.desc(), Product.rating.desc()).limit(15).all()
    return render_template("index.html", results=products)


@app.route("/results")
def show_results():
    search_term = request.args.get('query', '')
    final = request.args.get('final')

    fetched_csv_path = os.path.join(FETCHED_DIR, f"{search_term}.csv")
    recommended_csv_path = os.path.join(RECOMMENDED_DIR, f"{search_term}_recommended.csv")

    if not final:
        # Start background processing
        if processing_status.get(search_term) != "done":
            processing_status[search_term] = "processing"

            def background_task():
                updater = ModelUpdater(search_term)
                updater.run_pipeline()
                processing_status[search_term] = "done"

            Thread(target=background_task).start()
        return render_template("processing.html", query=search_term)

    # Final result rendering
    if not os.path.exists(recommended_csv_path):
        recommender = ProductRecommender(fetched_csv_path)
        top_products = recommender.run_recommendation(top_n=10)
        top_products.to_csv(recommended_csv_path, index=False)

        for _, row in top_products.iterrows():
            existing = Product.query.filter_by(product_url=row["product_url"]).first()
            if not existing:
                product = Product(
                    title=row["title"],
                    price=row["price"],
                    rating=row["rating"],
                    review_count=row["review_count"],
                    score=row["score"],
                    product_url=row["product_url"],
                    image_url=row["image_url"]
                )
                db.session.add(product)
            db.session.commit()

    df = pd.read_csv(recommended_csv_path)
    top_product_json = df.to_dict(orient='records')
    return render_template("show-Result.html", query=search_term, results=top_product_json)


@app.route("/status")
def check_status():
    search_term = request.args.get("query", "")
    status = processing_status.get(search_term, "not_started")
    return jsonify({"status": status})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
