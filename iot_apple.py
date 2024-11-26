from flask import Flask, request, jsonify
from cassandra.cluster import Cluster
from datetime import datetime

app = Flask(__name__)

# Connect to Cassandra
cluster = Cluster(["127.0.0.1"])  # Replace with your Cassandra cluster IP
session = cluster.connect()
session.set_keyspace("apple_watch_iot")  # Replace with your keyspace


# Utility function for formatting rows
def format_row(row, fields):
    row_data = {field: getattr(row, field) for field in fields if hasattr(row, field)}
    if "timestamp" in row_data:
        row_data["timestamp"] = row.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return row_data


# Generic Query Function
def query_table(table_name, query_params, fields="*"):
    conditions = []
    params = []

    for key, value in query_params.items():
        if key == "start_time":
            conditions.append("timestamp >= %s")
            params.append(datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        elif key == "end_time":
            conditions.append("timestamp <= %s")
            params.append(datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
        else:
            conditions.append(f"{key} = %s")
            params.append(value)

    query = f"SELECT {fields} FROM {table_name}"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ALLOW FILTERING;"

    rows = session.execute(query, tuple(params))
    result = [
        format_row(row, fields.split(",") if fields != "*" else row._fields)
        for row in rows
    ]
    return result


# API Endpoints for Each Table


@app.route("/device_metadata", methods=["GET"])
def device_metadata():
    query_params = {
        "device_id": request.args.get("device_id"),
    }
    fields = request.args.get("fields", "*")
    query_params = {k: v for k, v in query_params.items() if v is not None}
    result = query_table("device_metadata", query_params, fields)
    return jsonify(result), 200


@app.route("/health_metrics", methods=["GET"])
def health_metrics():
    query_params = {
        "device_id": request.args.get("device_id"),
        "metric_type": request.args.get("metric_type"),
        "start_time": request.args.get("start_time"),
        "end_time": request.args.get("end_time"),
    }
    fields = request.args.get("fields", "*")
    query_params = {k: v for k, v in query_params.items() if v is not None}
    result = query_table("health_metrics", query_params, fields)
    return jsonify(result), 200


@app.route("/activity_tracking", methods=["GET"])
def activity_tracking():
    query_params = {
        "device_id": request.args.get("device_id"),
        "activity_type": request.args.get("activity_type"),
        "start_time": request.args.get("start_time"),
        "end_time": request.args.get("end_time"),
    }
    fields = request.args.get("fields", "*")
    query_params = {k: v for k, v in query_params.items() if v is not None}
    result = query_table("activity_tracking", query_params, fields)
    return jsonify(result), 200


@app.route("/environmental_data", methods=["GET"])
def environmental_data():
    query_params = {
        "device_id": request.args.get("device_id"),
        "data_type": request.args.get("data_type"),
        "start_time": request.args.get("start_time"),
        "end_time": request.args.get("end_time"),
    }
    fields = request.args.get("fields", "*")
    query_params = {k: v for k, v in query_params.items() if v is not None}
    result = query_table("environmental_data", query_params, fields)
    return jsonify(result), 200


@app.route("/notifications", methods=["GET"])
def notifications():
    query_params = {
        "device_id": request.args.get("device_id"),
        "notification_type": request.args.get("notification_type"),
        "start_time": request.args.get("start_time"),
        "end_time": request.args.get("end_time"),
        "is_read": request.args.get("is_read"),
    }
    fields = request.args.get("fields", "*")
    query_params = {k: v for k, v in query_params.items() if v is not None}
    result = query_table("notifications", query_params, fields)
    return jsonify(result), 200


@app.route("/device_status_logs", methods=["GET"])
def device_status_logs():
    query_params = {
        "device_id": request.args.get("device_id"),
        "status_code": request.args.get("status_code"),
        "start_time": request.args.get("start_time"),
        "end_time": request.args.get("end_time"),
    }
    fields = request.args.get("fields", "*")
    query_params = {k: v for k, v in query_params.items() if v is not None}
    result = query_table("device_status_logs", query_params, fields)
    return jsonify(result), 200


@app.route("/")
def hello_world():
    return "<p>Hello, IoT API is running!</p>"


if __name__ == "__main__":
    app.run(debug=True)
