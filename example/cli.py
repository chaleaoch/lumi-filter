import click
from flask.cli import with_appcontext

from app.db_model import Category, Product
from extentions import database


def init_db():
    """Initialize the database with sample data."""
    click.echo("Initializing database...")

    database.connect(reuse_if_open=True)
    database.create_tables([Category, Product])

    if Category.select().count() == 0 and Product.select().count() == 0:
        click.echo("Adding sample data...")
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

        click.echo("Sample data added successfully!")
    else:
        click.echo("Database already contains data. Skipping sample data creation.")

    database.close()
    click.echo("Database initialization completed!")


def clean_db():
    # Delete all records from both tables
    Product.delete().execute()
    Category.delete().execute()

    # Reset SQLite sequence counters (equivalent to TRUNCATE behavior)
    # database.execute_sql("DELETE FROM sqlite_sequence WHERE name='product'")
    # database.execute_sql("DELETE FROM sqlite_sequence WHERE name='category'")

    database.close()


@click.command()
@with_appcontext
def initialize():
    init_db()


def init_app(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(initialize)
