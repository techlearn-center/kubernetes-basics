"""
Simple Flask API for Kubernetes Challenge
==========================================
This is a basic Flask app that you'll deploy to Kubernetes.
It has health endpoints and returns simple JSON responses.
"""

import os
from flask import Flask, jsonify

app = Flask(__name__)

# Configuration from environment variables (will come from ConfigMap/Secret)
APP_NAME = os.getenv("APP_NAME", "K8s Challenge App")
APP_ENV = os.getenv("FLASK_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
API_KEY = os.getenv("API_KEY", "not-set")


@app.route("/")
def home():
    """Home endpoint - returns app info."""
    return jsonify({
        "app": APP_NAME,
        "environment": APP_ENV,
        "message": "Welcome to the Kubernetes Challenge!",
        "endpoints": {
            "/": "This page",
            "/health": "Health check endpoint",
            "/config": "Show configuration (from ConfigMap)",
            "/secret-check": "Verify secret is loaded"
        }
    })


@app.route("/health")
def health():
    """
    Health check endpoint.
    Kubernetes will use this for liveness and readiness probes.
    """
    return jsonify({
        "status": "healthy",
        "app": APP_NAME
    })


@app.route("/config")
def config():
    """Show configuration loaded from ConfigMap."""
    return jsonify({
        "app_name": APP_NAME,
        "environment": APP_ENV,
        "log_level": LOG_LEVEL,
        "source": "ConfigMap (environment variables)"
    })


@app.route("/secret-check")
def secret_check():
    """Verify that the secret was loaded (without exposing the actual value)."""
    api_key_loaded = API_KEY != "not-set" and len(API_KEY) > 0
    return jsonify({
        "api_key_loaded": api_key_loaded,
        "api_key_length": len(API_KEY) if api_key_loaded else 0,
        "source": "Secret (environment variable)"
    })


@app.route("/ready")
def ready():
    """
    Readiness check - more detailed than health.
    In a real app, this might check database connections, etc.
    """
    return jsonify({
        "ready": True,
        "checks": {
            "config_loaded": APP_NAME != "K8s Challenge App",
            "secret_loaded": API_KEY != "not-set"
        }
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = APP_ENV == "development"
    print(f"Starting {APP_NAME} on port {port} (env: {APP_ENV})")
    app.run(host="0.0.0.0", port=port, debug=debug)
