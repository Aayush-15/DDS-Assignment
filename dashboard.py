import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import requests
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Apple Watch IoT Data Dashboard"

# Fetch available states for dropdown
def fetch_states():
    response = requests.get("http://127.0.0.1:5000/states")
    if response.status_code == 200:
        return response.json()
    return []

# Fetch available device IDs for dropdown
def fetch_device_ids():
    response = requests.get("http://127.0.0.1:5000/device_ids")
    if response.status_code == 200:
        return response.json()
    return []

# Fetch available dates for a device
def fetch_dates(device_id):
    response = requests.get(f"http://127.0.0.1:5000/dates?device_id={device_id}")
    if response.status_code == 200:
        return response.json()
    return []

# Define the layout of the dashboard
app.layout = html.Div(
    [
        html.H1("Apple Watch IoT Data Dashboard", style={"textAlign": "center"}),

        # Device ID Input
        html.Div(
        [
            html.Label("Enter Device ID:", style={"display": "block", "marginBottom": "10px"}),
            dcc.Input(
                id="device-id-input",
                type="text",
                placeholder="Enter a device ID...",
                style={"width": "50%", "padding": "10px", "display": "block", "marginBottom": "10px"},
            ),
            html.Button("Submit", id="submit-button", n_clicks=0, style={"display": "block"}),
        ],
        style={"textAlign": "left", "marginBottom": "20px", "marginLeft": "20px"},
    ),


        # Health Metrics Charts
        html.Div(
            id="health-metrics-charts",
            style={
                "display": "flex",
                "flexDirection": "row",
                "flexWrap": "wrap",
                "justifyContent": "space-around",
                "alignItems": "center",
            },
        ),

        # Activity Tracking Charts
        html.Div(
            id="activity-tracking-charts",
            style={
                "display": "flex",
                "flexDirection": "row",
                "flexWrap": "wrap",
                "justifyContent": "space-around",
                "alignItems": "center",
            },
        ),

        # Environmental Data Charts
        html.Div(
            id="environmental-data-charts",
            style={
                "display": "flex",
                "flexDirection": "row",
                "flexWrap": "wrap",
                "justifyContent": "space-around",
                "alignItems": "center",
            },
        ),

        html.Hr(),

        # New Graph: Stress Levels by State
        html.Div(
            [
                html.H2("Stress Levels by State"),
                html.Label("Select State:"),
                dcc.Dropdown(
                    id="state-dropdown",
                    options=[{"label": state, "value": state} for state in fetch_states()],
                    value=fetch_states()[0] if fetch_states() else None,
                    style={"width": "50%", "padding": "10px"},
                ),
                dcc.Graph(id="stress-levels-graph"),
            ],
            style={"margin": "20px"},
        ),

        html.Hr(),

        # New Graph: Heart Rate for Single User Over a Day
        html.Div(
            [
                html.H2("Heart Rate for Single User Over a Day"),
                html.Label("Select Device ID:"),
                dcc.Dropdown(
                    id="single-user-dropdown",
                    options=[{"label": device, "value": device} for device in fetch_device_ids()],
                    value=None,
                    style={"width": "50%", "padding": "10px"},
                    placeholder="Select a device ID",
                ),
                html.Label("Select Date:"),
                dcc.Dropdown(
                    id="date-dropdown",
                    options=[],
                    value=None,
                    style={"width": "50%", "padding": "10px"},
                    placeholder="Select a date",
                ),
                dcc.Graph(id="single-user-heart-rate-graph"),
            ],
            style={"margin": "20px"},
        ),

        html.Hr(),

        # New Graph: Correlation between Heart Rate and Stress Level
        html.Div(
            [
                html.H2("Correlation between Heart Rate and Stress Level"),
                html.Label("Select Device ID:"),
                dcc.Dropdown(
                    id="correlation-device-dropdown",
                    options=[{"label": device, "value": device} for device in fetch_device_ids()],
                    value=None,
                    style={"width": "50%", "padding": "10px"},
                    placeholder="Select a device ID",
                ),
                dcc.Graph(id="correlation-graph"),
            ],
            style={"margin": "20px"},
        ),

        html.Hr(),

        # New Graph: Average Stress Level per State
        html.Div(
            [
                html.H2("Average Stress Level per State"),
                dcc.Graph(id="average-stress-level-state-graph"),
            ],
            style={"margin": "20px"},
        ),

        html.Hr(),

        # New Graph: Activity Distribution for Devices
        html.Div(
            [
                html.H2("Activity Distribution for Devices"),
                dcc.Graph(id="activity-distribution-graph"),
            ],
            style={"margin": "20px"},
        ),

        html.Hr(),

        # New Graph: Stress Level Heatmap Over Time
        html.Div(
            [
                html.H2("Stress Level Heatmap Over Time"),
                dcc.Graph(id="stress-level-heatmap"),
            ],
            style={"margin": "20px"},
        ),

        html.Hr(),

        # New Graph: Temperature vs. Heart Rate Over Time
        html.Div(
            [
                html.H2("Temperature vs. Heart Rate Over Time"),
                html.Label("Select Device ID:"),
                dcc.Dropdown(
                    id="temp-hr-device-dropdown",
                    options=[{"label": device, "value": device} for device in fetch_device_ids()],
                    value=None,
                    style={"width": "50%", "padding": "10px"},
                    placeholder="Select a device ID",
                ),
                dcc.Graph(id="temp-hr-graph"),
            ],
            style={"margin": "20px"},
        ),

        html.Hr(),

        # New Graph: Map of Device Locations
        html.Div(
            [
                html.H2("Map of Device Locations"),
                dcc.Graph(id="device-location-map"),
            ],
            style={"margin": "20px"},
        ),

        html.Hr(),

        # New Graph: Heart Rate Distribution Histogram
        html.Div(
            [
                html.H2("Heart Rate Distribution"),
                html.Label("Select Device ID (or leave blank for all devices):"),
                dcc.Dropdown(
                    id="hr-histogram-device-dropdown",
                    options=[{"label": device, "value": device} for device in fetch_device_ids()],
                    value=None,
                    style={"width": "50%", "padding": "10px"},
                    placeholder="Select a device ID or leave blank",
                ),
                dcc.Graph(id="hr-histogram"),
            ],
            style={"margin": "20px"},
        ),

        # Interval component for periodic updates (optional)
        dcc.Interval(
            id='interval-component',
            interval=60*1000,  # Refresh every minute
            n_intervals=0
        ),
    ]
)

