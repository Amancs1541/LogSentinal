import os
from flask import Flask
from .config import Config
from .extensions import db, migrate
from .routes.main import main_bp
from .routes.logs import logs_bp
from .routes.anomalies import anomalies_bp
from .routes.auth import auth_bp
from .routes.geo import geo_bp
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    from .models import user, log_entry, anomaly  # noqa

    app.register_blueprint(main_bp)
    app.register_blueprint(logs_bp, url_prefix="/logs")
    app.register_blueprint(anomalies_bp, url_prefix="/anomalies")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(geo_bp, url_prefix="/api")

    return app
