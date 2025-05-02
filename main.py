from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/results")
def show_results():
    search_term = request.args.get('query', '')
    recommended_product = {
        'name': f"{search_term}",
        'price': '₹150',
        'description': f'Recommended product for "{search_term}"',
    }
    return render_template("show-Result.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render's port or default to 5000
    app.run(host="0.0.0.0", port=port, debug=False)
