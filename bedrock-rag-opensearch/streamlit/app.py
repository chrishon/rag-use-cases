import streamlit as st
import requests
import json
import os

endpoint = os.environ.get("LLM_ENDPOINT")
content_window = ""

# Header/Title of streamlit app
st.title(f""":rainbow[Knowledge base RAG search]:flag-ch:""")


# configuring values for session state
if "messages" not in st.session_state:
    st.session_state.messages = []
# writing the message that is stored in session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
# adding some special effects from the UI perspective
st.balloons()
# evaluating st.chat_input and determining if a question has been input
if question := st.chat_input("Ask about your data stored in your knowledge base"):
    # with the user icon, write the question to the front end
    with st.chat_message("user"):
        st.markdown(question)
        if "session_state" not in st.session_state:
            st.session_state.session_state = ""
        st.session_state.session_state += f"Question: {question} \n"
        print(f"Session State: {st.session_state.session_state}")
    # append the question and the role (user) as a message to the session state
    st.session_state.messages.append({"role": "user", "content": question})
    # respond as the assistant with the answer
    with st.chat_message("assistant"):
        # making sure there are no messages present when generating the answer
        message_placeholder = st.empty()
        # putting a spinning icon to show that the query is in progress
        with st.status(
            "Determining the best possible answer!", expanded=False
        ) as status:
            # passing the question into the OpenSearch search function, which later invokes the llm
            answer = requests.post(
                url=endpoint,
                json={
                    "query": question,
                    "user_context": st.session_state.session_state,
                    "person": "Blake",
                },
            )

            st.session_state.session_state += f"Answer: {answer.content} \n"
            print(f"session_state: {st.session_state.session_state}")
            # writing the answer to the front end
            message_placeholder.markdown(answer.content.decode("utf-8"))
            # showing a completion message to the front end
            status.update(
                label="Question Answered...", state="complete", expanded=False
            )
    # appending the results to the session state
    st.session_state.messages.append({"role": "assistant", "content": answer})
