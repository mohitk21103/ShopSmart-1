from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300))
    price = db.Column(db.Float)
    rating = db.Column(db.Float)
    review_count = db.Column(db.Integer)
    score = db.Column(db.Float)
    product_url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
