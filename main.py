from flask import Flask, render_template, request, jsonify
import os
from scrap_product import AmazonScraper
from product_recommender import ProductRecommender

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/results")
def show_results():
    search_term = request.args.get('query', '')

    scraper = AmazonScraper(search_term)
    scraper.scrape_all()

    file_name = f"{search_term}.csv"
    scraper.save_to_csv(file_name)

    recommender = ProductRecommender(file_name)
    top_products = recommender.run_recommendation(top_n=5)

    top_product_json = top_products.to_dict(orient='records')

    # top_product_json = [{ "image_url": "https://m.media-amazon.com/images/I/61aaBr2UhdL._SL1500_.jpg",
    # "price": 1077, "product_url": "https://www.amazon.in/KECHAODA-Company-Bluetooth-Dialer-Stylish/dp/B074P32V9D",
    # "rating": 3.6, "review_count": 783, "score": 0.676470588235294, "title": "KECHAODA SM Company K33 Bluetooth
    # Dialer with Camera and Dual Sim,Slim Card Size and Light Weight and Stylish Mobile Phone(Black)" }]

    return render_template("show-Result.html", query=search_term, results=top_product_json)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render's port or default to 5000
    app.run(host="0.0.0.0", port=port, debug=False)
