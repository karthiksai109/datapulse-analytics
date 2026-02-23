import os
from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
    app.config["AWS_REGION"] = os.environ.get("AWS_REGION", "us-east-1")
    app.config["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")
    app.config["BEDROCK_MODEL_ID"] = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-v2")

    CORS(app, origins="*")

    from .routes.ai_routes import ai_bp
    from .routes.health_routes import health_bp

    app.register_blueprint(ai_bp, url_prefix="/api/v1/ai")
    app.register_blueprint(health_bp, url_prefix="/api/v1")

    return app
