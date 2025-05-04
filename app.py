from module import LangChainModel
import streamlit as st

import os
from dotenv import load_dotenv

load_dotenv()

def main() -> None:
    # give title to the page
    st.title("USC Course Chatbot")
    st.subheader("Ask me anything about USC courses!")

    # initialize session variables at the start once
    if "model" not in st.session_state:
        st.session_state["model"] = LangChainModel()

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # TODO Make a display in the sidebar to show the planned schedule
    # Sidebar
    st.sidebar.title("Schedule")

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
            st.markdown(response)

        # update the interface with the response
        st.session_state["messages"].append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
