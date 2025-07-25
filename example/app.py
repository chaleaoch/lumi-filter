import peewee
from flask import Flask, jsonify, request

from lumi_filter.field import FilterField
from lumi_filter.model import Model
from lumi_filter.shortcut import AutoQueryModel

app = Flask(__name__)

# Database setup
db = peewee.SqliteDatabase(":memory:")


class BaseModel(peewee.Model):
    class Meta:
        database = db


class UserModel(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    name = peewee.CharField()
    age = peewee.IntegerField()
    email = peewee.CharField()
    active = peewee.BooleanField()
    salary = peewee.FloatField()


class ProductModel(BaseModel):
    id = peewee.IntegerField(primary_key=True)
    name = peewee.CharField()
    category = peewee.CharField()
    price = peewee.FloatField()
    stock = peewee.IntegerField()
    available = peewee.BooleanField()


# Create tables and sample data
db.create_tables([UserModel, ProductModel])

# Insert sample data
UserModel.create(
    id=1, name="Alice", age=25, email="alice@example.com", active=True, salary=50000.0
)
UserModel.create(
    id=2, name="Bob", age=30, email="bob@example.com", active=False, salary=60000.0
)

ProductModel.create(
    id=1, name="Laptop", category="Electronics", price=999.99, stock=10, available=True
)
ProductModel.create(
    id=2, name="Chair", category="Furniture", price=149.99, stock=15, available=True
)

# Sample list data
USERS = [
    {
        "id": 1,
        "name": "Alice",
        "age": 25,
        "email": "alice@example.com",
        "active": True,
        "salary": 50000.0,
    },
    {
        "id": 2,
        "name": "Bob",
        "age": 30,
        "email": "bob@example.com",
        "active": False,
        "salary": 60000.0,
    },
]


@app.route("/users")
def get_users():
    """
    Get filtered users using AutoQueryModel
    curl "http://localhost:5000/users?age__gte=30&ordering=salary"
    """
    try:
        model = AutoQueryModel(USERS, request.args)
        filtered_data = model.filter().order().result()

        # Ensure data is a list for len() calculation
        if hasattr(filtered_data, "__iter__") and not isinstance(
            filtered_data, (str, bytes)
        ):
            filtered_data = list(filtered_data)

        return jsonify(
            {
                "success": True,
                "count": len(filtered_data)
                if isinstance(filtered_data, (list, tuple))
                else 1,
                "data": filtered_data,
                "filters": dict(request.args),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/users_peewee")
def get_users_peewee():
    """
    Get filtered users using Peewee model
    curl "http://localhost:5000/users_peewee?age__gte=25&ordering=salary"
    """
    try:
        query = UserModel.select()
        model = AutoQueryModel(query, request.args)
        filtered_data = model.filter().order().result()

        # Convert Peewee objects to dict and count
        data = [
            {
                "id": u.id,
                "name": u.name,
                "age": u.age,
                "email": u.email,
                "active": u.active,
                "salary": u.salary,
            }
            for u in filtered_data
        ]

        return jsonify(
            {
                "success": True,
                "count": len(data),
                "data": data,
                "filters": dict(request.args),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/users_manual")
def get_users_manual():
    """
    Get filtered users using manual Model class
    curl "http://localhost:5000/users_manual?age__gte=25&ordering=salary"
    """

    # Define custom filter model
    class UserFilter(Model):
        class Meta:
            schema = None
            fields = []
            extra_field = {
                "id": FilterField(source="id"),
                "name": FilterField(source="name"),
                "age": FilterField(source="age"),
                "email": FilterField(source="email"),
                "active": FilterField(source="active"),
                "salary": FilterField(source="salary"),
            }
            ordering_extra_field = {"id", "name", "age", "email", "active", "salary"}

    try:
        filtered_data = UserFilter(USERS, request.args).filter().order().result()

        # Ensure data is a list for len() calculation
        if hasattr(filtered_data, "__iter__") and not isinstance(
            filtered_data, (str, bytes)
        ):
            filtered_data = list(filtered_data)

        return jsonify(
            {
                "success": True,
                "count": len(filtered_data)
                if isinstance(filtered_data, (list, tuple))
                else 1,
                "data": filtered_data,
                "filters": dict(request.args),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
