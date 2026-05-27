from flask import Flask
from flask_cors import CORS
from celery_app import init_celery
from database.extensions import db, migrate
from logging_config.config import setup_logging


def create_app():
    setup_logging()

    app = Flask(__name__)

    CORS(app, origins=[
        "http://localtyrematch.com:8080",
        "http://localhost:8080",
    ])

    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db, directory="database/migrations")

    init_celery(app)

    from api.routes import register_blueprints
    register_blueprints(app)

    return app
