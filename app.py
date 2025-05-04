from module import LangChainModel
import streamlit as st


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

    # update the interface with the previous messages
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # TODO Fix issue with prior chats becoming None once a new response is generated
    # create the chat interface
    if prompt := st.chat_input("Enter your query"):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # get response from the model
        response = st.session_state["model"](prompt)
        with st.chat_message("assistant"):
            st.markdown(response.replace("\n", "  \n"))

        # update the interface with the response
        st.session_state["messages"].append({"role": "assistant", "content": response})

        if st.session_state["model"].fig_created:
            st.sidebar.plotly_chart(
                st.session_state["model"].fig,
                use_container_width=True,
                config={"displayModeBar": False},
            )


if __name__ == "__main__":
    main()
