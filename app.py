import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import json
import datetime

with st.sidebar:
    st.title('🤖💬🛩️ AI TravelBot')
    if 'OPENAI_API_KEY' in st.secrets:
        openai.api_key = st.secrets['OPENAI_API_KEY']
        st.success('API key already provided!', icon='✅')
    else:
        st.markdown("🔐 We don't save your API keys or any data you enter")
        openai.api_key = st.text_input('Enter OpenAI API token:', type='password')
        if not openai.api_key.startswith('sk-'):
            st.warning('Please enter your credentials!', icon='⚠️')
            st.stop()
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {"role": "system", "content": "You are a helpful travel planning assistant. Please focus only on travel-related questions, such as the destination, budget, trip length, and preferred activities. At the end of your recommendation also add a dataframe for the itinerary you plan with the following columns: Date, location of the destination, nearest city, description, time to be spent, category, latitude and longitude"}
    ]

        # travel_plan = [
        #     {"date": "2024-10-10", "location": "Louvre Museum", "nearest_city": "Paris", "description": "Explore world-famous artworks.", "hours": "09:00-12:00", "category": "Culture", "latitude": 48.8606, "longitude": 2.3376},
        #     {"date": "2024-10-10", "location": "Eiffel Tower", "nearest_city": "Paris", "description": "Visit the iconic landmark.", "hours": "14:00-16:00", "category": "Adventure", "latitude": 48.8584, "longitude": 2.2945}
        # ]

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
        next_question = "How long are you planning to stay? Could you give me start and end dates?"
    elif st.session_state.travel_info["trip_length"] is None:
        st.session_state.travel_info["trip_length"] = prompt
        next_question = "What activities or experiences would you like to prioritize?"
    elif st.session_state.travel_info["activities"] is None:
        st.session_state.travel_info["activities"] = prompt
        next_question = "Do you have any preferences for accommodation?"

    if all(st.session_state.travel_info.values()):
        next_question = "I have all the details. Now let me generate your itinerary!"

    st.session_state.messages.append({"role": "assistant", "content": next_question})
    with st.chat_message("assistant"):
        st.markdown(next_question)

    if all(st.session_state.travel_info.values()):
        with st.chat_message("assistant"):
            stream = openai.chat.completions.create(
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

        try:
            travel_plan = json.loads(response)
            itinerary_df = pd.DataFrame(travel_plan)

            csv_file = f"travel_itinerary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            itinerary_df.to_csv(csv_file, index=False)
            st.success(f"Travel itinerary saved as {csv_file}!")
            st.dataframe(itinerary_df)

            # Load the updated itinerary events CSV file with coordinates
            itinerary_df = pd.read_csv("itinerary_events_with_coordinates.csv")

            # Streamlit app
            st.title('Travel Itinerary Dashboard')

            # Display the itinerary events
            st.header('Itinerary Events 🐢')
            st.dataframe(itinerary_df)

        except json.JSONDecodeError as e:
            st.error(f"Error decoding JSON: {e}")
        except Exception as e:
            st.error(f"Error saving CSV: {e}")
