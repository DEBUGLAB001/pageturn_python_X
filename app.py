import os
from flask import Flask, render_template
from database import init_db
from routes.api_routes import api_bp
from routes.view_routes import view_bp

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "pageturn-dev-secret-key")

    # Initialize database tables and seed initial records if needed
    init_db(force_reseed=False)

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(view_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html"), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