# Callback to update date options based on selected device
@app.callback(
    Output("date-dropdown", "options"),
    [Input("single-user-dropdown", "value")]
)
def update_date_options(selected_device):
    if not selected_device:
        return []
    dates = fetch_dates(selected_device)
    return [{"label": date, "value": date} for date in dates]

# Callback to update health metrics charts
@app.callback(
    Output("health-metrics-charts", "children"),
    [Input("submit-button", "n_clicks")],
    [State("device-id-input", "value")],
)
def update_health_metrics(n_clicks, device_id):
    if not device_id or n_clicks == 0:
        return []

    charts = []
    HEALTH_METRICS = ["heart_rate", "calories_burned", "stress_level"]

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
            unit = str(group["unit"].unique()[0]) if "unit" in group.columns else ""

            # Create line chart
            fig = px.line(
                group,
                x="timestamp",
                y="value",
                title=f"{metric_type.replace('_', ' ').title()} Over Time for Device: {device_id}",
                labels={
                    "timestamp": "Time",
                    "value": f"{metric_type.replace('_', ' ').title()} ({unit})",
                },
                template="plotly_white",
            )

            # Customize layout
            fig.update_layout(
                title_font_size=16,
                xaxis_title="Time",
                yaxis_title=f"{metric_type.replace('_', ' ').title()} ({unit})",
                xaxis_tickformat="%H:%M:%S",
                font=dict(
                    family="Arial",
                    size=12,
                ),
                hovermode="x unified",
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

# Callback to update activity tracking charts
@app.callback(
    Output("activity-tracking-charts", "children"),
    [Input("submit-button", "n_clicks")],
    [State("device-id-input", "value")],
)
def update_activity_tracking(n_clicks, device_id):
    if not device_id or n_clicks == 0:
        return []

    charts = []
    ACTIVITY_TYPES = ["walking", "running", "cycling", "biking"]

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
            unit = str(group["unit"].unique()[0]) if "unit" in group.columns else ""

            # Create bar chart
            fig = px.bar(
                group,
                x="timestamp",
                y="value",
                title=f"{activity_type.title()} Activity Over Time for Device: {device_id}",
                labels={"value": f"{activity_type.title()} ({unit})"},
                template="plotly_white",
            )

            # Customize layout
            fig.update_layout(
                title_font_size=16,
                xaxis_title="Time",
                yaxis_title=f"{activity_type.title()} ({unit})",
                xaxis_tickformat="%H:%M:%S",
                font=dict(
                    family="Arial",
                    size=12,
                ),
                hovermode="x unified",
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

# Callback to update environmental data charts
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

            unit = ""
            if data_type == "temperature":
                group["value"] = group["value"].str.replace('°C', '').astype(float)
                unit = "°C"
            elif data_type == "humidity":
                group["value"] = group["value"].str.replace('%', '').astype(float)
                unit = "%"

            # Create line chart
            fig = px.line(
                group,
                x="timestamp",
                y="value",
                title=f"{data_type.title()} Over Time for Device: {device_id}",
                labels={"timestamp": "Time", "value": f"{data_type.title()} ({unit})"},
                template="plotly_white",
            )

            # Customize layout
            fig.update_layout(
                title_font_size=16,
                xaxis_title="Time",
                yaxis_title=f"{data_type.title()} ({unit})",
                xaxis_tickformat="%H:%M:%S",
                font=dict(
                    family="Arial",
                    size=12,
                ),
                hovermode="x unified",
            )

            # Append chart component to the list of charts
            charts.append(
                html.Div(
                    [
                        dcc.Graph(figure=fig),
                    ],
                    style={"width": "45%", "padding": "10px"},
                )
            )
    except Exception as e:
        print(f"Error updating environmental data charts: {e}")

    return charts

# Callback for Stress Levels by State
@app.callback(
    Output("stress-levels-graph", "figure"),
    [Input("state-dropdown", "value")]
)
def update_stress_levels(state):
    if not state:
        return {}
    try:
        response = requests.get(
            f"http://127.0.0.1:5000/stress_levels?state={state}"
        )
        data = response.json()
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        fig = px.line(
            df,
            x="timestamp",
            y="value",
            color="device_id",
            title=f"Stress Levels Over Time in {state}",
            labels={"timestamp": "Time", "value": "Stress Level"},
            template="plotly_white",
        )
        fig.update_layout(
            title_font_size=16,
            xaxis_title="Time",
            yaxis_title="Stress Level",
            xaxis_tickformat="%H:%M:%S",
            font=dict(
                family="Arial",
                size=12,
            ),
            hovermode="x unified",
        )
        return fig
    except Exception as e:
        print(f"Error updating stress levels graph: {e}")
        return {}

# Callback for Single User Heart Rate Over a Day
@app.callback(
    Output("single-user-heart-rate-graph", "figure"),
    [Input("single-user-dropdown", "value"),
     Input("date-dropdown", "value")]
)
def update_single_user_heart_rate(device_id, selected_date):
    if not device_id or not selected_date:
        return {}
    try:
        response = requests.get(
            f"http://127.0.0.1:5000/heart_rate?device_id={device_id}&date={selected_date}"
        )
        data = response.json()
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        fig = px.line(
            df,
            x="timestamp",
            y="value",
            title=f"Heart Rate Over Time for {device_id} on {selected_date}",
            labels={"timestamp": "Time", "value": "Heart Rate (bpm)"},
            template="plotly_white",
        )
        fig.update_layout(
            title_font_size=16,
            xaxis_title="Time",
            yaxis_title="Heart Rate (bpm)",
            xaxis_tickformat="%H:%M:%S",
            font=dict(
                family="Arial",
                size=12,
            ),
            hovermode="x unified",
        )
        return fig
    except Exception as e:
        print(f"Error updating single user heart rate graph: {e}")
        return {}

# Callback for Correlation between Heart Rate and Stress Level
@app.callback(
    Output("correlation-graph", "figure"),
    [Input("correlation-device-dropdown", "value")]
)
def update_correlation_graph(device_id):
    if not device_id:
        return {}
    try:
        # Fetch heart rate and stress level data
        ff=f"http://127.0.0.1:5000/health_metrics?device_id={device_id}&metric_type=heart_rate"
        print("DDS-------------")
        print(ff)
        response_hr = requests.get(
            f"http://127.0.0.1:5000/health_metrics?device_id={device_id}&metric_type=heart_rate"
        )
        response_sl = requests.get(
            f"http://127.0.0.1:5000/health_metrics?device_id={device_id}&metric_type=stress_level"
        )
        data_hr = response_hr.json()
        data_sl = response_sl.json()

        # Merge data on timestamp
        df_hr = pd.DataFrame(data_hr)
        df_sl = pd.DataFrame(data_sl)
        print(df_hr)
        print(df_sl)
        df_hr["timestamp"] = pd.to_datetime(df_hr["timestamp"])
        df_sl["timestamp"] = pd.to_datetime(df_sl["timestamp"])

        df = pd.merge(df_hr, df_sl, on="timestamp", suffixes=("_hr", "_sl"))

        # Create scatter plot
        fig = px.scatter(
            df,
            x="value_hr",
            y="value_sl",
            trendline="ols",
            title=f"Heart Rate vs. Stress Level for Device: {device_id}",
            labels={
                "value_hr": "Heart Rate (bpm)",
                "value_sl": "Stress Level",
            },
            template="plotly_white",
        )
        fig.update_layout(
            title_font_size=16,
            xaxis_title="Heart Rate (bpm)",
            yaxis_title="Stress Level",
            font=dict(
                family="Arial",
                size=12,
            ),
            hovermode="closest",
        )
        return fig
    except Exception as e:
        
        print(f"Error updating correlation graph: {e}")
        return {}

# Callback for Average Stress Level per State
@app.callback(
    Output("average-stress-level-state-graph", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_average_stress_level_state_graph(n):
    try:
        # Fetch stress level data for all devices
        response = requests.get("http://127.0.0.1:5000/health_metrics?metric_type=stress_level")
        data = response.json()
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Fetch device locations to get states
        response_locations = requests.get("http://127.0.0.1:5000/environmental_data?data_type=location")
        location_data = response_locations.json()
        df_locations = pd.DataFrame(location_data)
        df_locations = df_locations[["device_id", "state"]].drop_duplicates()

        # Merge data to get state information
        df_merged = pd.merge(df, df_locations, on="device_id")

        # Calculate average stress level per state
        df_grouped = df_merged.groupby("state")["value"].mean().reset_index()

        # Create bar chart
        fig = px.bar(
            df_grouped,
            x="state",
            y="value",
            title="Average Stress Level per State",
            labels={
                "state": "State",
                "value": "Average Stress Level",
            },
            template="plotly_white",
        )
        fig.update_layout(
            title_font_size=16,
            xaxis_title="State",
            yaxis_title="Average Stress Level",
            font=dict(
                family="Arial",
                size=12,
            ),
        )
        return fig
    except Exception as e:
        print(f"Error updating average stress level per state graph: {e}")
        return {}

# Callback for Activity Distribution for Devices
@app.callback(
    Output("activity-distribution-graph", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_activity_distribution_graph(n):
    try:
        # Fetch activity tracking data
        response = requests.get("http://127.0.0.1:5000/activity_tracking")
        data = response.json()
        
        if len(data) == 0:
            return
        
        
        df = pd.DataFrame(data)

        # Count activities
        activity_counts = df["activity_type"].value_counts().reset_index()
        activity_counts.columns = ["activity_type", "count"]

        # Create pie chart
        fig = px.pie(
            activity_counts,
            names="activity_type",
            values="count",
            title="Activity Distribution Across Devices",
            template="plotly_white",
        )
        fig.update_layout(
            title_font_size=16,
            font=dict(
                family="Arial",
                size=12,
            ),
        )
        return fig
    except Exception as e:
        print(f"Error updating activity distribution graph: {e}")
        return {}

# Callback for Stress Level Heatmap Over Time
@app.callback(
    Output("stress-level-heatmap", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_stress_level_heatmap(n):
    try:
        # Fetch stress level data
        response = requests.get("http://127.0.0.1:5000/health_metrics?metric_type=stress_level")
        data = response.json()
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour

        # Pivot the data
        heatmap_data = df.pivot_table(
            index="device_id",
            columns="hour",
            values="value",
            aggfunc='mean'
        )

        # Create heatmap
        fig = px.imshow(
            heatmap_data,
            labels=dict(x="Hour of Day", y="Device ID", color="Stress Level"),
            x=heatmap_data.columns,
            y=heatmap_data.index,
            title="Average Stress Level by Hour and Device",
            template="plotly_white",
        )
        fig.update_layout(
            title_font_size=16,
            font=dict(
                family="Arial",
                size=12,
            ),
        )
        return fig
    except Exception as e:
        print(f"Error updating stress level heatmap: {e}")
        return {}

# Callback for Temperature vs. Heart Rate Over Time
@app.callback(
    Output("temp-hr-graph", "figure"),
    [Input("temp-hr-device-dropdown", "value")]
)
def update_temp_hr_graph(device_id):
    if not device_id:
        return {}
    try:
        # Fetch heart rate data
        response_hr = requests.get(
            f"http://127.0.0.1:5000/health_metrics?device_id={device_id}&metric_type=heart_rate"
        )
        data_hr = response_hr.json()
        df_hr = pd.DataFrame(data_hr)
        df_hr["timestamp"] = pd.to_datetime(df_hr["timestamp"])
        df_hr["heart_rate"] = df_hr["value"]
        df_hr = df_hr[["timestamp", "heart_rate"]]

        # Fetch temperature data
        response_temp = requests.get(
            f"http://127.0.0.1:5000/environmental_data?device_id={device_id}&data_type=temperature"
        )
        data_temp = response_temp.json()
        df_temp = pd.DataFrame(data_temp)
        df_temp["timestamp"] = pd.to_datetime(df_temp["timestamp"])
        df_temp["temperature"] = df_temp["value"].str.replace('°C', '').astype(float)
        df_temp = df_temp[["timestamp", "temperature"]]

        # Merge data
        df = pd.merge(df_hr, df_temp, on="timestamp", how="inner")

        # Create dual-axis line chart
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=df["timestamp"], y=df["heart_rate"], name="Heart Rate (bpm)", mode='lines'),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=df["timestamp"], y=df["temperature"], name="Temperature (°C)", mode='lines'),
            secondary_y=True,
        )

        fig.update_layout(
            title=f"Heart Rate and Temperature Over Time for Device: {device_id}",
            xaxis_title="Time",
            hovermode="x unified",
            template="plotly_white",
            title_font_size=16,
            font=dict(
                family="Arial",
                size=12,
            ),
        )
        fig.update_xaxes(tickformat="%H:%M:%S")
        fig.update_yaxes(title_text="Heart Rate (bpm)", secondary_y=False)
        fig.update_yaxes(title_text="Temperature (°C)", secondary_y=True)
        return fig
    except Exception as e:
        print(f"Error updating temperature vs. heart rate graph: {e}")
        return {}

# Callback for Map of Device Locations
@app.callback(
    Output("device-location-map", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_device_location_map(n):
    try:
        # Fetch location data
        response = requests.get("http://127.0.0.1:5000/environmental_data?data_type=location")
        data = response.json()
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp").drop_duplicates(subset="device_id", keep="last")

        # Extract latitude and longitude
        df["latitude"] = df["value"].str.split(", ").str[0].astype(float)
        df["longitude"] = df["value"].str.split(", ").str[1].astype(float)

        # Create map
        fig = px.scatter_mapbox(
            df,
            lat="latitude",
            lon="longitude",
            hover_name="device_id",
            hover_data=["town", "state"],
            zoom=3,
            height=600,
            title="Current Locations of Devices",
        )
        fig.update_layout(
            mapbox_style="open-street-map",
            title_font_size=16,
            font=dict(
                family="Arial",
                size=12,
            ),
        )
        return fig
    except Exception as e:
        print(f"Error updating device location map: {e}")
        return {}

# Callback for Heart Rate Distribution Histogram
@app.callback(
    Output("hr-histogram", "figure"),
    [Input("hr-histogram-device-dropdown", "value")]
)
def update_hr_histogram(device_id):
    try:
        if device_id:
            url = f"http://127.0.0.1:5000/health_metrics?metric_type=heart_rate&device_id={device_id}"
        else:
            url = "http://127.0.0.1:5000/health_metrics?metric_type=heart_rate"
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data)
        df["value"] = df["value"].astype(float)

        # Create histogram
        fig = px.histogram(
            df,
            x="value",
            nbins=20,
            title=f"Heart Rate Distribution {'for ' + device_id if device_id else 'for All Devices'}",
            labels={"value": "Heart Rate (bpm)"},
            template="plotly_white",
        )
        fig.update_layout(
            title_font_size=16,
            xaxis_title="Heart Rate (bpm)",
            yaxis_title="Count",
            font=dict(
                family="Arial",
                size=12,
            ),
        )
        return fig
    except Exception as e:
        print(f"Error updating heart rate histogram: {e}")
        return {}

# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True, host="127.0.0.1", port=8050)
