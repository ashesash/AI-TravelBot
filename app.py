import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

with st.sidebar:
    st.title('🤖💬🛩️ AI TravelBot')
    if 'OPENAI_API_KEY' in st.secrets:
        st.success('API key already provided!', icon='✅')
        openai.api_key = st.secrets['OPENAI_API_KEY']
    else:
        openai.api_key = st.text_input('Enter OpenAI API token:', type='password')
        if not (openai.api_key.startswith('sk-') and len(openai.api_key)==51):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"role": "system", "content": "You are a helpful travel planning assistant. Please focus only on travel-related questions, such as the destination, budget, trip length, and preferred activities."}
    ]

if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Where would you like to go?"}
    ]

if "travel_info" not in st.session_state:
    st.session_state.travel_info = {
        "destination": None,
        "budget": None,
        "trip_length": None,
        "activities": None
    }

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Write your message here"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Store the user's response into the travel info based on the current missing info
    if st.session_state.travel_info["destination"] is None:
        st.session_state.travel_info["destination"] = prompt
        next_question = "Great! Now, what's your budget for the trip?"
    elif st.session_state.travel_info["budget"] is None:
        st.session_state.travel_info["budget"] = prompt
        next_question = "How long are you planning to stay?"
    elif st.session_state.travel_info["trip_length"] is None:
        st.session_state.travel_info["trip_length"] = prompt
        next_question = "What activities or experiences would you like to prioritize?"
    elif st.session_state.travel_info["activities"] is None:
        st.session_state.travel_info["activities"] = prompt
        next_question = "Do you have any preferences for accommodation?"

    # If all information is collected, set up to generate the itinerary
    if all(st.session_state.travel_info.values()):
        next_question = "I have all the details. Now let me generate your itinerary!"

    st.session_state.messages.append({"role": "assistant", "content": next_question})

    # Display the next follow-up question
    with st.chat_message("assistant"):
        st.markdown(next_question)

    if all(st.session_state.travel_info.values()):
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
        response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.markdown(response)





