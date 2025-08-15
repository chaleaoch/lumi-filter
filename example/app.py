"""Flask application entrypoint for the example.

Run with:
	uvicorn-like: (Flask dev server)
		python -m example.app

Feature demo endpoints:
	Peewee basic:            GET /peewee/products
	Peewee extra ordering:   GET /peewee/products/extra-ordering?ordering=-name_len
	Generic iterable:        GET /generic/users
	Auto Peewee:             GET /auto/peewee/products
	Auto Pydantic:           GET /auto/pydantic/products

Examples:
	curl 'http://127.0.0.1:5000/peewee/products?price__gte=1&ordering=-price'
	curl 'http://127.0.0.1:5000/peewee/products/extra-ordering?ordering=-name_len'
	curl 'http://127.0.0.1:5000/generic/users?profile_bio__iin=python'
	curl 'http://127.0.0.1:5000/auto/pydantic/products?name__in=Al'
"""

from __future__ import annotations

from flask import Flask

from .app.api.peewee_basic import bp as peewee_basic_bp  # type: ignore
from .app.api.peewee_extra_ordering import (
	bp as peewee_extra_ordering_bp,  # type: ignore
)
from .app.api.generic_iterable import bp as generic_iterable_bp  # type: ignore
from .app.api.auto_filter_peewee import bp as auto_peewee_bp  # type: ignore
from .app.api.auto_filter_pydantic import bp as auto_pydantic_bp  # type: ignore


def create_app() -> Flask:
	app = Flask(__name__)
	app.register_blueprint(peewee_basic_bp)
	app.register_blueprint(peewee_extra_ordering_bp)
	app.register_blueprint(generic_iterable_bp)
	app.register_blueprint(auto_peewee_bp)
	app.register_blueprint(auto_pydantic_bp)
	return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
	app.run(debug=True)

