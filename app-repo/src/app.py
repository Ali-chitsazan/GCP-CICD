from flask import Flask, jsonify
import time

app = Flask(__name__)

start_time = time.time()

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
    # simulate startup delay (dependency not ready yet)
    uptime = time.time() - start_time
    if uptime < 10:
        return jsonify(status="not ready"), 500
    return jsonify(status="ready")

'''@app.route("/ready")
def ready():
    # simulate dependency check (like DB)
    if random.random() > 0.2:
        return jsonify(status="ready")
    return jsonify(status="not ready"), 500'''

@app.route("/metrics")
def metrics():
    uptime = time.time() - start_time
    return jsonify(
        uptime_seconds=int(uptime),
        message="basic metrics"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)