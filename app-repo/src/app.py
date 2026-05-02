from flask import Flask, jsonify, Response, request
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

start_time = time.time()

REQUEST_COUNT = Counter(
    "simple_api_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "simple_api_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

UPTIME = Gauge(
    "simple_api_uptime_seconds",
    "Application uptime in seconds"
)


@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    endpoint = request.endpoint or "unknown"

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()

    if hasattr(request, "start_time"):
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(time.time() - request.start_time)

    return response


@app.route("/")
def home():
    return jsonify(
        service="simple-api",
        status="running",
        endpoints=["/health", "/ready", "/metrics"]
    )


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/ready")
def ready():
    uptime = time.time() - start_time

    if uptime < 10:
        return jsonify(status="not ready"), 500

    return jsonify(status="ready")


@app.route("/metrics")
def metrics():
    uptime = time.time() - start_time
    UPTIME.set(uptime)

    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
