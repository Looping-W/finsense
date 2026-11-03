import logging
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from finsense_api.auth.routes import bp as auth_bp
from finsense_api.config import load_config, sqlalchemy_database_uri
from finsense_api.db import database_status
from finsense_api.extensions import db, migrate

logger = logging.getLogger(__name__)


def create_app():
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    config = load_config()

    app = Flask(__name__)
    app.config["FINSENSE"] = config
    app.config["SQLALCHEMY_DATABASE_URI"] = sqlalchemy_database_uri(config)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.json.ensure_ascii = False
    CORS(app, resources={r"/api/*": {"origins": config.cors_origins}})
    db.init_app(app)
    from finsense_api import models  # noqa: F401

    migrate.init_app(app, db)

    from finsense_api.errors import ApiError

    @app.errorhandler(ApiError)
    def handle_api_error(err):
        return jsonify(error=err.message), err.status

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", database=database_status())

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    logger.debug("finsense api ready")
    return app
