from flask import Flask, jsonify, Response, render_template_string, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import time
import socket
import platform
from datetime import datetime, timezone

app = Flask(__name__)

APP_STARTED_AT = time.time()
READINESS_DELAY_SECONDS = int(os.getenv("READINESS_DELAY_SECONDS", "10"))

REQUEST_COUNT = Counter(
    "app_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "app_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)


@app.before_request
def start_timer():
    request.start_time = time.time()


@app.after_request
def record_metrics(response):
    endpoint = request.path
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()

    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=endpoint
    ).observe(time.time() - request.start_time)

    return response


def get_app_info():
    uptime_seconds = int(time.time() - APP_STARTED_AT)
    is_ready = uptime_seconds >= READINESS_DELAY_SECONDS

    return {
        "app_name": os.getenv("APP_NAME", "GCP CI/CD Demo App"),
        "environment": os.getenv("ENVIRONMENT", "dev"),
        "image_version": os.getenv("IMAGE_VERSION", "local"),
        "git_sha": os.getenv("GIT_SHA", "local"),
        "pod_name": os.getenv("POD_NAME", socket.gethostname()),
        "namespace": os.getenv("POD_NAMESPACE", "local"),
        "node_name": os.getenv("NODE_NAME", "local"),
        "python_version": platform.python_version(),
        "uptime_seconds": uptime_seconds,
        "started_at_utc": datetime.fromtimestamp(APP_STARTED_AT, timezone.utc).isoformat(),
        "ready": is_ready
    }


@app.route("/")
def home():
    info = get_app_info()

    readiness_badge = "READY" if info["ready"] else "STARTING"
    readiness_class = "ok" if info["ready"] else "warn"

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>GCP CI/CD Demo App</title>
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #0f172a, #1e3a8a);
                color: #f8fafc;
            }

            .container {
                max-width: 1100px;
                margin: 0 auto;
                padding: 50px 25px;
            }

            .hero {
                background: rgba(255, 255, 255, 0.10);
                border: 1px solid rgba(255, 255, 255, 0.20);
                border-radius: 20px;
                padding: 35px;
                margin-bottom: 25px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
            }

            h1 {
                margin: 0 0 10px;
                font-size: 36px;
            }

            .subtitle {
                color: #cbd5e1;
                font-size: 17px;
                line-height: 1.5;
            }

            .badge {
                display: inline-block;
                padding: 8px 14px;
                border-radius: 999px;
                font-size: 13px;
                font-weight: bold;
                margin-top: 20px;
            }

            .ok {
                background: #22c55e;
                color: #052e16;
            }

            .warn {
                background: #facc15;
                color: #422006;
            }

            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 18px;
            }

            .card {
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 16px;
                padding: 22px;
            }

            .label {
                color: #cbd5e1;
                font-size: 13px;
                margin-bottom: 8px;
            }

            .value {
                font-size: 20px;
                font-weight: bold;
                word-break: break-word;
            }

            .links {
                margin-top: 28px;
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
            }

            a {
                color: #0f172a;
                background: #f8fafc;
                text-decoration: none;
                padding: 11px 16px;
                border-radius: 10px;
                font-weight: bold;
            }

            a:hover {
                background: #dbeafe;
            }

            .footer {
                margin-top: 30px;
                color: #cbd5e1;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <h1>{{ info.app_name }}</h1>
                <div class="subtitle">
                    A containerized Flask application deployed to GKE using GitHub Actions, Docker Hub, ArgoCD, Kubernetes, and Prometheus metrics.
                </div>
                <div class="badge {{ readiness_class }}">{{ readiness_badge }}</div>
            </div>

            <div class="grid">
                <div class="card">
                    <div class="label">Environment</div>
                    <div class="value">{{ info.environment }}</div>
                </div>

                <div class="card">
                    <div class="label">Image Version</div>
                    <div class="value">{{ info.image_version }}</div>
                </div>

                <div class="card">
                    <div class="label">Git SHA</div>
                    <div class="value">{{ info.git_sha }}</div>
                </div>

                <div class="card">
                    <div class="label">Pod Name</div>
                    <div class="value">{{ info.pod_name }}</div>
                </div>

                <div class="card">
                    <div class="label">Namespace</div>
                    <div class="value">{{ info.namespace }}</div>
                </div>

                <div class="card">
                    <div class="label">Node Name</div>
                    <div class="value">{{ info.node_name }}</div>
                </div>

                <div class="card">
                    <div class="label">Python Version</div>
                    <div class="value">{{ info.python_version }}</div>
                </div>

                <div class="card">
                    <div class="label">Uptime</div>
                    <div class="value">{{ info.uptime_seconds }} seconds</div>
                </div>
            </div>

            <div class="links">
                <a href="/health">Health</a>
                <a href="/ready">Readiness</a>
                <a href="/metrics">Prometheus Metrics</a>
                <a href="/api/info">API Info</a>
            </div>

            <div class="footer">
                Built for a real DevOps portfolio project: CI/CD, GitOps, GKE, observability, and runtime visibility.
            </div>
        </div>
    </body>
    </html>
    """

    return render_template_string(
        html,
        info=info,
        readiness_badge=readiness_badge,
        readiness_class=readiness_class
    )


@app.route("/api/info")
def api_info():
    return jsonify(get_app_info())


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": os.getenv("APP_NAME", "GCP CI/CD Demo App")
    }), 200


@app.route("/ready")
def ready():
    info = get_app_info()

    if not info["ready"]:
        return jsonify({
            "status": "not_ready",
            "message": "Application is still warming up",
            "uptime_seconds": info["uptime_seconds"]
        }), 503

    return jsonify({
        "status": "ready",
        "uptime_seconds": info["uptime_seconds"]
    }), 200


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)