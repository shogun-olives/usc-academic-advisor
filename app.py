import pandas as pd
from module import LangChainModel
import streamlit as st
from module.api.api_requests import fetch_all_sections


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
        unsafe_allow_html=True,
    )

    if "sections" not in st.session_state:
        st.session_state["sections"] = pd.DataFrame(columns=[
            "id", "code", "dept", "term", "title", "instructor", "location",
            "start_time", "end_time", "day", "spaces_left",
            "number_registered", "spaces_available", "units"
        ])
    # give title to the page
    st.title("USC Course Chatbot")
    st.subheader("Ask me anything about USC courses!")

    if st.button("Fetch Latest Sections"):
        with st.spinner("Fetching all departments..."):
            st.session_state["sections"] = fetch_all_sections()
            st.success("Fetched latest sections!")

    # initialize session variables at the start once
    if "model" not in st.session_state:
        st.session_state["model"] = LangChainModel()

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "debug_logs" not in st.session_state:
        st.session_state["debug_logs"] = []

    # update the interface with the previous messages
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # create the chat interface
    if prompt := st.chat_input("Enter your query"):
        st.session_state["messages"].append(
            {"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # get response from the model
        with st.spinner("Generating Response...", show_time=True):
            response = st.session_state["model"](prompt)

        with st.chat_message("assistant"):
            st.markdown(response)

        # update the interface with the response
        st.session_state["messages"].append(
            {"role": "assistant", "content": response})

        if st.session_state["model"].fig_created:
            st.sidebar.plotly_chart(
                st.session_state["model"].fig,
                use_container_width=True,
                config={"displayModeBar": False},
            )


if __name__ == "__main__":
    main()
