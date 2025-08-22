from logging.config import dictConfig

from flask import Flask

from app import cli
from app.api.advanced_model_filter import bp as advanced_model_filter_bp
from app.api.auto_filter import bp as auto_iterable_bp
from app.api.model_filter import bp as model_filter_bp
from extentions import db


def create_app() -> Flask:
    app = Flask(__name__)
    db.init_app(app)

    # Register CLI commands
    cli.init_app(app)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "standard": {
                    "format": """[%(levelname)s]&&[%(asctime)s]&&[%(name)s]&&[%(pathname)s:%(lineno)d]&&[%(funcName)s]:
%(message)s""",
                    "datefmt": "%Y-%m-%d %H:%M:%S %z",
                },
                "console": {"format": """[%(name)s]&&[%(pathname)s:%(lineno)d]&&[%(funcName)s]: %(message)s"""},
            },
            "filters": {},
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "console",
                },
            },
            "loggers": {
                "peewee": {
                    "handlers": ["console"],
                    "level": "DEBUG",
                    "propagate": True,
                },
            },
        }
    )
    # Register all API blueprints
    app.register_blueprint(auto_iterable_bp)
    app.register_blueprint(model_filter_bp)
    app.register_blueprint(advanced_model_filter_bp)

    return app
