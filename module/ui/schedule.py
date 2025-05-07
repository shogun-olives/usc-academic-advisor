from ..util import decimal_to_time
import plotly.graph_objects as go


def create_schedule(
    events: list[dict[str : str | int]] = None,
    start_time: int = 5,
    end_time: int = 22,
) -> go.Figure:
    """
    Create a weekly schedule with events.

    Args:
        events (list[dict[str : str | int]]): A list of events to display on the schedule. The events should be in the format:
            -   day (str): The day of the week (e.g., "Mon", "Tue", etc.)
            -   start_hour (int): The starting hour of the event (24-hour format).
            -   end_hour (int): The ending hour of the event (24-hour format).
            -   label (str): The label for the event.
        start_time (int): The starting hour of the schedule (default is 5 for 5 am).
        end_time (int): The ending hour of the schedule (default is 22 for 10 pm).

    Returns:
        (output) go.Figure: A Plotly figure object representing the weekly schedule.

    Examples:
        ```
        # Create a weekly schedule with events
        events = [
            {"day": "Mon", "start_hour": 9, "end_hour": 11.5, "label": "Meeting"},
            {"day": "Wed", "start_hour": 14.33333, "end_hour": 16, "label": "Workshop"},
        ]
        schedule = create_schedule(events)
        ```
    """
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    hours = list(range(start_time, end_time + 1))

    fig = go.Figure()

    for h in hours:
        fig.add_shape(
            type="line",
            x0=0,
            x1=len(days),
            y0=h,
            y1=h,
            line=dict(color="#444", width=1),
        )

    for i in range(len(days) + 1):
        fig.add_shape(
            type="line",
            x0=i,
            x1=i,
            y0=hours[0],
            y1=hours[-1],
            line=dict(color="#444", width=1),
        )

    for i, day in enumerate(days):
        for j, hour in enumerate(hours):
            fig.add_trace(
                go.Scatter(
                    x=[i + 0.5],
                    y=[hour + 0.5],
                    text=[f"{day}, {hour}:00"],
                    mode="markers",
                    marker=dict(size=20, opacity=0),
                    hoverinfo="text",
                    showlegend=False,
                )
            )

    fig.update_layout(
        title="Weekly Schedule",
        xaxis=dict(
            tickmode="array",
            tickvals=[i + 0.5 for i in range(len(days))],
            ticktext=days,
            range=[0, len(days)],
            showgrid=False,
            color="#fff",
            side="top",
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=[h + 0.5 for h in hours],
            ticktext=[f"{h}:00 {'AM' if h < 12 else 'PM'}" for h in hours],
            range=[hours[-1], hours[0]],
            showgrid=False,
            color="#fff",
        ),
        plot_bgcolor="#2c2c2c",
        paper_bgcolor="#2c2c2c",
        font=dict(color="#ffffff"),
        dragmode=False,
        height=900,
        margin=dict(l=20, r=20, t=60, b=20),
    )

    if events is None:
        return fig

    day_to_index = {day: i for i, day in enumerate(days)}

    for event in events:
        for day in event["day"]:
            x0 = day_to_index[day]
            x1 = x0 + 1
            y0 = event["start_hour"]
            y1 = event["end_hour"]
            mid_x = x0 + 0.5
            mid_y = (y0 + y1) / 2

            # 1. Add visual block
            fig.add_shape(
                type="rect",
                x0=x0,
                x1=x1,
                y0=y0,
                y1=y1,
                fillcolor="rgba(0, 200, 200, 0.4)",
                line=dict(width=0),
                layer="above",
            )

            # 2. Add label annotation
            fig.add_annotation(
                x=mid_x,
                y=mid_y,
                text=event["label"],
                showarrow=False,
                font=dict(color="white", size=12),
                align="center",
            )

            # 3. Add invisible hover layer
            fig.add_trace(
                go.Scatter(
                    x=[x0, x0, x1, x1, x0],
                    y=[y0, y1, y1, y0, y0],
                    mode="lines",
                    fill="toself",
                    fillcolor="rgba(0,0,0,0)",  # invisible
                    line=dict(width=0),
                    hoverinfo="text",
                    text=event["hover"],
                    showlegend=False,
                )
            )

    return fig
