from flask import Flask

from app.api.auto_filter_iteratorable import bp as auto_iterable_bp
from app.api.auto_filter_peewee import bp as auto_peewee_bp
from app.api.extra_field_ordering_extra_field import bp as extra_fields_bp
from app.api.model_filter import bp as model_filter_bp
from app.api.model_filter_peewee import bp as peewee_filter_bp
from app.api.model_filter_pydantic import bp as pydantic_filter_bp
from app.db_model import Category, Product
from extentions import database, db


def init_db():
    database.connect(reuse_if_open=True)
    database.create_tables([Category, Product])

    if Category.select().count() == 0 and Product.select().count() == 0:
        # Compact one-line seed data list.
        sample = [
            {"name": "Apple", "price": 1.20, "is_active": True, "category": "Fruit"},
            {"name": "Orange", "price": 2.50, "is_active": True, "category": "Citrus"},
            {"name": "Banana", "price": 0.80, "is_active": True, "category": "Tropical"},
            {"name": "Watermelon", "price": 6.30, "is_active": False, "category": "Melon"},
            {"name": "Grape", "price": 3.10, "is_active": True, "category": "Berry"},
            {"name": "Strawberry", "price": 4.50, "is_active": True, "category": "Berry"},
            {"name": "Blueberry", "price": 5.10, "is_active": True, "category": "Berry"},
            {"name": "Mango", "price": 2.90, "is_active": True, "category": "Tropical"},
            {"name": "Pineapple", "price": 3.70, "is_active": True, "category": "Tropical"},
            {"name": "Lemon", "price": 0.60, "is_active": True, "category": "Citrus"},
            {"name": "Lime", "price": 0.55, "is_active": True, "category": "Citrus"},
            {"name": "Peach", "price": 2.20, "is_active": True, "category": "Stone"},
            {"name": "Cherry", "price": 6.80, "is_active": True, "category": "Stone"},
            {"name": "Pear", "price": 1.85, "is_active": True, "category": "Fruit"},
            {"name": "Kiwi", "price": 1.10, "is_active": True, "category": "Tropical"},
            {"name": "Papaya", "price": 2.40, "is_active": True, "category": "Tropical"},
            {"name": "Dragonfruit", "price": 7.90, "is_active": True, "category": "Tropical"},
            {"name": "Avocado", "price": 3.30, "is_active": True, "category": "Berry"},
            {"name": "Plum", "price": 2.05, "is_active": True, "category": "Stone"},
            {"name": "Apricot", "price": 2.15, "is_active": True, "category": "Stone"},
            {"name": "Coconut", "price": 4.20, "is_active": False, "category": "Tropical"},
            {"name": "Grapefruit", "price": 1.60, "is_active": True, "category": "Citrus"},
            {"name": "Pomegranate", "price": 5.60, "is_active": True, "category": "Berry"},
            {"name": "Fig", "price": 3.95, "is_active": True, "category": "Fruit"},
            {"name": "Date", "price": 6.10, "is_active": True, "category": "Fruit"},
        ]

        with database.atomic():
            cat_map: dict[str, Category] = {}
            for cat_name in sorted({p["category"] for p in sample}):
                cat_map[cat_name] = Category.create(name=cat_name)
            for item in sample:
                cat = cat_map[item.pop("category")]
                Product.create(**item, category=cat)
    database.close()


def create_app() -> Flask:
    app = Flask(__name__)
    db.init_app(app)
    init_db()

    # Register all API blueprints
    app.register_blueprint(auto_peewee_bp)
    app.register_blueprint(auto_iterable_bp)
    app.register_blueprint(model_filter_bp)
    app.register_blueprint(peewee_filter_bp)
    app.register_blueprint(pydantic_filter_bp)
    app.register_blueprint(extra_fields_bp)

    return app
