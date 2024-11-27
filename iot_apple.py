from flask import Flask, request, jsonify
from cassandra.cluster import Cluster
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd

app = Flask(__name__)

# Connect to Cassandra
cluster = Cluster(["127.0.0.1"])
session = cluster.connect()
session.set_keyspace("apple_watch_iot")


# Utility function for formatting rows
def format_row(row, fields):
    row_data = {
        field: getattr(row, field, None) for field in fields if hasattr(row, field)
    }
    if "timestamp" in row_data and isinstance(row.timestamp, datetime):
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


# Existing API Endpoints for Each Table
# (No changes needed here unless you want to update them)


# New Endpoint: Get list of states
@app.route("/states", methods=["GET"])
def get_states():
    query = "SELECT * FROM environmental_data;"
    rows = session.execute(query)
    states = sorted({row.state for row in rows if row.state})
    
    return jsonify(states), 200


# New Endpoint: Get list of device IDs
@app.route("/device_ids", methods=["GET"])
def get_device_ids():
    query = "SELECT DISTINCT device_id FROM health_metrics;"
    rows = session.execute(query)
    device_ids = sorted({row.device_id for row in rows if row.device_id})
    return jsonify(device_ids), 200


# New Endpoint: Get list of dates for a device
@app.route("/dates", methods=["GET"])
def get_dates():
    device_id = request.args.get("device_id")
    if not device_id:
        return jsonify({"error": "device_id is required"}), 400

    query = "SELECT timestamp FROM health_metrics WHERE device_id = %s ALLOW FILTERING;"
    rows = session.execute(query, (device_id,))
    dates = sorted(
        {row.timestamp.strftime("%Y-%m-%d") for row in rows if row.timestamp}
    )
    return jsonify(dates), 200


# New Endpoint: Get stress levels by state
@app.route("/stress_levels", methods=["GET"])
def get_stress_levels():
    state = request.args.get("state")
    if not state:
        return jsonify({"error": "state is required"}), 400

    # Get device_ids for the given state
    query = f"SELECT *  FROM environmental_data WHERE state = '{state}' ALLOW FILTERING;"
    print(query)
    device_rows = session.execute(query)
    print(device_rows)
    device_ids = list(set([row.device_id for row in device_rows]))

    # Collect stress level data for all devices in the state
    stress_levels = []
    for device_id in device_ids:
        query = """
            SELECT timestamp, value FROM health_metrics
            WHERE device_id = %s AND metric_type = 'stress_level' ALLOW FILTERING;
        """
        rows = session.execute(query, (device_id,))
        stress_levels.extend(
            [
                {
                    "timestamp": row.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "value": row.value,
                    "device_id": device_id,
                }
                for row in rows
            ]
        )

    # Sort data by timestamp
    stress_levels.sort(key=lambda x: x["timestamp"])
    return jsonify(stress_levels), 200


# New Endpoint: Get heart rate data for a device on a specific date
@app.route("/heart_rate", methods=["GET"])
def get_heart_rate():
    device_id = request.args.get("device_id")
    date_str = request.args.get("date")
    if not device_id or not date_str:
        return jsonify({"error": "device_id and date are required"}), 400

    try:
        start_date = datetime.strptime(date_str, "%Y-%m-%d")
        end_date = start_date + timedelta(days=1)
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    query = """
        SELECT timestamp, value FROM health_metrics
        WHERE device_id = %s AND metric_type = 'heart_rate' AND timestamp >= %s AND timestamp < %s ALLOW FILTERING;
    """
    rows = session.execute(query, (device_id, start_date, end_date))
    heart_rates = [
        {"timestamp": row.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "value": row.value}
        for row in rows
    ]
    heart_rates.sort(key=lambda x: x["timestamp"])
    return jsonify(heart_rates), 200


# New Endpoint: Get weather data by state
@app.route("/weather", methods=["GET"])
def get_weather():
    state = request.args.get("state")
    if not state:
        return jsonify({"error": "state is required"}), 400

    # Get temperature data
    temp_query = """
        SELECT timestamp, value FROM environmental_data
        WHERE state = %s AND data_type = 'temperature' ALLOW FILTERING;
    """
    temp_rows = session.execute(temp_query, (state,))
    temp_data = [
        {
            "timestamp": row.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": float(row.value.replace("°C", "")),
        }
        for row in temp_rows
    ]

    # Get humidity data
    hum_query = """
        SELECT timestamp, value FROM environmental_data
        WHERE state = %s AND data_type = 'humidity' ALLOW FILTERING;
    """
    hum_rows = session.execute(hum_query, (state,))
    hum_data = [
        {
            "timestamp": row.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "humidity": float(row.value.replace("%", "")),
        }
        for row in hum_rows
    ]

    # Merge temperature and humidity data
    temp_df = pd.DataFrame(temp_data)
    hum_df = pd.DataFrame(hum_data)
    if not temp_df.empty and not hum_df.empty:
        merged_df = (
            pd.merge(temp_df, hum_df, on="timestamp", how="outer")
            .fillna(method="ffill")
            .fillna(method="bfill")
        )
    else:
        merged_df = temp_df if not temp_df.empty else hum_df

    merged_df = merged_df.sort_values("timestamp")
    weather_data = merged_df.to_dict(orient="records")
    return jsonify(weather_data), 200


# Existing API Endpoints (Unchanged)
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
        "state": request.args.get("state"),
        "town": request.args.get("town"),
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
