import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()


def create_app():
    """
    Application factory pattern.
    Creates and configures the Flask app.
    Returning the app from a function (rather than creating it at module level)
    makes it easier to test — you can call create_app() in tests to get a
    fresh instance each time.
    """
    app = Flask(__name__)

    # CORS allows the React dev server (localhost:5173) to call this API.
    # In production you would restrict this to your actual frontend domain.
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # ── API Key Authentication ────────────────────────────────────────
    # This function runs before EVERY request.
    # It checks for a valid X-API-Key header and rejects requests without one.
    @app.before_request
    def check_api_key():
        # Allow health checks and CORS preflight requests through without auth
        if request.path == '/health' or request.method == 'OPTIONS':
            return None

        key = request.headers.get('X-API-Key')
        expected = os.getenv('MEDRAG_API_KEY')

        if not key or key != expected:
            return jsonify({'error': 'Invalid or missing API key'}), 401

        return None

    # ── Health check endpoint ─────────────────────────────────────────
    # Used by AWS ECS to verify the container is alive.
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'}), 200

    # ── Register route blueprints ─────────────────────────────────────
    # Blueprints are Flask's way of splitting routes across multiple files.
    # Each blueprint registers its own URL prefix.
    from api.routes.recommend import recommend_bp
    app.register_blueprint(recommend_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

