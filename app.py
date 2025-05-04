from module import LangChainModel
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

import os
from dotenv import load_dotenv

load_dotenv()


def main() -> None:

    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                flex: 0 0 1000px !important;
                max-width: 1000px !important;
            }

            section[data-testid="stSidebar"] > div:first-child {
                width: 1000px !important;
            }

            div[data-testid="stAppViewContainer"] > div:nth-child(2) {
                margin-left: 1000px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # give title to the page
    st.title("USC Course Chatbot")
    st.subheader("Ask me anything about USC courses!")

    # initialize session variables at the start once
    if "model" not in st.session_state:
        st.session_state["model"] = LangChainModel()

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "debug_logs" not in st.session_state:
        st.session_state["debug_logs"] = []

    # TODO Make a display in the sidebar to show the planned schedule

    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    hours = list(range(5, 23))  # 5AM to 10PM

    fig = go.Figure()

    for h in hours:
        fig.add_shape(
            type="line",
            x0=0, x1=len(days),
            y0=h, y1=h,
            line=dict(color="#444", width=1)
        )

    for i in range(len(days) + 1):
        fig.add_shape(
            type="line",
            x0=i, x1=i,
            y0=hours[0], y1=hours[-1],
            line=dict(color="#444", width=1)
        )

    for i, day in enumerate(days):
        for j, hour in enumerate(hours):
            fig.add_trace(go.Scatter(
                x=[i + 0.5],
                y=[hour + 0.5],
                text=[f"{day}, {hour}:00"],
                mode="markers",
                marker=dict(size=20, opacity=0),
                hoverinfo="text",
                showlegend=False
            ))

    fig.update_layout(
        title="Weekly Schedule (Click on a Cell to Fill)",
        xaxis=dict(
            tickmode="array",
            tickvals=[i + 0.5 for i in range(len(days))],
            ticktext=days,
            range=[0, len(days)],
            showgrid=False,
            color="#fff",
            side="top"
        ),
        yaxis=dict(
            tickmode="array",
            tickvals=[h + 0.5 for h in hours],
            ticktext=[f"{h}:00 {'AM' if h < 12 else 'PM'}" for h in hours],
            range=[hours[-1], hours[0]],
            showgrid=False,
            color="#fff"
        ),
        plot_bgcolor="#2c2c2c",
        paper_bgcolor="#2c2c2c",
        font=dict(color="#ffffff"),
        dragmode=False,
        height=900,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.sidebar.plotly_chart(fig, use_container_width=True, config={
                            "displayModeBar": False})

    # update the interface with the previous messages
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # TODO Fix issue with prior chats becoming None once a new response is generated
    # create the chat interface
    if prompt := st.chat_input("Enter your query"):
        st.session_state["messages"].append(
            {"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # get response from the model
        response = st.session_state["model"](prompt)
        with st.chat_message("assistant"):
            st.markdown(response)

        # update the interface with the response
        st.session_state["messages"].append(
            {"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
