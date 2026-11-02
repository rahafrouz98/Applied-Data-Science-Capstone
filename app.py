import pandas as pd
import dash
from dash import html, dcc, Input, Output
import plotly.express as px

# Load launch data
DATA_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
)
spacex_df = pd.read_csv(DATA_URL)

min_payload = float(spacex_df["Payload Mass (kg)"].min())
max_payload = float(spacex_df["Payload Mass (kg)"].max())
launch_sites = sorted(spacex_df["Launch Site"].dropna().unique())

# Create the application
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    style={
        "maxWidth": "1100px",
        "margin": "0 auto",
        "padding": "24px",
        "fontFamily": "Arial, sans-serif",
    },
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36"},
        ),

        html.Label(
            "Select a launch site:",
            htmlFor="site-dropdown",
            style={"fontWeight": "bold"},
        ),
        dcc.Dropdown(
            id="site-dropdown",
            options=[
                {"label": "All Launch Sites", "value": "All"}
            ] + [
                {"label": site, "value": site}
                for site in launch_sites
            ],
            value="All",
            clearable=False,
            searchable=True,
        ),

        dcc.Graph(id="success-pie-chart"),

        html.P(
            "Select payload mass range (kg):",
            style={"fontWeight": "bold"},
        ),
        html.Div(
    style={
        "padding": "15px 25px 40px",
        "overflow": "visible",
    },
    children=[
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=20000,
            step=1000,
            marks={
                value: f"{value:,}"
                for value in range(0, 20001, 5000)
            },
            value=[min_payload, max_payload],
            tooltip={
                "placement": "bottom",
                "always_visible": True,
            },
            updatemode="drag",
            allowCross=False,
        ),
    ],
),

        dcc.Graph(id="success-payload-scatter-chart"),
    ],
)


# Update the pie chart when the launch site changes
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value"),
)
def get_pie_chart(entered_site):
    if entered_site == "All":
        successful_launches = (
            spacex_df[spacex_df["class"] == 1]
            .groupby("Launch Site")
            .size()
            .reset_index(name="Successful launches")
        )

        fig = px.pie(
            successful_launches,
            values="Successful launches",
            names="Launch Site",
            title="Share of Successful Launches by Launch Site",
            labels={"Launch Site": "Launch site"},
        )
        fig.update_traces(
            textinfo="percent+label",
            hovertemplate=(
                "Launch site: %{label}<br>"
                "Successful launches: %{value}<br>"
                "Share: %{percent}<extra></extra>"
            ),
        )

    else:
        site_data = spacex_df[
            spacex_df["Launch Site"] == entered_site
        ]

        outcomes = (
            site_data["class"]
            .value_counts()
            .reindex([0, 1], fill_value=0)
        )

        outcome_counts = pd.DataFrame({
            "Launch outcome": ["Failure", "Success"],
            "Number of launches": outcomes.to_numpy(),
        })

        fig = px.pie(
            outcome_counts,
            values="Number of launches",
            names="Launch outcome",
            color="Launch outcome",
            color_discrete_map={
                "Failure": "#EF553B",
                "Success": "#00A878",
            },
            title=f"Launch Outcomes — {entered_site}",
        )
        fig.update_traces(
            textinfo="label+percent",
            hovertemplate=(
                "Outcome: %{label}<br>"
                "Launches: %{value}<br>"
                "Share: %{percent}<extra></extra>"
            ),
        )

    fig.update_layout(title_x=0.5)
    return fig


# Update the scatter chart using BOTH selected filters
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    Input("site-dropdown", "value"),
    Input("payload-slider", "value"),
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range

    filtered_df = spacex_df[
        spacex_df["Payload Mass (kg)"].between(low, high)
    ].copy()

    if entered_site != "All":
        filtered_df = filtered_df[
            filtered_df["Launch Site"] == entered_site
        ].copy()

    filtered_df["Launch outcome"] = filtered_df["class"].map({
        0: "Failure",
        1: "Success",
    })

    site_label = (
        "All Launch Sites" if entered_site == "All" else entered_site
    )

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        labels={
            "Payload Mass (kg)": "Payload mass (kg)",
            "class": "Launch outcome",
            "Booster Version Category": "Booster version",
        },
        custom_data=["Launch Site", "Launch outcome"],
        title=(
            f"Launch Outcome by Payload Mass — {site_label}"
            f"<br><sup>Selected payload: {low:,.0f}–{high:,.0f} kg</sup>"
        ),
    )

    fig.update_traces(
        marker={"size": 11, "opacity": 0.8},
        hovertemplate=(
            "Launch site: %{customdata[0]}<br>"
            "Payload mass: %{x:,.0f} kg<br>"
            "Outcome: %{customdata[1]}"
            "<extra>%{fullData.name}</extra>"
        ),
    )

    fig.update_yaxes(
        tickvals=[0, 1],
        ticktext=["Failure", "Success"],
        range=[-0.15, 1.15],
    )
    fig.update_xaxes(
        tickformat=",.0f",
        range=[low, high],
    )
    fig.update_layout(
        title_x=0.5,
        legend_title_text="Booster version",
        margin={"t": 100},
    )

    if filtered_df.empty:
        fig.add_annotation(
            text="No launches match the selected site and payload range.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )

    return fig


if __name__ == "__main__":
    app.run(debug=True)