import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import requests
import pandas as pd
import plotly.express as px

# Initialize the Dash app
app = dash.Dash(__name__)


# Define the layout of the dashboard
# Define the layout of the dashboard
app.layout = html.Div(
    [
        html.H1("Apple Watch IoT Data Dashboard", style={"textAlign": "center"}),
        # Text input to Enter Device ID
        html.Div(
            [
                html.Label("Enter Device ID:"),
                dcc.Input(
                    id="device-id-input",
                    type="text",
                    placeholder="Enter a device ID...",
                    style={"width": "50%", "padding": "10px"},
                ),
                html.Button("Submit", id="submit-button", n_clicks=0),
            ],
            style={"textAlign": "center", "marginBottom": "20px"},
        ),
        # Placeholder for health metrics charts (horizontally aligned)
        html.Div(
            id="health-metrics-charts",
            style={
                "display": "flex",
                "flexDirection": "row",
                "flexWrap": "nowrap",
                "justifyContent": "space-around",
                "alignItems": "center",
            },
        ),
        html.Div(
            id="activity-tracking-charts",
            style={
                "display": "flex",
                "flexDirection": "row",
                "flexWrap": "nowrap",
                "justifyContent": "space-around",
                "alignItems": "center",
            },
        ),
        html.Div(
            id="environmental-data-charts",
            style={
                "display": "flex",
                "flexDirection": "row",
                "flexWrap": "nowrap",
                "justifyContent": "space-around",
                "alignItems": "center",
            },
        ),
    ]
)


@app.callback(
    Output("health-metrics-charts", "children"),
    [Input("submit-button", "n_clicks")],
    [State("device-id-input", "value")],
)
def update_health_metrics(n_clicks, device_id):
    if not device_id or n_clicks == 0:
        return []

    charts = []
    HEALTH_METRICS = ["heart_rate", "calories_burned", "sleep_quality"]

    try:
        response = requests.get(
            f"http://127.0.0.1:5000/health_metrics?device_id={device_id}"
        )
        data = response.json()

        # Convert data to a DataFrame
        df = pd.DataFrame(data)
        gb = df.groupby(by="metric_type")

        # Generate a graph for each health metric type
        for metric_type in HEALTH_METRICS:
            if metric_type not in gb.groups:
                continue

            group = gb.get_group(metric_type)
            group["timestamp"] = pd.to_datetime(group["timestamp"])
            unit = str(group["unit"].unique()[0])

            # Create line chart
            fig = px.line(
                group,
                x="timestamp",
                y="value",
                title=f"{metric_type.replace('_', ' ').title()} Over Time for Device: {device_id}",
                labels={
                    "timestamp": "Time (Days)",  # X-axis label
                    "value": f"{metric_type.replace('_', ' ').title()}({str(unit)})",  # Y-axis label
                },
            )

            # Append chart component to the list of charts
            charts.append(
                html.Div(
                    [
                        dcc.Graph(figure=fig),
                    ],
                    style={"width": "30%", "padding": "10px"},
                )
            )
    except Exception as e:
        print(f"Error updating health metrics charts: {e}")

    return charts


@app.callback(
    Output("activity-tracking-charts", "children"),
    [Input("submit-button", "n_clicks")],
    [State("device-id-input", "value")],
)
def update_activity_tracking(n_clicks, device_id):
    if not device_id or n_clicks == 0:
        return []

    charts = []
    ACTIVITY_TYPES = ["walking", "running", "cycling"]

    try:
        response = requests.get(
            f"http://127.0.0.1:5000/activity_tracking?device_id={device_id}"
        )
        data = response.json()

        # Convert data to a DataFrame
        df = pd.DataFrame(data)
        gb = df.groupby(by="activity_type")

        # Generate a graph for each activity type
        for activity_type in ACTIVITY_TYPES:
            if activity_type not in gb.groups:
                continue

            group = gb.get_group(activity_type)
            group["timestamp"] = pd.to_datetime(group["timestamp"])
            unit = str(group["unit"].unique()[0])

            # Create bar chart for each activity type
            fig = px.bar(
                group,
                x="timestamp",
                y="value",
                title=f"{activity_type.title()} Activity Over Time for Device: {device_id}",
                labels={"value": f"{activity_type.title()}({unit})"},
            )

            # Append chart component to the list of charts
            charts.append(
                html.Div(
                    [
                        dcc.Graph(figure=fig),
                    ],
                    style={"width": "30%", "padding": "10px"},
                )
            )
    except Exception as e:
        print(f"Error updating activity tracking charts: {e}")

    return charts


@app.callback(
    Output("environmental-data-charts", "children"),
    [Input("submit-button", "n_clicks")],
    [State("device-id-input", "value")],
)
def update_environmental_data(n_clicks, device_id):
    if not device_id or n_clicks == 0:
        return []

    charts = []
    DATA_TYPES = ["temperature", "humidity"]

    try:
        # Fetch data from the Flask API for environmental data
        response = requests.get(
            f"http://127.0.0.1:5000/environmental_data?device_id={device_id}"
        )
        data = response.json()

        # Convert data to a DataFrame
        df = pd.DataFrame(data)
        gb = df.groupby(by="data_type")

        # Generate a graph for each environmental data type
        for data_type in DATA_TYPES:
            if data_type not in gb.groups:
                continue

            group = gb.get_group(data_type)
            group["timestamp"] = pd.to_datetime(group["timestamp"])

            # Extract the unit (assuming the unit is included in the 'value' column for environmental metrics)
            # e.g., if value contains '25.3°C', we extract the unit part.
            unit = "units"  # Placeholder if unit extraction is not clear
            if data_type in ["temperature", "humidity"]:
                # Split the value and extract unit assuming the value is like '25.3°C' or '50%'
                unit = (
                    group["value"].iloc[0].split()[-1]
                    if len(group["value"].iloc[0].split()) > 1
                    else ""
                )

            # Create line chart for each data type (except location which might need different handling)
            fig = px.line(
                group,
                x="timestamp",
                y="value",
                title=f"{data_type.title()} Over Time for Device: {device_id}",
                labels={"timestamp": "Time", "value": f"{data_type.title()} ({unit})"},
            )

            # Append chart component to the list of charts
            charts.append(
                html.Div(
                    [
                        dcc.Graph(figure=fig),
                    ],
                    style={"width": "30%", "padding": "10px"},
                )
            )
    except Exception as e:
        print(f"Error updating environmental data charts: {e}")

    return charts


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True, host="127.0.0.1", port=8050)
